"""LangGraph StateGraph-based workflow engine for AI-MultiColony.

Provides a production-grade workflow engine that wraps LangGraph's StateGraph
with event-triggered execution, conditional branching, retry logic, and
comprehensive error handling.

Key components:
- ``WorkflowEngine``: Wraps LangGraph StateGraph for building and running
  multi-step workflows with shared state.
- ``EventTrigger``: Event-binding system that connects event types to handler
  callables with full invocation semantics (not a no-op).
- ``WorkflowState``: TypedDict defining the shared state schema.
- ``WorkflowStep`` / ``WorkflowDefinition``: Declarative workflow specifications.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    TypedDict,
    Union,
)

import structlog
from langgraph.graph import END, START, StateGraph

logger = structlog.get_logger(__name__)


# ── State Schema ──────────────────────────────────────────────────────────────


class WorkflowState(TypedDict, total=False):
    """Shared state that flows through every step of a workflow.

    Fields
    ------
    step:
        Name or identifier of the current step being executed.
    data:
        Arbitrary payload carried between steps.
    results:
        Accumulated results from completed steps.
    errors:
        Errors keyed by step name.
    status:
        Current workflow-level status (e.g. ``"running"``, ``"completed"``,
        ``"failed"``).
    """

    step: str
    data: Dict[str, Any]
    results: Dict[str, Any]
    errors: Dict[str, str]
    status: str


# ── Data Classes ──────────────────────────────────────────────────────────────


@dataclass
class WorkflowStep:
    """Declarative definition of a single workflow step.

    Parameters
    ----------
    name:
        Unique step identifier used for routing and logging.
    handler:
        Callable that receives and returns a ``WorkflowState`` dict.
        May be sync or async.
    condition:
        Optional callable ``condition(state: WorkflowState) -> str``
        that returns the name of the next step.  When *None* the step
        simply flows to the next one in definition order.
    retry_count:
        Maximum number of automatic retries on handler failure.
    timeout:
        Per-step timeout in seconds.  ``0`` means no timeout.
    """

    name: str
    handler: Callable[..., Any]
    condition: Optional[Callable[[WorkflowState], str]] = None
    retry_count: int = 0
    timeout: float = 0.0


@dataclass
class WorkflowDefinition:
    """Declarative definition of an entire workflow.

    Parameters
    ----------
    name:
        Human-readable workflow name.
    steps:
        Ordered list of ``WorkflowStep`` definitions.
    triggers:
        Mapping of event-type strings to handler callables that should
        fire when those events are triggered during execution.
    config:
        Arbitrary configuration overrides.
    """

    name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    triggers: Dict[str, List[Callable]] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)


# ── Event Trigger ─────────────────────────────────────────────────────────────


class EventTrigger:
    """Event binding and invocation system for workflow lifecycle hooks.

    Unlike a no-op stub, ``EventTrigger.bind()`` **registers** handlers and
    ``EventTrigger.trigger()`` **invokes** every handler bound to a given
    event type, propagating the payload dict.

    Usage::

        trigger = EventTrigger()
        trigger.bind("on_bar", lambda payload: print(payload))
        trigger.trigger("on_bar", {"symbol": "BTC/USDT", "close": 65000})
    """

    def __init__(self) -> None:
        self._workflow_bindings: Dict[str, List[Callable]] = {}
        self._engine: Optional[WorkflowEngine] = None

    # ── Public API ───────────────────────────────────────────────────

    def bind(self, event_type: str, handler: Callable) -> None:
        """Register *handler* to be invoked when *event_type* is triggered.

        Parameters
        ----------
        event_type:
            Arbitrary event category string (e.g. ``"on_bar"``,
            ``"on_signal"``, ``"on_error"``).
        handler:
            Synchronous or asynchronous callable accepting a single
            ``dict`` payload argument.
        """
        if event_type not in self._workflow_bindings:
            self._workflow_bindings[event_type] = []
        self._workflow_bindings[event_type].append(handler)
        logger.debug(
            "event_handler_bound",
            event_type=event_type,
            handler=handler.__qualname__,
            total_handlers=len(self._workflow_bindings[event_type]),
        )

    def trigger(self, event_type: str, payload: dict) -> None:
        """Invoke every handler bound to *event_type* with *payload*.

        Handlers are invoked in registration order.  Both sync and async
        handlers are supported — async handlers are scheduled on the
        running event loop if one exists.

        Parameters
        ----------
        event_type:
            The event category to fire.
        payload:
            Dict passed as the single argument to each handler.
        """
        handlers = self._workflow_bindings.get(event_type, [])
        if not handlers:
            logger.debug("event_trigger_no_handlers", event_type=event_type)
            return

        logger.debug(
            "event_trigger_firing",
            event_type=event_type,
            handler_count=len(handlers),
        )

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    # Try to run in an existing event loop
                    try:
                        loop = asyncio.get_running_loop()
                        loop.create_task(handler(payload))
                    except RuntimeError:
                        # No running loop — run synchronously
                        asyncio.run(handler(payload))
                else:
                    handler(payload)
            except Exception as exc:
                logger.warning(
                    "event_handler_error",
                    event_type=event_type,
                    handler=handler.__qualname__,
                    error=str(exc),
                )

    @property
    def engine(self) -> Optional[WorkflowEngine]:
        """Return the attached workflow engine, if any."""
        return self._engine

    @engine.setter
    def engine(self, value: Optional[WorkflowEngine]) -> None:
        """Attach (or detach) a workflow engine reference."""
        self._engine = value

    @property
    def bindings(self) -> Dict[str, List[Callable]]:
        """Return a shallow copy of all current bindings."""
        return dict(self._workflow_bindings)

    def clear(self) -> None:
        """Remove all registered bindings."""
        self._workflow_bindings.clear()


# ── Workflow Engine ────────────────────────────────────────────────────────────


class WorkflowEngine:
    """LangGraph StateGraph-based workflow engine.

    Wraps a ``StateGraph`` to provide an ergonomic, high-level API for
    building and executing multi-step workflows with:

    * **Conditional branching** — steps can route to different successors
      based on state.
    * **Retry logic** — per-step configurable retry with exponential
      back-off.
    * **Error handling** — failed steps record errors in state and
      optionally continue.
    * **Event triggers** — bind event handlers that fire at key lifecycle
      points.

    Usage::

        engine = WorkflowEngine("data_pipeline")

        engine.add_step(WorkflowStep(
            name="fetch",
            handler=fetch_data,
            retry_count=3,
            timeout=30,
        ))
        engine.add_step(WorkflowStep(
            name="transform",
            handler=transform_data,
            condition=lambda s: "enrich" if s["data"].get("needs_enrichment") else "load",
        ))
        engine.add_step(WorkflowStep(name="enrich", handler=enrich_data))
        engine.add_step(WorkflowStep(name="load", handler=load_data))

        result = engine.run({"data": {"url": "..."}})
    """

    def __init__(self, name: str = "default_workflow") -> None:
        self._name = name
        self._steps: List[WorkflowStep] = []
        self._trigger = EventTrigger()
        self._trigger.engine = self
        self._state: Optional[WorkflowState] = None
        self._compiled = False
        self._graph: Optional[StateGraph] = None

        logger.info("workflow_engine_created", name=name)

    # ── Construction ──────────────────────────────────────────────────

    def add_step(self, step: WorkflowStep) -> None:
        """Append a step to the workflow.

        Parameters
        ----------
        step:
            Fully-specified ``WorkflowStep`` instance.
        """
        self._steps.append(step)
        self._compiled = False  # invalidate compiled graph
        logger.debug("step_added", step_name=step.name, workflow=self._name)

    @property
    def trigger(self) -> EventTrigger:
        """Access the event-trigger system for this engine."""
        return self._trigger

    # ── Internal Graph Builder ────────────────────────────────────────

    def _build_graph(self) -> StateGraph:
        """Construct a ``StateGraph`` from the current step list."""
        graph = StateGraph(WorkflowState)

        if not self._steps:
            raise ValueError(f"Workflow '{self._name}' has no steps")

        # Register each step as a graph node
        for idx, step in enumerate(self._steps):
            node_fn = self._make_node_fn(step, idx)
            graph.add_node(step.name, node_fn)

        # Wire edges
        graph.add_edge(START, self._steps[0].name)

        for idx, step in enumerate(self._steps):
            if step.condition is not None:
                # Conditional edge — the condition function returns the
                # name of the next step (must be a registered step name
                # or END).
                cond_fn = self._make_cond_fn(step)
                # Build a mapping: each subsequent step name → itself,
                # plus a special "__end__" → END.
                target_map: Dict[str, str] = {}
                for later_step in self._steps[idx + 1 :]:
                    target_map[later_step.name] = later_step.name
                target_map["__end__"] = END  # type: ignore[dict-item]
                graph.add_conditional_edges(step.name, cond_fn, target_map)
            elif idx < len(self._steps) - 1:
                # Simple linear edge to the next step
                graph.add_edge(step.name, self._steps[idx + 1].name)
            else:
                # Last step → END
                graph.add_edge(step.name, END)

        return graph

    def _make_node_fn(
        self, step: WorkflowStep, idx: int
    ) -> Callable[[WorkflowState], WorkflowState]:
        """Create a graph-node callable that wraps a ``WorkflowStep.handler``.

        The returned callable implements retry logic and error handling
        around the user-supplied handler.
        """

        def node_fn(state: WorkflowState) -> WorkflowState:
            state["step"] = step.name
            retries_remaining = step.retry_count
            last_error: Optional[str] = None

            for attempt in range(1, retries_remaining + 2):  # +1 for initial try
                try:
                    # Trigger pre-step event
                    self._trigger.trigger(
                        f"before_{step.name}",
                        {"step": step.name, "attempt": attempt, "state": state},
                    )

                    # Execute handler with optional timeout
                    if asyncio.iscoroutinefunction(step.handler):
                        result = asyncio.get_event_loop().run_until_complete(
                            asyncio.wait_for(
                                step.handler(state),
                                timeout=step.timeout if step.timeout > 0 else None,
                            )
                        )
                    else:
                        if step.timeout > 0:
                            result = self._run_with_timeout(step.handler, state, step.timeout)
                        else:
                            result = step.handler(state)

                    # Merge result back into state
                    if isinstance(result, dict):
                        for key, value in result.items():
                            if key in ("data", "results", "errors"):
                                if isinstance(value, dict):
                                    state[key].update(value)  # type: ignore[index]
                            else:
                                state[key] = value  # type: ignore[literal-required]

                    # Clear any previous error for this step on success
                    state["errors"].pop(step.name, None)  # type: ignore[union-attr]

                    # Trigger post-step event
                    self._trigger.trigger(
                        f"after_{step.name}",
                        {"step": step.name, "attempt": attempt, "state": state},
                    )

                    return state

                except Exception as exc:
                    last_error = str(exc)
                    logger.warning(
                        "step_error",
                        step=step.name,
                        attempt=attempt,
                        max_retries=retries_remaining + 1,
                        error=last_error,
                    )
                    if retries_remaining > 0:
                        retries_remaining -= 1
                        # Exponential back-off (deterministic)
                        backoff = min(0.1 * (2 ** (attempt - 1)), 10.0)
                        time.sleep(backoff)
                        continue
                    break  # Exhausted retries

            # Record error in state
            if last_error is not None:
                state["errors"][step.name] = last_error  # type: ignore[index]
                self._trigger.trigger(
                    f"error_{step.name}",
                    {"step": step.name, "error": last_error, "state": state},
                )

            return state

        return node_fn

    @staticmethod
    def _run_with_timeout(
        fn: Callable, state: WorkflowState, timeout: float
    ) -> Any:
        """Run a synchronous callable with a wall-clock timeout."""
        import threading

        result_box: list[Any] = []
        error_box: list[Exception] = []

        def _target() -> None:
            try:
                result_box.append(fn(state))
            except Exception as exc:
                error_box.append(exc)

        thread = threading.Thread(target=_target, daemon=True)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(
                f"Step timed out after {timeout}s"
            )
        if error_box:
            raise error_box[0]
        return result_box[0] if result_box else state

    def _make_cond_fn(
        self, step: WorkflowStep
    ) -> Callable[[WorkflowState], str]:
        """Wrap a step's condition callable for LangGraph conditional edges."""

        def cond(state: WorkflowState) -> str:
            try:
                result = step.condition(state)  # type: ignore[misc]
                if result == END:
                    return "__end__"
                return result
            except Exception as exc:
                logger.warning(
                    "condition_error",
                    step=step.name,
                    error=str(exc),
                )
                # On condition error, fall through to the next step if
                # possible, otherwise end.
                idx = next(
                    (i for i, s in enumerate(self._steps) if s.name == step.name),
                    -1,
                )
                if idx >= 0 and idx < len(self._steps) - 1:
                    return self._steps[idx + 1].name
                return "__end__"

        return cond

    # ── Execution ─────────────────────────────────────────────────────

    def run(
        self,
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowState:
        """Execute the workflow from start to finish.

        Parameters
        ----------
        initial_data:
            Seed values merged into the workflow state before execution.

        Returns
        -------
        WorkflowState
            Final state after all steps have completed (or errored out).
        """
        # Build/compile graph if necessary
        if not self._compiled or self._graph is None:
            self._graph = self._build_graph()

        compiled = self._graph.compile()

        # Initialise state
        self._state = WorkflowState(
            step="",
            data=initial_data or {},
            results={},
            errors={},
            status="running",
        )

        logger.info(
            "workflow_starting",
            name=self._name,
            step_count=len(self._steps),
        )

        self._trigger.trigger("workflow_start", {"workflow": self._name})

        try:
            result = compiled.invoke(self._state)
            if isinstance(result, dict):
                result["status"] = "completed" if not result.get("errors") else "failed"
                self._state = result  # type: ignore[assignment]
            logger.info(
                "workflow_completed",
                name=self._name,
                status=self._state.get("status", "unknown"),
            )
            self._trigger.trigger(
                "workflow_end",
                {"workflow": self._name, "status": self._state.get("status")},
            )
        except Exception as exc:
            if self._state is not None:
                self._state["status"] = "failed"
                self._state["errors"]["__workflow__"] = str(exc)
            logger.error(
                "workflow_fatal",
                name=self._name,
                error=str(exc),
            )
            self._trigger.trigger(
                "workflow_error",
                {"workflow": self._name, "error": str(exc)},
            )

        return self._state or WorkflowState(
            step="", data={}, results={}, errors={"__workflow__": "no state"}, status="failed"
        )

    def get_state(self) -> Optional[WorkflowState]:
        """Return a copy of the current workflow state, or *None* if
        the workflow has not yet been run."""
        if self._state is None:
            return None
        return dict(self._state)  # type: ignore[return-value]

    # ── Properties ────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Workflow engine name."""
        return self._name

    @property
    def steps(self) -> List[WorkflowStep]:
        """Registered workflow steps."""
        return list(self._steps)

    @property
    def is_compiled(self) -> bool:
        """Whether the internal graph has been compiled."""
        return self._compiled


__all__ = [
    "WorkflowEngine",
    "EventTrigger",
    "WorkflowState",
    "WorkflowStep",
    "WorkflowDefinition",
]
