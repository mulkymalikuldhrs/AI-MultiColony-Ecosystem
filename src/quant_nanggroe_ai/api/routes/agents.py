"""Agent control routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.post("/run")
async def run_agent(symbol: str, query: str = ""):
    """Run the full agent pipeline for a symbol."""
    return {"status": "started", "symbol": symbol}


@router.get("/status")
async def get_agent_status():
    """Get current agent status."""
    return {"agents": [], "active": False}


@router.post("/kill-switch/activate")
async def activate_kill_switch(reason: str = "MANUAL"):
    """Activate the kill switch."""
    from quant_nanggroe_ai.engine.kill_switch import KillSwitch
    ks = KillSwitch()
    result = ks.activate(reason=reason)
    return result


@router.post("/kill-switch/reset")
async def reset_kill_switch(confirmation: str = ""):
    """Reset the kill switch (requires confirmation)."""
    from quant_nanggroe_ai.engine.kill_switch import KillSwitch
    ks = KillSwitch()
    result = ks.reset(confirmation=confirmation)
    return result


@router.get("/kill-switch/status")
async def kill_switch_status():
    """Get kill switch status."""
    from quant_nanggroe_ai.engine.kill_switch import KillSwitch
    ks = KillSwitch()
    return ks.status()
