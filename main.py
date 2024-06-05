import logging
from fastapi import FastAPI, Request, Response
import httpx
import oai_server
import re

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
    if 'metadataPrefix' not in params:
        params['metadataPrefix'] = 'dcat_ap'
    response = oai_server.oai_server.handleRequest(params)
    logging.debug(f"OAI-PMH Response: {response}")
    # Replace date in datestamp by empty string
    response = re.sub(b'<datestamp>.*</datestamp>', b'', response)
    return Response(content=response, media_type="text/xml")


# To run, use uvicorn main:app --reload
