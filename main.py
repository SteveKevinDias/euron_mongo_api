from fastapi import FastAPI,HTTPException
from fastapi.responses import HTMLResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware # Required for frontend integration

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI) # to make api prod grade

db = client["euron"]

euron_data = db["euron_col"]

app = FastAPI()
# --- CORS Configuration ---
# Allows the frontend served from any origin (e.g., localhost or canvas environment) 
# to communicate with this API.
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class eurondata(BaseModel):
    name:str
    phone:int
    city:str
    course:str

@app.get("/")
def serve_home():
    with open("static/index.html") as file:
        return HTMLResponse(content=file.read())

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/euron/insert")
async def euron_data_insert_helper(data:eurondata):
    result = await euron_data.insert_one(data.dict())
    return str(result.inserted_id)

def euron_helper(doc):
    doc["id"] = str(doc["_id"]) # Removes id and returns everything else
    del doc["_id"]
    return doc
    

@app.get("/euron/getdata")
async def get_euron_data():
    iterms = []
    cursor = euron_data.find({})
    async for document in cursor:
        iterms.append(euron_helper(document)) # iterms.append(document)
    return iterms

@app.put("/euron/update/{phone}")
async def update_euron_data(phone:int, data:eurondata):
    updated_data = await euron_data.update_one({"phone": phone}, {"$set":data.dict()})
    if updated_data.modified_count == 1:
        return {"msg":"Data updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Data not found")
    
@app.delete("/euron/delete/{phone}")
async def delete_euron_data(phone:int):
    deleted_data = await euron_data.delete_one({"phone": phone})
    if deleted_data.deleted_count == 1:
        return {"msg":"Data deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Data not found")

@app.get("/euron/getdata/{id}")
async def get_euron_data(phone:int):
    iterms = []
    cursor = euron_data.find({"phone": phone})
    async for document in cursor:
        iterms.append(euron_helper(document)) # iterms.append(document)
    return iterms