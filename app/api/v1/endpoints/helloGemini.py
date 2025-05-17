from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/hello")
def say_hello():
    return {
        "Hello Gemini"
    }