from oaipmh.server import ServerBase, oai_dc_writer
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
import metadata_provider
from lxml.etree import fromstring

# Create writer for dcat_ap metadata 
def dcat_ap_writer(metadata_element, metadata):
    rdf_string = metadata["rdf"]
    rdf_element = fromstring(rdf_string)
    for child in rdf_element:
        metadata_element.append(child)

class MyServer(ServerBase):
    def __init__(self):
        metadata_registry = MetadataRegistry()
        metadata_registry.registerWriter("oai_dc", oai_dc_writer)
        metadata_registry.registerReader("oai_dc", oai_dc_reader)
        server = metadata_provider.MyMetadataProvider()
        super(MyServer, self).__init__(server, metadata_registry)


oai_server = MyServer()
