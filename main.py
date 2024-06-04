import logging
from fastapi import FastAPI, Request, Response
import httpx
import oai_server

# Logging config
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()


# Fetch data from an endpoint with httpx
def fetch_data(url):
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


# Define OAI-PMH endpoint route
@app.get("/oai")
@app.post("/oai")
def oai(request: Request):
    params = dict(request.query_params)
    response = oai_server.oai_server.handleRequest(params)
    logging.debug(f"OAI-PMH Response: {response}")
    return Response(content=response, media_type="text/xml")


# To run, use uvicorn main:app --reload
