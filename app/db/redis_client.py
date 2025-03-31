from redis import StrictRedis

from app.core.config import settings

r = StrictRedis(host=str(settings.REDIS_URL))


if __name__ == "__main__":
    print(r.ping())
    r.set("test", "test")
    print(r.get("test"))
