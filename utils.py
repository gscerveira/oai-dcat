from rdflib import Graph, Literal, Namespace, RDF, URIRef, BNode
from rdflib.namespace import DCAT, DCTERMS, FOAF
import logging

# Logging config
logging.basicConfig(level=logging.DEBUG)

# Namespaces for DCAT-AP
DCAT = Namespace("http://www.w3.org/ns/dcat#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

# Mapping between current fields and DCAT-AP equivalents
FIELD_MAPPINGS = {
    "dataset.metadata.description": (DCTERMS.description, Literal),
    "dataset.metadata.contact.name": (VCARD.fn, Literal),
    "dataset.metadata.contact.email": (VCARD.hasEmail, lambda x: URIRef(f"mailto:{x}")),
    "dataset.metadata.contact.webpage": (VCARD.hasURL, URIRef),
    "dataset.metadata.label": (DCTERMS.title, Literal),
    "dataset.metadata.doi": (DCTERMS.identifier, Literal),
    "dataset.metadata.publication_date": (
        DCTERMS.issued,
        lambda x: Literal(x, datatype=DCTERMS.W3CDTF),
    ),
    "dataset.metadata.update_frequency": (DCTERMS.accrualPeriodicity, Literal),
    "dataset.metadata.license": (DCTERMS.license, URIRef),
    "dataset.metadata.id": (DCTERMS.identifier, Literal),
    "dataset.products.monthly.catalog_dir": (DCAT.accessURL, URIRef),
    "dataset.products.monthly.description": (DCTERMS.description, Literal),
    # Add mappings for missing fields
    "dataset.metadata.keywords": (DCAT.keyword, Literal),
    "dataset.metadata.categories": (DCAT.theme, Literal),
    "dataset.metadata.spatial_coverage": (DCTERMS.spatial, Literal),
    "dataset.metadata.temporal_coverage": (DCTERMS.temporal, Literal),
    "dataset.products.monthly.download_url": (DCAT.downloadURL, URIRef),
    "dataset.products.monthly.format": (DCTERMS.format, Literal),
    "dataset.products.monthly.media_type": (DCAT.mediaType, Literal),
    "dataset.metadata.access_rights": (DCTERMS.accessRights, Literal),
    "dataset.metadata.rights": (DCTERMS.rights, Literal),
    "dataset.products.monthly.file_size": (DCAT.byteSize, Literal),
    "dataset.metadata.modification_date": (
        DCTERMS.modified,
        lambda x: Literal(x, datatype=DCTERMS.W3CDTF),
    ),
}


def convert_to_dcat_ap(data):
    logging.debug("Starting convert_to_dcat_ap function")
    g = Graph()

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
    if "metadata" in data and "contact" in data["metadata"]:
        contact = data["metadata"]["contact"]
        contact_point = BNode()
        g.add((dataset, DCAT.contactPoint, contact_point))

        for field_path, (dcat_property, converter) in FIELD_MAPPINGS.items():
            if field_path.startswith("dataset.metadata.contact."):
                value = contact
                try:
                    for part in field_path.split("."):
                        value = value[part]
                    if value is not None and value != "null":
                        logging.debug(f"Adding contact field {field_path} with value {value}")
                        g.add((contact_point, dcat_property, converter(value)))
                    else:
                        logging.debug(f"Contact field {field_path} is None or 'null'")
                except (KeyError, TypeError) as e:
                    logging.debug(f"Contact field {field_path} not found: {e}")
                    continue

    return g
