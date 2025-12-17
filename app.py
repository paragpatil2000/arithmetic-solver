from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from arithmetic_solver import solve
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Arithmetic Solver API")

class Problem(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"message": "Arithmetic Solver Running. Use POST /solve"}

@app.post("/solve")
async def solve_problem(p: Problem):
    try:
        return solve(p.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
