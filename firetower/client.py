import random
from optparse import OptionParser

from firetower.config import Config
from firetower.redis_util import Redis
from firetower.tracebacks import tracebacks
from firetower.util import json


FAKE_SIGS = [
'Test Exception', 'Another Random Error'
]
FAKE_SIGS = tracebacks

FAKE_DATA = {'hostname': 'testmachine',
             'msg': 'I/O Exception from some file',
             'logfacility': 'local1',
             'syslogtag': 'test',
             'programname': 'firetower client',
             'severity': None}


class Client(object):
    """Main loop."""

    def run(self, conf):
        queue = Redis(host=conf.redis_host, port=conf.redis_port)
        print queue.conn.keys()
        for i in xrange(0, 50):
            try:
                # Semi-randomly seed the 'sig' key in our fake errors
                FAKE_DATA['sig'] = random.choice(FAKE_SIGS)
                print FAKE_DATA
                encoded = json.dumps(FAKE_DATA)
                err = queue.push(conf.queue_key, encoded)
            except:
                print "Something went wrong storing value from redis"


def main():
    parser = OptionParser(usage='usage: firetower options args')
    parser.add_option(
        '-c', '--conf', action='store', dest='conf_path',
         help='Path to YAML configuration file.')

    (options, args) = parser.parse_args()

    if len(args) > 1:
        parser.error('Please supply some arguments')

    conf = Config()
    with open(options.conf_path) as conf_file:
        conf.load(conf_file)

    main = Client()
    main.run(conf)
