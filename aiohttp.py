"""aiohttp stub – minimal subset."""
class ClientSession:  # noqa: D101
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def get(self, *args, **kwargs):
        class _Resp:
            status = 200
            async def json(self):
                return {}
        return _Resp()

    async def post(self, *args, **kwargs):
        class _Resp:
            status = 200
            async def json(self):
                return {}
        return _Resp()