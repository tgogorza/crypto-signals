import json
import requests
import time
import config
import logging
import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import smtplib
import time
import imaplib
import email


# from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)


class SignalReader:
    def __init__(self):
        self.api_key = ''
        self.url = ''
        self.enabled = True
        self.name = ''

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
                        logging.info('Reading {}:\n{}'.format(self.name, signals))
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

    def query_signal(self, exchange, interval=None):
        pass

    def stop_reader(self):
        self.enabled = False


class CryptoSignalsReader(SignalReader):
    def __init__(self):
        SignalReader.__init__(self)
        self.api_key = config.CRYPTO_SIGNALS_API_KEY
        self.url = config.CRYPTO_SIGNALS_API
        self.name = 'CryptoQualitySignals'

    def query_signal(self, exchange, interval=None):
        params = {'api_key': self.api_key, 'exchange': exchange, 'interval': interval}
        signals = json.loads(requests.get(self.url, params=params).text)
        return self.parse(signals)

    def parse(self, signal):
        # print('Parsing Signal:\n{}'.format(signal))
        signals = signal['signals']
        return signals


class GmailSignalReader(SignalReader):
    def __init__(self):
        SignalReader.__init__(self)
        self.url = 'https://www.googleapis.com/auth/gmail.readonly'
        self.creds = self.get_credentials()
        self.service = build('gmail', 'v1', credentials=self.creds)
        self.name = 'Gmail Signals'

    def query_signal(self, exchange, interval=None):

        results = self.service.users().messages()\
            .list(userId='me', q='subject:(tradingview alert), newer_than:1d, is:unread ').execute()['messages']
        message_id = results[0]['id']
        message = self.service.users().messages().get(userId='me', id=message_id).execute()
        # MARK MESSAGE AS READ
        self.service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
        signal = self.parse(message['snippet'])
        return [signal]

    def parse(self, signal):
        """
        This function assumes signal with format: i.e. "long btc/usd", "short eth/btc", etc.
        :param signal:
        :return: parsed signal dictionary
        """
        signal = signal.split
        parsed = {
            'action': signal[5],
            'pair': signal[6],
            'target': signal[6].split('/')[0],
            'base': signal[6].split('/')[1],
        }
        return parsed

    def get_credentials(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', [self.url])
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        return creds
