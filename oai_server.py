from oaipmh.server import ServerBase, oai_dc_writer
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
import metadata_provider


class MyServer(ServerBase):
    def __init__(self):
        metadata_registry = MetadataRegistry()
        metadata_registry.registerWriter("oai_dc", oai_dc_writer)
        metadata_registry.registerReader("oai_dc", oai_dc_reader)
        server = metadata_provider.MyMetadataProvider()
        super(MyServer, self).__init__(server, metadata_registry)


oai_server = MyServer()
