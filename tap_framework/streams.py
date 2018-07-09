import inspect
import os.path
import singer
import singer.utils
import singer.metrics

from funcy import project

LOGGER = singer.get_logger()


class BaseStream:
    # GLOBAL PROPERTIES
    TABLE = None
    KEY_PROPERTIES = ['id']
    API_METHOD = 'GET'
    REQUIRES = []

    def __init__(self, config, state, catalog, client):
        self.config = config
        self.state = state
        self.catalog = catalog
        self.client = client
        self.substreams = []

    def get_class_path(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def load_schema_by_name(self, name):
        return singer.utils.load_json(
            os.path.normpath(
                os.path.join(
                    self.get_class_path(),
                    '../schemas/{}.json'.format(name))))

    def get_schema(self):
        return self.load_schema_by_name(self.TABLE)

    def get_stream_data(self, result):
        """
        Given a result set from Campaign Monitor, return the data
        to be persisted for this stream.
        """
        raise RuntimeError("get_stream_data not implemented!")

    def get_url(self):
        """
        Return the URL to hit for data from this stream.
        """
        raise RuntimeError("get_url not implemented!")


    @classmethod
    def requirements_met(cls, catalog):
        selected_streams = [
            s.stream for s in catalog.streams if s.schema.selected
        ]

        return set(cls.REQUIRES).issubset(selected_streams)

    @classmethod
    def matches_catalog(cls, stream_catalog):
        return stream_catalog.stream == cls.TABLE

    def generate_catalog(self):
        return [{
            'tap_stream_id': self.TABLE,
            'stream': self.TABLE,
            'key_properties': self.KEY_PROPERTIES,
            'schema': self.get_schema()
        }]

    def get_catalog_keys(self):
        return list(self.catalog.schema.properties.keys())

    def filter_keys(self, obj):
        return project(obj, self.get_catalog_keys())

    def write_schema(self):
        singer.write_schema(
            self.catalog.stream,
            self.catalog.schema.to_dict(),
            key_properties=self.catalog.key_properties)

    def sync(self):
        LOGGER.info('Syncing stream {} with {}'
                    .format(self.catalog.tap_stream_id,
                            self.__class__.__name__))

        self.write_schema()

        return self.sync_data()

    def sync_data(self, substreams=None):
        if substreams is None:
            substreams = []

        table = self.TABLE

        url = self.get_url()

        result = self.client.make_request(url, self.API_METHOD)

        data = self.get_stream_data(result)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for index, obj in enumerate(data):
                LOGGER.debug("On {} of {}".format(index, len(data)))

                singer.write_records(
                    table,
                    [self.filter_keys(obj)])

                counter.increment()

                for substream in substreams:
                    substream.sync_data(parent=obj)


class ChildStream(BaseStream):

    def get_parent_id(self, parent):
        raise NotImplementedError('get_parent_id is not implemented!')

    def get_api_path_for_child(self, parent):
        raise NotImplementedError(
            'get_api_path_for_child is not implemented!')

    def sync_data(self, parent=None):
        if parent is None:
            raise RuntimeError('Cannot sync a subobject of null!')

        table = self.TABLE
        url = self.get_url()

        result = self.client.make_request(url, self.API_METHOD)

        data = self.get_stream_data(result)

        with singer.metrics.record_counter(endpoint=table) as counter:
            for obj in data:
                singer.write_records(
                    table,
                    [self.filter_keys(
                        self.incorporate_parent_id(obj, parent))])

                counter.increment()
