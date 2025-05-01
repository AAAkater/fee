from fastapi import FastAPI

from app.api import api_router
from app.db.main import init_db

app = FastAPI(lifespan=init_db)


app.include_router(api_router)


def main():
    pass


if __name__ == "__main__":
    main()
