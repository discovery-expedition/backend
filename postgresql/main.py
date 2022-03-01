from fastapi import FastAPI
from database import engine
from models.influencer import Influencer

app = FastAPI()

Influencer.metadata.create_all(bind=engine)

@app.get("/")
async def create_database():
	return {"Database": "created"}
