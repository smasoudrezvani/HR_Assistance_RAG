from fastapi import FastAPI
import uvicorn

app = FastAPI()

# @app.get("/api/query")

# def query_endpoint(q: str):
#     return {"answer": f"Hello Newcomer, you asked: '{q}'. How are you doing today? I am a simple RAG assistant built with FastAPI and OpenAI. Ask me anything about our company policies!"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0",port = 8000)

@app.get("/")

def route_controller():
    return {"status" : "healthy"}
# curl -X GET http://localhost:8000/ or curl http://localhost:8000/ --> windows
if __name__ == "__main__":
    uvicorn.run("main:app", port=8000,reload = True)
