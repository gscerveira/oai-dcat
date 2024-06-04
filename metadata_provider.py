from oaipmh.common import Identify, Metadata, Header
from datetime import datetime
from lxml import etree
from lxml.etree import Element, SubElement, fromstring, tostring
import main
from utils import convert_to_dcat_ap
import logging

# Logging config
logging.basicConfig(level=logging.DEBUG)


class MyMetadataProvider:
    # Method to list records, only method used by data.europa harvester
    def listRecords(self, metadataPrefix='oai_dc', from_=None, until=None, set_=None):
        logging.debug("Fetching data from API")
        # Fetch data from the dataset endpoint
        data = main.fetch_data(
            "https://sebastien-datalake.cmcc.it/api/v2/datasets/blue-tongue"
        )
        logging.debug(f"Fetched data: {data}")

        # Convert to DCAT-AP format
        rdf_graph = convert_to_dcat_ap(data)

        # Serialize RDF graph
        rdf_string = rdf_graph.serialize(format='xml')
        logging.debug(f"RDF string: {rdf_string}")

        # Parse RDF string into XML element
        rdf_element = fromstring(bytes(rdf_string, encoding='utf-8'))

        logging.debug(f"Parsed RDF Element: {tostring(rdf_element, pretty_print=True).decode('utf-8')}")

        # Create a header
        identifier = "id1"
        datestamp = datetime.utcnow().isoformat() + "Z"
        header_element = Element("header")
        header = Header(deleted=False, element=header_element, identifier=identifier, datestamp=datetime.utcnow(), setspec=[])

        # Create metadata element and include RDF elements as children of oai_dc:dc
        metadata_element = Element("metadata")
        oai_dc_element = SubElement(metadata_element, "{http://www.openarchives.org/OAI/2.0/oai_dc/}dc", nsmap={
            "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
            "dc": "http://purl.org/dc/elements/1.1/",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        })
        oai_dc_element.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                           "http://www.openarchives.org/OAI/2.0/oai_dc/ http://www.openarchives.org/OAI/2.0/oai_dc.xsd")

        # Append children of rdf_element to oai_dc_element
        for child in rdf_element:
            oai_dc_element.append(child)

        logging.debug(f"Final OAI_DC Element: {tostring(oai_dc_element, pretty_print=True).decode('utf-8')}")

        metadata = Metadata(element=metadata_element, map={})
        logging.debug(f"Metadata Element: {tostring(metadata_element, pretty_print=True).decode('utf-8')}")

        return [(header, metadata, [])], None

    # Minimal implementation for identify
    def identify(self):
        return Identify(
            repositoryName='My Repository',  # Name of the repository
            baseURL='http://myserver.com/oai',  # Base URL of the OAI-PMH endpoint
            protocolVersion='2.0',  # OAI-PMH protocol version
            adminEmails=['admin@myserver.com'],  # List of admin email addresses
            earliestDatestamp=datetime(2024, 1, 1),  # Earliest datestamp for records
            deletedRecord='no',  # Policy on deleted records
            granularity='YYYY-MM-DDThh:mm:ssZ',  # Date granularity
            compression=['identity'],  # Supported compression methods
        )

    # Minimal implementation for getRecord
    def getRecord(self, identifier, metadataPrefix='oai_dc'):
        # Create a header
        header = Header(identifier=identifier, datestamp=datetime.now(), setspec=[])

        # Create metadata element (empty in this example)
        metadata = Metadata(element=Element("record"), map={})

        return header, metadata, []

    # Minimal implementation for listIdentifiers
    def listIdentifiers(self, metadataPrefix='oai_dc', from_=None, until=None, set_=None):
        # Create a header
        header = Header(identifier="id1", datestamp=datetime.now(), setspec=[])

        return [header]

    # Minimal implementation for listMetadataFormats
    def listMetadataFormats(self, identifier=None):
        return [('oai_dc', 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd', 'http://www.openarchives.org/OAI/2.0/oai_dc/')]

    # Minimal implementation for listSets
    def listSets(self):
        return []
