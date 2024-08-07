import logging
from fastapi import FastAPI, Request, Response
import httpx
import oai_server
import re
from metadata_provider import BASE_URL
from utils import convert_to_dcat_ap, convert_to_dcat_ap_it, serialize_and_concatenate_graphs

# Logging config
logging.basicConfig(level=logging.DEBUG)

# Initialize a FastAPI app to serve the OAI-PMH endpoint
app = FastAPI()


# Fetch data from an endpoint with httpx (used to get the data from the metadata from the datalake)
def fetch_data(url):
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        return response.json()


# Define OAI-PMH endpoint route
@app.get("/oai/{dataset_id}")
@app.post("/oai/{dataset_id}")
def oai(request: Request, dataset_id: str):
    params = dict(request.query_params)

    # Add dataset_id to the parameters as "set_", which is a parameter from the OAI-PMH protocol
    params['set'] = dataset_id

    # Making sure it uses the dcat_ap metadata prefix
    if 'metadataPrefix' not in params:
        params['metadataPrefix'] = 'dcat_ap'

    # handleRequest points the request to the appropriate method in metadata_provider.py
    response = oai_server.oai_server.handleRequest(params)
    logging.debug(f"OAI-PMH Response: {response}")
    # Replace date in datestamp by empty string
    response = re.sub(b'<datestamp>.*</datestamp>', b'', response)
    return Response(content=response, media_type="text/xml")

# Define an endpoint for getting all the datasets
@app.get("/oai")
@app.post("/oai")
def oai_all_datasets(request: Request):
    params = dict(request.query_params)

    # Making sure it uses the dcat_ap metadata prefix
    if 'metadataPrefix' not in params:
        params['metadataPrefix'] = 'dcat_ap'

    # handleRequest points the request to the appropriate method in metadata_provider.py
    response = oai_server.oai_server.handleRequest(params)
    logging.debug(f"OAI-PMH Response: {response}")
    # Replace date in datestamp by empty string
    response = re.sub(b'<datestamp>.*</datestamp>', b'', response)
    return Response(content=response, media_type="text/xml")

# Endpoint for generating DCAT-AP IT catalog
@app.get("/dcatapit")
def dcatapit(request: Request):
    data = fetch_data(BASE_URL)
    #dcatap_graph = convert_to_dcat_ap(data, BASE_URL)
    #dcatapit_graph = convert_to_dcat_ap_it(data, BASE_URL)
    catalog_graph, datasets_graph, distributions_graph, vcard_graph = convert_to_dcat_ap_it(data, BASE_URL)
    #response = dcatapit_graph.serialize(format='pretty-xml')
    response = serialize_and_concatenate_graphs(catalog_graph, datasets_graph, distributions_graph, vcard_graph)

    return Response(content=response, media_type="application/rdf+xml")

    




# To run, use uvicorn main:app --reload
# To use the OAI-PMH listRecords method, send a request to the following URL: http://localhost:8000/oai?verb=ListRecords
