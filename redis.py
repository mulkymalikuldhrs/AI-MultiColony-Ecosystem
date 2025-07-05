"""redis stub – minimal stand-in to satisfy imports when real redis-py not present."""
class RedisStub:
    def __getattr__(self, item):
        raise ImportError("Stub redis module in use; install real 'redis' package for full functionality")

StrictRedis = Redis = RedisStub()