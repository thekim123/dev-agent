from dotenv import load_dotenv
from fastapi import FastAPI
from app.api import agent, images, health

load_dotenv()
app = FastAPI()

app.include_router(health.router)
app.include_router(agent.router)
app.include_router(images.router)
