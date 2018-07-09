import requests
import singer
import time

LOGGER = singer.get_logger()


class BaseClient:

    def __init__(self, config):
        self.config = config

    def get_authorization(self):
        raise RuntimeError("get_authorization not implemented!")

    def make_request(self, url, method, base_backoff=45,
                     params=None, body=None):
        auth = self.get_authorization()

        LOGGER.info("Making {} request to {}".format(method, url))

        response = requests.request(
            method,
            url,
            headers={
                'Content-Type': 'application/json'
            },
            auth=auth,
            params=params,
            json=body)

        if response.status_code == 429:
            LOGGER.info('Got a 429, sleeping for {} seconds and trying again'
                        .format(base_backoff))
            time.sleep(base_backoff)
            return self.make_request(url, method, base_backoff * 2, params, body)

        if response.status_code != 200:
            raise RuntimeError(response.text)

        return response.json()
