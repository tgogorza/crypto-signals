import config
import requests
import json
import logging
from three_commas_helper import create_headers, get_accounts
from BinanceOperator import BinanceOperator

logging.basicConfig(filename=config.LOGGING_FILE, level=logging.INFO)


class OrderCreator:
    def __init__(self):
        self.api_key = ''
        self.api_secret = ''

    def place_order(self, order_info, base_amount):
        raise NotImplementedError()


class ThreeCommasOrderCreator(OrderCreator):
    def __init__(self):
        OrderCreator.__init__(self)
        self.api_key = config.THREE_COMMAS_API_KEY
        self.api_secret = config.THREE_COMMAS_API_SECRET
        self.max_stop_loss = config.MAX_STOP_LOSS
        self.risk_reward_ratio = config.DEFAULT_RISK_REWARD_RATIO
        self.base_url = 'https://3commas.io'

    def place_order(self, order_info, base_amount, target_level=2):
        try:
            order_endpoint = '/public/api/ver1/smart_trades/create_smart_trade'
            url = '{}{}'.format(self.base_url, order_endpoint)
            
            accounts = get_accounts(self.api_key, self.api_secret)
            account = accounts[order_info['exchange']]

            if target_level not in (1, 2, 3):
                target_level = 1

            units_to_buy = round(float(base_amount) / float(order_info['ask']), 0)
            if units_to_buy > 0.0:
                #for i in range(1, target_level+1):
                # target = 'target{}'.format(i)
                target = 'target{}'.format(target_level)
                current_price = float(order_info['ask'])
                # If signal has no stop-loss, calculate it (default risk-reward ratio defined in config file)
                if 'stop_loss' in order_info and float(order_info['stop_loss']) > 0.0:
                    stop_loss = float(order_info['stop_loss'])
                else:
                    stop_loss = self.calculate_stop_loss(current_price,
                                                         float(order_info[target]),
                                                         risk_ratio=self.risk_reward_ratio)
                if self.max_stop_loss:
                    stop_loss_cap = current_price - (current_price * abs(self.max_stop_loss))
                    stop_loss = max(stop_loss, stop_loss_cap)

                if target in order_info.keys():
                    params = {
                        'api_key': self.api_key,
                        'secret': self.api_secret,
                        'account_id': account,
                        'pair': '{}_{}'.format(order_info['currency'], order_info['coin']),
                        'units_to_buy': units_to_buy,
                        'buy_price': current_price,
                        'take_profit_enabled': True,
                        'take_profit_type': 'classic', # classic / step_sell
                        'take_profit_price_condition': float(order_info[target]),    # if classic
                        # 'take_profit_step_orders': [],  # if step_sell ->  [{percent: 50, price: 100, price_method: bid,ask,last}, ...]
                        'trailing_take_profit': True,
                        'trailing_take_profit_step': 0.01,
                        'stop_loss_enabled': True,
                        'stop_loss_price_condition': stop_loss,
                        'trailing_stop_loss': True,
                        #'note': '' #order_info
                    }
                    self.execute_order(order_endpoint, order_info, params, url)
        except Exception as e:
            raise ValueError('Failed creating order for {}:\n{}'.format(order_info['coin'], e.args))

    def execute_order(self, order_endpoint, order_info, params, url):
        pairs = zip(params.keys(), params.values())
        pairs = ['{}={}'.format(p[0], p[1]) for p in pairs]
        paramstr = '&'.join(pairs)
        headers = create_headers('{}?{}'.format(order_endpoint, paramstr), self.api_key, self.api_secret)
        response = requests.post(url=url, data=params, headers=headers)
        response = json.loads(response.text)
        if 'error' not in response:
            print('Created Order for {} in {}'.format(params['pair'], order_info['exchange']))
            logging.info('CREATED ORDER:\n{}\n'.format(params))
            logging.info('ORDER:\n{}'.format(response))
        else:
            logging.info('FAILED CREATING ORDER:\n{}'.format(response))

    def calculate_stop_loss(self, price, target, risk_ratio=1.0/2):
        target_profit = float(target - price) / price
        stop_loss = price - (price * target_profit * risk_ratio)
        return stop_loss


class BinanceOrderCreator:
    def __init__(self):
        self.operator = BinanceOperator(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)

    def place_order(self, order_info, base_amount=0):
        try:
            response = {}
            symbol = order_info['symbol']
            if order_info['action'] == 'long' and self.operator.buying_allowed(symbol):
                response = self.operator.create_market_buy(symbol, base_amount)
            elif order_info['action'] == 'short' and self.operator.selling_allowed(symbol):
                response = self.operator.create_market_sell(symbol)
            else:
                response['error'] = '{} action not allowed right now for {}'.format(order_info['action'], symbol)
            if 'error' not in response:
                print('Created Order for {} in {}'.format(order_info['symbol'], order_info['exchange']))
                logging.info('CREATED ORDER:\n{}\n'.format(order_info))
                logging.info('ORDER:\n{}'.format(response))
            else:
                logging.info('FAILED CREATING ORDER:\n{}'.format(response))
        except Exception as e:
            raise ValueError('Failed creating order for {}:\n{}'.format(order_info['symbol'], e.message))
