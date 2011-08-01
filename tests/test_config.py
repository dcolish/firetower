from os import getcwd
from os.path import join
from StringIO import StringIO

from firetower.config import Config

simple_config = StringIO("""\
#
# Sample Firetower Config
#

# Redis Server
redis_host: localhost
redis_port: 6379

# Queue source for classification
queue_key: incoming

# Time Between Alert Checks

alert_time: 0.5

# How far back in time we look for error counts.

timeslices:
  - 300  # Look 5 minutes into the past for threshold checks

# These are the things we'll be matching against

error_signatures:
  Test Error:
    signatures:
      sig:
        Test Error
      threshold:
        0.5
    alert_thresholds:
      high:
        1000
      med:
        100
      low:
        10
""")


def test_simple_config():
    conf = Config()
    conf.load(simple_config)
    assert conf.redis_host == 'localhost'
    assert conf.redis_port == 6379
    assert conf.queue_key == 'incoming'
    assert conf.alert_time == 0.5
    assert conf.timeslices == [300]
    assert conf.error_signatures == {
            'Test Error': {
                'signatures':
                    {'threshold': 0.5, 'sig': 'Test Error'},
                'alert_thresholds': {'high': 1000, 'med': 100, 'low': 10}
                }
            }


def test_read_conf():
    #XXX:dc: this only passes when you run it from the top level project
    # directory
    local_path = getcwd()
    conf = Config()
    with open(join(local_path, 'tests/fixtures/config.yaml')) as conf_file:
        conf.load(conf_file)
