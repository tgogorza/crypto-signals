import json
import requests
import time
import config
import logging

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)

class SignalReader:
    def __init__(self):
        self.api_key = ''
        self.url = ''

    def parse_signal(self, signal):
        raise NotImplementedError()

    def start_reader(self, exchange='', interval=5, signal_queue=None):
        if exchange:
            print('Started CryptSignal reader for {}'.format(exchange))
            params = { 'api_key': self.api_key, 'exchange': exchange, 'interval': interval }
            while True:                
                signals = json.loads(requests.get(self.url, params=params).text)
                signals = self.parse(signals)
                if signals:
                    print('Signal received...')
                    logging.info('Reading cryptoqualitysignals.com:\n{}'.format(signals))
                    [signal_queue.put(signal) for signal in signals]
                #if signals['count'] > 0:
                #    print signals
                #else:
                #    print 'No new signals at this time, waiting 5 minutes...'
                time.sleep(301)
    
class CryptoSignalsReader(SignalReader):
    def __init__(self):
        SignalReader.__init__(self)
        self.api_key = config.CRYPTO_SIGNALS_API_KEY
        self.url = config.CRYPTO_SIGNALS_API
        
    def parse(self, signal):
        # print('Parsing Signal:\n{}'.format(signal))
        signals = signal['signals']
        return signals
