from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_graph import agent_app

class NoteRequest(BaseModel):
    prompt: str

app = FastAPI()

# Allow frontend (React) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/create-note")
async def create_note(req: NoteRequest):
    state = {"user_prompt": req.prompt}
    result = agent_app.invoke(state)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
