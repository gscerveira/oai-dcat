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

class ContactPoint:
    def __init__(self, name=None, email=None, webpage=None):
        self.name = name
        self.email = email
        self.webpage = webpage

class Distribution:
    def __init__(self, access_url=None, description=None, download_url=None,
                 media_type=None, format=None, rights=None, license=None, identifier=None):
        self.access_url = access_url
        self.description = description
        self.download_url = download_url
        self.media_type = media_type
        self.format = format
        self.rights = rights
        self.license = license
        self.identifier = identifier

class Dataset:
    def __init__(self, uri, title=None, description=None, issued=None, identifier=None, contact_point=None):
        self.uri = uri
        self.title = title
        self.description = description
        self.issued = issued
        self.identifier = identifier
        self.contact_point = contact_point
        self.distributions = []

    def add_distribution(self, distribution):
        self.distributions.append(distribution)

    def to_graph(self, g):
        dataset = URIRef(self.uri)
        g.add((dataset, RDF.type, DCAT.Dataset))
        if self.title:
            g.add((dataset, DCT.title, Literal(self.title)))
        if self.description:
            g.add((dataset, DCT.description, Literal(self.description)))
        if self.issued:
            g.add((dataset, DCTERMS.issued, Literal(self.issued, datatype=DCTERMS.W3CDTF)))
        if self.identifier:
            g.add((dataset, DCTERMS.identifier, Literal(self.identifier)))

        if self.contact_point:
            contact_bnode = BNode()
            g.add((dataset, DCAT.contactPoint, contact_bnode))
            if self.contact_point.name:
                g.add((contact_bnode, VCARD.fn, Literal(self.contact_point.name)))
            if self.contact_point.email:
                g.add((contact_bnode, VCARD.hasEmail, URIRef(f"mailto:{self.contact_point.email}")))
            if self.contact_point.webpage:
                g.add((contact_bnode, VCARD.hasURL, URIRef(self.contact_point.webpage)))

        for dist in self.distributions:
            distribution_bnode = BNode()
            g.add((dataset, DCAT.distribution, distribution_bnode))
            if dist.access_url:
                g.add((distribution_bnode, DCAT.accessURL, URIRef(dist.access_url)))
            if dist.description:
                g.add((distribution_bnode, DCTERMS.description, Literal(dist.description)))
            if dist.download_url:
                g.add((distribution_bnode, DCAT.downloadURL, URIRef(dist.download_url)))
            if dist.media_type:
                g.add((distribution_bnode, DCTERMS.mediaType, URIRef(dist.media_type)))
            if dist.format:
                g.add((distribution_bnode, DCTERMS.format, URIRef(dist.format)))
            if dist.rights:
                rights_bnode = BNode()
                g.add((distribution_bnode, DCTERMS.rights, rights_bnode))
                g.add((rights_bnode, RDF.type, DCTERMS.RightsStatement))
                g.add((rights_bnode, DCTERMS.rights, URIRef(dist.rights)))
            if dist.license:
                license_bnode = BNode()
                g.add((distribution_bnode, DCTERMS.license, license_bnode))
                g.add((license_bnode, RDF.type, DCTERMS.LicenseDocument))
                g.add((license_bnode, DCTERMS.license, URIRef(dist.license)))
            if dist.identifier:
                g.add((distribution_bnode, DCTERMS.identifier, Literal(dist.identifier)))

        return g

# Mapping between current fields and DCAT-AP equivalents
""" FIELD_MAPPINGS = {
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
            continue """

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
    dataset_uri = "http://example.org/dataset/blue-tongue"
    
    # Create dataset
    dataset = Dataset(
        uri=dataset_uri,
        title=data.get("dataset", {}).get("metadata", {}).get("label"),
        description=data.get("dataset", {}).get("metadata", {}).get("description"),
        issued=data.get("dataset", {}).get("metadata", {}).get("publication_date"),
        identifier=data.get("dataset", {}).get("metadata", {}).get("id"),
    )

    # Create contact point
    contact = data.get("dataset", {}).get("metadata", {}).get("contact")
    contact_point = ContactPoint(
        name=contact.get("name"),
        email=contact.get("email"),
        webpage=contact.get("webpage"),
    )
    dataset.contact_point = contact_point

    # Create distributions
    products = data.get("dataset", {}).get("products", {}).get("monthly", {})
    distribution = Distribution(
        access_url=url,
        description=products.get("description"),
        )
    dataset.add_distribution(distribution)

    # Add dataset to graph
    dataset.to_graph(g)

    """ g.add((dataset, RDF.type, DCAT.Dataset))

    # Iterate over field mappings, add them to the RDF graph if present
    add_field_to_graph(g, dataset, data, FIELD_MAPPINGS)

    # Handle building of contactPoint separately
    if "metadata" in data["dataset"] and "contact" in data["dataset"]["metadata"]:
        contact = data["dataset"]["metadata"]["contact"]
        contact_point = BNode()
        g.add((dataset, DCAT.contactPoint, contact_point))

        contact_field_mappings = {key: value for key, value in FIELD_MAPPINGS.items() 
                                  if key.startswith("dataset.metadata.contact.")}
        add_field_to_graph(g, contact_point, contact, contact_field_mappings) """

    return g
