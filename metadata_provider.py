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

        # Create a header element
        header_element = Element("header")
        header = Header(element=header_element, deleted=False, identifier="id1", datestamp=datetime.now(), setspec=[])

           
        
        
        # Create metadata element and add RDF data
        metadata_element = Element("metadata")
        
        
        for child in rdf_element:
            metadata_element.append(child)

        #metadata_element.append(rdf_element)
        metadata = Metadata(element=metadata_element, map={})

        logging.debug(f"Metadata Element: {tostring(metadata_element, pretty_print=True).decode('utf-8')}")

        # Return the record element instead of the header and metadata separately
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
    #def getRecord(self, identifier, metadataPrefix):
        # Return dummy record data
    #    header = Header(identifier=identifier, datestamp=datetime.now(), sets=[])
    #    metadata = Metadata(element=Element("record"), map={})
    #    return header, metadata, []

    # Minimal implementation for listIdentifiers
    #def listIdentifiers(self, metadataPrefix, from_=None, until=None, set_=None):
    #    # Return dummy identifiers
    #    return [Header(identifier="id1", datestamp=datetime.now(), sets=[])]

    # Minimal implementation for listMetadataFormats
    #def listMetadataFormats(self, identifier=None):
    #    return [('oai_dc', 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd', 'http://www.openarchives.org/OAI/2.0/oai_dc/')]

    # Minimal implementation for listSets
    #def listSets(self):
    #    return []
