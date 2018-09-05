#!/usr/bin/env python3

import json
import sys

import singer

from tap_framework.state import save_state
from tap_framework.streams import is_selected

LOGGER = singer.get_logger()  # noqa


class Runner:

    def __init__(self, args, client, available_streams):
        self.config = args.config
        self.state = args.state
        self.catalog = args.catalog
        self.client = client
        self.available_streams = available_streams

    def get_streams_to_replicate(self):
        streams = []

        if not self.catalog:
            return streams

        for stream_catalog in self.catalog.streams:
            if not is_selected(stream_catalog):
                LOGGER.info("'{}' is not marked selected, skipping."
                            .format(stream_catalog.stream))
                continue

            for available_stream in self.available_streams:
                if available_stream.matches_catalog(stream_catalog):
                    if not available_stream.requirements_met(self.catalog):
                        raise RuntimeError(
                            "{} requires that that the following are "
                            "selected: {}"
                            .format(stream_catalog.stream,
                                    ','.join(available_stream.REQUIRES)))

                    to_add = available_stream(
                        self.config, self.state, stream_catalog, self.client)

                    streams.append(to_add)

        return streams

    def do_discover(self):
        LOGGER.info("Starting discovery.")

        catalog = []

        for available_stream in self.available_streams:
            stream = available_stream(self.config, self.state, None, None)

            catalog += stream.generate_catalog()

        json.dump({'streams': catalog}, sys.stdout, indent=4)

    def do_sync(self):
        LOGGER.info("Starting sync.")

        streams = self.get_streams_to_replicate()

        for stream in streams:
            try:
                stream.state = self.state
                stream.sync()
                self.state = stream.state
            except OSError as e:
                LOGGER.error(str(e))
                exit(e.errno)

            except Exception as e:
                LOGGER.error(str(e))
                LOGGER.error('Failed to sync endpoint {}, moving on!'
                             .format(stream.TABLE))
                raise e

        save_state(self.state)


# @singer.utils.handle_top_exception(LOGGER)
# def main():
#     args = singer.utils.parse_args(
#         required_config_keys=['api_key', 'client_id'])

#     if args.discover:
#         do_discover(args)
#     else:
#         do_sync(args)


# if __name__ == '__main__':
#     main()
