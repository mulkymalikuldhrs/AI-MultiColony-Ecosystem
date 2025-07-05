"""requests stub – provides minimal get/post functions using urllib for environments without real requests package."""
from __future__ import annotations

import json
import sys
import urllib.request as _urlreq
import urllib.error as _urlerr
import urllib.parse as _urlparse
from types import SimpleNamespace
from typing import Any, Dict, Optional

class _SimpleResponse:  # noqa: D101
    def __init__(self, data: bytes, status: int):
        self._data = data
        self.status_code = status

    def json(self):  # noqa: D401
        try:
            return json.loads(self._data.decode())
        except Exception:
            return {}


def _http(method: str, url: str, *, headers: Optional[Dict[str, str]] = None, json_body: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, str]] = None, timeout: int = 30):  # noqa: E501
    if params:
        url += ("?" if "?" not in url else "&") + _urlparse.urlencode(params)
    data = json_body and json.dumps(json_body).encode() or None
    req = _urlreq.Request(url, data=data, headers=headers or {}, method=method.upper())
    try:
        with _urlreq.urlopen(req, timeout=timeout) as resp:  # nosec B310
            return _SimpleResponse(resp.read(), resp.getcode())
    except _urlerr.URLError as exc:
        return _SimpleResponse(json.dumps({"error": str(exc)}).encode(), 500)


def get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, str]] = None, timeout: int = 30):  # noqa: D401, E501
    return _http("GET", url, headers=headers, params=params, timeout=timeout)

def post(url: str, headers: Optional[Dict[str, str]] = None, json: Optional[Dict[str, Any]] = None, timeout: int = 30):  # noqa: E501
    return _http("POST", url, headers=headers, json_body=json, timeout=timeout)

# Ensure module object has get/post attributes to mimic real requests
sys.modules[__name__] = SimpleNamespace(get=get, post=post, __doc__=__doc__)