import datetime
import json
import singer

from dateutil.parser import parse

LOGGER = singer.get_logger()


def get_last_record_value_for_table(state, table):
    last_value = state.get('bookmarks', {}) \
                      .get(table, {}) \
                      .get('last_record')

    if last_value is None:
        return None

    return parse(last_value)


def incorporate(state, table, field, value):
    if value is None:
        return state

    if state is None:
        new_state = {}
    else:
        new_state = state.copy()

    if isinstance(value, datetime.datetime):
        parsed = value.strftime("%Y-%m-%d %H:%M:%S")
    else:
        parsed = parse(value).strftime("%Y-%m-%d %H:%M:%S")

    if 'bookmarks' not in new_state:
        new_state['bookmarks'] = {}

    if(new_state['bookmarks'].get(table, {}).get('last_record') is None or
       new_state['bookmarks'].get(table, {}).get('last_record') < parsed):
        new_state['bookmarks'][table] = {
            'field': field,
            'last_record': parsed,
        }

    return new_state


def save_state(state):
    if not state:
        return

    LOGGER.info('Updating state.')

    singer.write_state(state)


def load_state(filename):
    if filename is None:
        return {}

    try:
        with open(filename) as handle:
            return json.load(handle)
    except:
        LOGGER.fatal("Failed to decode state file. Is it valid json?")
        raise RuntimeError
