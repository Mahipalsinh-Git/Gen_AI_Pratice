from fastapi import FastAPI, Query
from .queue.connection import queue
from .queue.worker import process_query

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "Server is up and running"}


@app.post("/chat")
def chat(userQuery: str = Query(..., description="Chat Message")):
    # Query ko queue me dal do
    # User ko bolo your job received
    # job = queue.enqueue(process_query, userQuery)
    job = queue.enqueue("pratice.05_class.queue.worker.process_query", userQuery)
    print("queue id:", job)
    return {"status": "queued", "job_id": job.id}


"""
"""
