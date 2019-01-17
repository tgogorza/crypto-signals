import json
import requests
import time
import config
import logging

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)


class SignalReader():
    def __init__(self):
        self.api_key = ''
        self.url = ''
        self.enabled = True

    def parse(self, signal):
        raise NotImplementedError()

    def start_reader(self, exchange='', interval=5, signal_queue=None):
        if exchange and signal_queue:
            print('Started CryptSignal reader for {}'.format(exchange))
            while self.enabled: 
                try:
                    signals = self.query_signal(exchange, interval)
                    if signals:
                        print('Signal received...')
                        logging.info('Reading cryptoqualitysignals.com:\n{}'.format(signals))
                        [signal_queue.put(signal) for signal in signals]
                        # if signals['count'] > 0:
                        #    print signals
                        # else:
                        #    print 'No new signals at this time, waiting 5 minutes...'
                except Exception as e:
                    logging.error('Failed retrieving signal:\n{}'.format(e.message))
                finally:
                    time.sleep(301)
                    #time.sleep(10)

    def query_signal(self, exchange, interval):
        params = {'api_key': self.api_key, 'exchange': exchange, 'interval': interval}
        signals = json.loads(requests.get(self.url, params=params).text)
        return self.parse(signals)

    def stop_reader(self):
        self.enabled = False


class CryptoSignalsReader(SignalReader):
    def __init__(self):
        SignalReader.__init__(self)
        self.api_key = config.CRYPTO_SIGNALS_API_KEY
        self.url = config.CRYPTO_SIGNALS_API
        
    def parse(self, signal):
        # print('Parsing Signal:\n{}'.format(signal))
        signals = signal['signals']
        return signals
