from fastapi import FastAPI

app = FastAPI(
    title="AgriRent AI",
    version="1.0.0",
    description="AI-Powered Agricultural Equipment Rental Platform"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to AgriRent AI",
        "hi": "Hi I am Harissh"
    }