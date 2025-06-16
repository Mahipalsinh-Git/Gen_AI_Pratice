from fastapi import FastAPI, Query, Path
from .queue.connection import queue
from .queue.worker import process_query


app = FastAPI()


@app.get("/")
def root():
    return {"status": "server is up and running"}


@app.post("/chat")
def chat(query: str = Query(..., description="Chat messge")):
    # job = queue.enqueue(process_query, query)
    job = queue.enqueue("pratice.rag_queue.queue.worker.process_query", query)
    return {"status": "queued", "job_id": job.id}

    # This query insert int queue, and then update to user "Your query is got"


@app.get("/result/{job_id}")
def get_result(job_id: str = Path(..., description="Job ID")):
    job = queue.fetch_job(job_id=job_id)
    result = job.return_value()
    return {"result": result}
