"""compat_requests.py
Thin wrapper that attempts to import the real `requests` library. If it is not
available, it exposes a **very minimal** subset (get / post with JSON body)
backed by Python std-lib `urllib.request` so that the wider codebase can still
import `requests` and perform basic HTTP interactions without crashing.
This is NOT intended for production-grade HTTP usage – just enough to keep the
system bootstrapped in environments where installing `requests` is not
possible (e.g. offline CI containers).
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Dict, Optional

try:
    import requests  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    import urllib.request as _urlreq
    import urllib.error as _urlerr
    import urllib.parse as _urlparse

    class _SimpleResponse:  # pylint: disable=too-few-public-methods
        """Mimic the minimal surface needed by existing code (status_code/json)."""

        def __init__(self, data: bytes, status: int):
            self._data = data
            self.status_code = status

        def json(self) -> Dict[str, Any]:  # type: ignore[override]
            return json.loads(self._data.decode()) if self._data else {}

    class _CompatRequests:  # pylint: disable=too-few-public-methods
        """Extremely minimal subset of requests (get/post JSON)."""

        @staticmethod
        def get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None):  # noqa: D401, E501
            if params:
                query = _urlparse.urlencode(params)
                sep = '&' if '?' in url else '?'
                url = f"{url}{sep}{query}"
            req = _urlreq.Request(url, headers=headers or {})
            try:
                with _urlreq.urlopen(req, timeout=30) as resp:  # nosec B310
                    data = resp.read()
                    return _SimpleResponse(data, resp.getcode())
            except _urlerr.URLError as exc:
                return _SimpleResponse(json.dumps({"error": str(exc)}).encode(), 500)

        @staticmethod
        def post(url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None):  # noqa: E501
            data = json and json.dumps(json).encode() or None
            req = _urlreq.Request(url, data=data, headers=headers or {}, method="POST")
            try:
                with _urlreq.urlopen(req, timeout=timeout or 60) as resp:  # nosec B310
                    rdata = resp.read()
                    return _SimpleResponse(rdata, resp.getcode())
            except _urlerr.URLError as exc:
                return _SimpleResponse(json.dumps({"error": str(exc)}).encode(), 500)

    # Expose instance matching requests module structure
    requests = SimpleNamespace(get=_CompatRequests.get, post=_CompatRequests.post)  # type: ignore