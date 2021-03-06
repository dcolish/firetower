from yaml import load


class ConfigError(Exception):
    """Base Exception class for all Config Errors"""


class SignatureMissingError(ConfigError):
    """Raised whehn no signatures are found to match errors against"""


class Config(object):
    """Configuraiton Object - read and store conf values.
    """

    def __init__(self):
        """
        :param conf_file: File or file-like object to load values from
        """
        self._defaults = (
            ('redis_host', 'localhost'),
            ('redis_port', 6379),
            ('queue_key', 'incoming'),
            ('timeslices', [300]),
            ('alert_time', 1.0),
            )

    def load(self, conf_file):
        """
        Convert string version of configuration to python datastructures.
        """
        defaults = dict(self._defaults)
        conf_dict = load(conf_file)
        if not conf_dict.get('error_signatures'):
            raise SignatureMissingError('No Error Signatures Defined in Conf')

        defaults.update(conf_dict)
        for k, v in defaults.items():
            setattr(self, k, v)
