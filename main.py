from fastapi import FastAPI

from app.api import api_router

app = FastAPI()

app.include_router(api_router)


def main():
    pass


if __name__ == "__main__":
    main()
