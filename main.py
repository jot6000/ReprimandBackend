from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb+srv://admin:BDVoTAlwXkMtaSqk@cluster0.vw4xy.mongodb.net/test")
db = client["reprimandApp"]
rep_collection = db["reprimands"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Reprimand(BaseModel):
    studentId: str
    staffName: str
    date: str
    time: str
    contactType: str
    contactReason: str
    details: str
    executed: bool

    class Config:
        schema_extra = {
            "example": {
                "studentId": "40029627",
                "staffName": "Joe Mercer",
                "date": "01/01/2020",
                "time": "00:00",
                "contactType": "s",
                "contactReason": "dd",
                "details": "Throwing chairs",
                "executed": False,
            }
        }

@app.post("/reprimand")
async def addReprimand(rep: Reprimand):
    """Used to add reprimands to the database"""
    result = rep_collection.insert_one(rep.dict())
    return { "insertion" : result.acknowledged }

def ReprimandEntity(db_item) -> dict:
    return{
        "_id": str(db_item["_id"]),
        **Reprimand(**db_item).dict()
    }

@app.get("/reprimand/nonExecuted")
async def getNonExecuted():
    """Retrieves all non executed reprimands"""
    repList = rep_collection.find({ "executed" : False })
    return [ ReprimandEntity(rep) for rep in repList]

@app.put("/reprimand/execute/{item_id}")
async def update_item(item_id: str):
    result = rep_collection.update_one({ "_id" : ObjectId(item_id) }, { "$set" : { "executed" : True } })
    return { "updated" : result.acknowledged }