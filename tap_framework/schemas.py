import os.path
import singer.utils
import sys


def get_abs_path(path):
    return os.path.join(
        os.path.dirname(
            os.path.dirname(
                sys.modules['__main__'].__file__)),
        path)


def load_schema_by_name(name):
    return singer.utils.load_json('schemas/{}.json'.format(name))
