
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import pandas as pd
from typing import List, Any, Dict

app = FastAPI()
DB_PATH = "/root/lumina_sql_lab/lumina.db"

class QueryRequest(BaseModel):
    sql: str
    challenge_id: str

class Challenge(BaseModel):
    id: str
    sql_expected: str
    module: str

# Mock challenges database
CHALLENGES = {
    "basic_1": Challenge(id="basic_1", sql_expected="SELECT name FROM users WHERE id = 1", module="Basics"),
    "agg_1": Challenge(id="agg_1", sql_expected="SELECT SUM(amount) FROM orders", module="Aggregation"),
}

def execute_sql(sql: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use pandas for easy table comparison and JSON serialization
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"SQL Error: {str(e)}")

@app.post("/execute")
async def execute_and_validate(request: QueryRequest):
    # 1. Execute user SQL
    user_result = execute_sql(request.sql)
    
    # 2. Validation Logic
    if request.challenge_id not in CHALLENGES:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    expected_sql = CHALLENGES[request.challenge_id].sql_expected
    expected_result = execute_sql(expected_sql)
    
    # Compare dataframes (ignoring index)
    is_correct = user_result.equals(expected_result)
    
    return {
        "is_correct": is_correct,
        "user_result": user_result.to_dict(orient="records"),
        "expected_result": expected_result.to_dict(orient="records") if not is_correct else None
    }

@app.get("/challenge/daily")
async def get_daily_challenge(module: str = "Basics"):
    # Simple rotation logic based on module
    relevant = [c for c in CHALLENGES.values() if c.module == module]
    if not relevant:
        return {"error": "No challenges for this module"}
    # In real app, this would rotate by date
    return relevant[0].dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
