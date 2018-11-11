import config
import requests
import json
import hmac
import hashlib
import logging

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)

class OrderCreator:
    def __init__(self):
        self.api_key = ''
        self.api_secret = ''

    def place_order():
        raise NotImplementedError()


class ThreeCommasOrderCreator(OrderCreator):
    def __init__(self):
        OrderCreator.__init__(self)
        self.api_key = config.THREE_COMMAS_API_KEY
        self.api_secret = config.THREE_COMMAS_API_SECRET
        self.base_url = 'https://3commas.io'

    def place_order(self, order_info, base_amount):
        create_endpoint = b'/public/api/ver1/smart_trades/create_smart_trade'
        url = '{}/{}'.format(self.base_url, create_endpoint)
        
        accounts = self.get_accounts()
        account = accounts[order_info['exchange']]
        
        # If signal has no stop-loss, calculate it (default risk-reward ratio: 2:1)
        if 'stop_loss' in order_info and float(order_info['stop_loss']) > 0.0:
            stop_loss = float(order_info['stop_loss'])
        else:
            stop_loss = self.calculate_stop_loss(float(order_info['ask']), float(order_info['target1']), risk_ratio=1.0/2)

        params = {
            'api_key': self.api_key,
            'secret': self.api_secret,
            'account_id': account,
            'pair': '{}_{}'.format(order_info['currency'], order_info['coin']),
            'units_to_buy': round(float(base_amount) / float(order_info['ask']), 0),
            'buy_price': float(order_info['ask']),
            'take_profit_enabled': True,
            'take_profit_type': 'classic', # classic / step_sell
            'take_profit_price_condition': float(order_info['target1']),    # if classic
            # 'take_profit_step_orders': [],  # if step_sell ->  [{percent: 50, price: 100, price_method: bid,ask,last}, ...]
            'trailing_take_profit': True,
            'trailing_take_profit_step': 0.01,
            'stop_loss_enabled': True,
            'stop_loss_price_condition': stop_loss,
            'trailing_stop_loss': True,
            'note': '' #order_info
        }
        pairs = zip(params.keys(), params.values())
        pairs = ['{}={}'.format(p[0], p[1]) for p in pairs]
        paramstr = '&'.join(pairs)
        headers = self.create_headers('{}?{}'.format(create_endpoint, paramstr))
        response = requests.post(url=url, params=params, headers=headers)
        response = json.loads(response.text)
        print('Created Order for {} in {}'.format(params['pair'], order_info['exchange']))
        logging.info('CREATING ORDER:\n{}'.format(params))
        logging.info('ORDER:\n{}'.format(response))
        
    def calculate_stop_loss(self, price, target, risk_ratio=1.0/2):
        target_profit = float(target - price) / price
        stop_loss = price - (price * target_profit)
        return stop_loss

    def get_accounts(self):
        accounts_endpoint = b'/public/api/ver1/accounts'
        url = '{}{}'.format(self.base_url, accounts_endpoint)        
        headers = self.create_headers(accounts_endpoint)
        response = requests.get(url=url, headers=headers)
        response = json.loads(response.text)
        accounts = {acc['name'].lower(): acc['id'] for acc in response}
        return accounts

    def create_headers(self, url):
        signature = hmac.new(self.api_secret, url, hashlib.sha256)
        headers = {
            'APIKEY': self.api_key,
            'Signature': signature.hexdigest()
            }
        return headers



        

