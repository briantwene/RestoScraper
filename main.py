# server.py
from fastapi import FastAPI, HTTPException
from scraper import get_menu_reservation, setup_agent_environment
from model import RestaurantInfo
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await setup_agent_environment(app)

    yield  # Waits here until app is shutting down

    # Shutdown
    if hasattr(app.state, "server"):
        await app.state.server.cleanup()

app = FastAPI(lifespan=lifespan)
@app.post("/scrape")
async def scrape_endpoint(data: RestaurantInfo):
    try:

        if not data.name or not data.website or not data.location:
            raise HTTPException(status_code=400, detail="Name and website and location are required fields.")
        
        agent = app.state.agent
        server = app.state.server
        result = await get_menu_reservation(agent, restaurant_info=data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, port=9000)