from dateutil.parser import parse


def get_config_start_date(config):
    return parse(config.get('start_date'))
