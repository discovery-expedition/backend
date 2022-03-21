from pip import main
import models
from fastapi  import FastAPI, Depends
from database import engine
from routers  import main, performance
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(main.router)
app.include_router(performance.router)

@app.get("/")
async def create_database():
	return {"Database": "created"}




