from rdflib import Graph, Literal, Namespace, RDF, URIRef, BNode
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, RDFS
import logging

# Logging config
logging.basicConfig(level=logging.DEBUG)

# Namespaces for DCAT-AP
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
EDP = Namespace("https://europeandataportal.eu/voc#")
SPDX = Namespace("http://spdx.org/rdf/terms#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
DQV = Namespace("http://www.w3.org/ns/dqv#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("http://schema.org/")

# Mapping between current fields and DCAT-AP equivalents
FIELD_MAPPINGS = {
    "dataset.metadata.description": (DCT.description, Literal),
    "dataset.metadata.contact.name": (VCARD.fn, Literal),
    "dataset.metadata.contact.email": (VCARD.hasEmail, lambda x: URIRef(f"mailto:{x}")),
    "dataset.metadata.contact.webpage": (VCARD.hasURL, URIRef),
    "dataset.metadata.label": (DCT.title, Literal),
    "dataset.metadata.doi": (DCT.identifier, Literal),
    "dataset.metadata.publication_date": (
        DCT.issued,
        lambda x: Literal(x, datatype=DCT.W3CDTF),
    ),
    "dataset.metadata.update_frequency": (DCT.accrualPeriodicity, Literal),
    "dataset.metadata.license": (DCT.license, URIRef),
    "dataset.metadata.id": (DCT.identifier, Literal),
    "url": (DCAT.accessURL, URIRef),
    "dataset.products.monthly.description": (DCT.description, Literal),
    # Add mappings for missing fields
    "dataset.metadata.keywords": (DCAT.keyword, Literal),
    "dataset.metadata.categories": (DCAT.theme, Literal),
    "dataset.metadata.spatial_coverage": (DCT.spatial, Literal),
    "dataset.metadata.temporal_coverage": (DCT.temporal, Literal),
    "dataset.products.monthly.download_url": (DCAT.downloadURL, URIRef),
    "dataset.products.monthly.format": (DCT.format, Literal),
    "dataset.products.monthly.media_type": (DCAT.mediaType, Literal),
    "dataset.metadata.access_rights": (DCT.accessRights, Literal),
    "dataset.metadata.rights": (DCT.rights, Literal),
    "dataset.products.monthly.file_size": (DCAT.byteSize, Literal),
    "dataset.metadata.modification_date": (
        DCT.modified,
        lambda x: Literal(x, datatype=DCT.W3CDTF),
    ),
}

def add_field_to_graph(graph, node, data, field_mappings):
    for field_path, (dcat_property, converter) in field_mappings.items():
        # Navigate the data using the field path (e.g. "dataset.metadata.description")
        value = data
        try:
            for part in field_path.split("."):
                value = value[part]
            # Add the value to the graph if it exists and isn't equal to 'null'
            if value is not None and value != "null":
                logging.debug(f"Adding field {field_path} with value {value}")
                graph.add((node, dcat_property, converter(value)))
            else:
                logging.debug(f"Field {field_path} is None or 'null'")

        except (KeyError, TypeError) as e:
            # Field not found, continue to next field
            logging.debug(f"Field {field_path} not found: {e}")
            continue

def convert_to_dcat_ap(data, url):
    logging.debug("Starting convert_to_dcat_ap function")

    # Add the URL to the data
    data["url"] = url
    
    g = Graph()

    # Bind namespaces
    g.bind("dcat", DCAT)
    g.bind("DCT", DCT)
    g.bind("foaf", FOAF)
    g.bind("vcard", VCARD)
    g.bind("edp", EDP)
    g.bind("spdx", SPDX)
    g.bind("adms", ADMS)
    g.bind("dqv", DQV)
    g.bind("skos", SKOS)
    g.bind("schema", SCHEMA)

    # Create a dataset
    dataset = URIRef("http://example.org/dataset/blue-tongue")
    g.add((dataset, RDF.type, DCAT.Dataset))

    # Iterate over field mappings, add them to the RDF graph if present
    for field_path, (dcat_property, converter) in FIELD_MAPPINGS.items():
        # Navigate the data using the field path
        value = data
        try:
            for part in field_path.split("."):
                value = value[part]
            # Add the value to the graph if it exists and isn't equal to 'null'
            if value is not None and value != "null":
                logging.debug(f"Adding field {field_path} with value {value}")
                g.add((dataset, dcat_property, converter(value)))
            else:
                logging.debug(f"Field {field_path} is None or 'null'")

        except (KeyError, TypeError) as e:
            # Field not found, continue to next field
            logging.debug(f"Field {field_path} not found: {e}")
            continue

    # Handle building of contactPoint separately
    if "metadata" in data["dataset"] and "contact" in data["dataset"]["metadata"]:
        contact = data["dataset"]["metadata"]["contact"]
        contact_point = BNode()
        g.add((dataset, DCAT.contactPoint, contact_point))

        contact_field_mappings = {key: value for key, value in FIELD_MAPPINGS.items() 
                                  if key.startswith("dataset.metadata.contact.")}
        add_field_to_graph(g, contact_point, contact, contact_field_mappings)

    return g
