import logging
import sys

import requests

from django_loki.formatters import LokiFormatter


class LokiHttpHandler(logging.Handler, object):
    """Python logging handler for Loki. Sends events over Http.
    :param host: The host of the loki server.
    :param port: The port of the loki server (default 3100).
    """

    def __init__(self, host: str = 'localhost', port: str = 3100, timeout=0.5, protocol: str = 'http',
                 source: str = 'Loki', src_host: str = 'localhost', tz: str = 'UTC'):
        super(LokiHttpHandler, self).__init__()
        self._address = f'{protocol}://{host}:{port}'
        self._post_address = f'{self._address}/api/prom/push'
        self._tz = tz
        self._timeout = timeout
        self._source = source
        self._src_host = src_host

    def emit(self, record):
        """
        Emit a record.
        Send the record to the Web server as a percent-encoded dictionary
        """
        try:
            payload = self.formatter.format(record)
            if payload is None:
                return
            res = requests.post(self._post_address, json=payload, timeout=self._timeout)
            if res.status_code != 204:
                sys.stderr.write('Loki occurs errors\n')
        except requests.exceptions.ReadTimeout:
            sys.stderr.write('Loki connect time out\n')
        except Exception:
            sys.stderr.write(f'{record.getMessage()}\n')

    def setFormatter(self, fmt: LokiFormatter) -> None:
        fmt.tz = self._tz
        fmt.source = self._source
        fmt.src_host = self._src_host
        self.formatter = fmt
