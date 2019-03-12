from binance.client import Client
import logging
import requests
import json
import math


class BinanceOperator:

    def __init__(self, api_key, secret):
        self.client = Client(api_key, secret)
        self.symbol_status = {}
        # self.base_url = 'https://api.binance.com'

    # def get_open_orders(self):
    #     endpoint = '/api/v3/openOrders'
    #     ts = int(time.time()*1000)
    #     symbol = 'LTCBTC'
    #     query = urlencode({'symbol': symbol, 'timestamp': ts})
    #     signature = hmac.new(self.api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    #     params = {
    #         'symbol': symbol,
    #         'timestamp': ts,
    #         'signature': signature,
    #     }
    #     header = {'X-MBX-APIKEY': self.api_key}
    #     url = self.base_url + endpoint
    #     response = requests.get(url, headers=header, params=params)
    #     orders = json.loads(response.text)
    #     return orders

    # def create_order(self, order):
    #     endpoint = '/api/v3/order/test'
    #     ts = int(time.time()*1000)
    #     symbol = 'LTCBTC'
    #     query = urlencode({'symbol': symbol, 'timestamp': ts})
    #     signature = hmac.new(self.api_secret.encode('utf-8'), query.encode('utf-8'), hashlib.sha256).hexdigest()
    #     params = {
    #         'symbol': symbol,
    #         'timestamp': ts,
    #         'signature': signature,
    #     }
    #     header = {'X-MBX-APIKEY': self.api_key}
    #     url = self.base_url + endpoint
    #     response = requests.post(url, headers=header, params=params)
    #     orders = json.loads(response.text)
    #     return orders

    def create_market_buy(self, symbol, total):
        price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
        qty = self.estimate_quantity(symbol, total, price)
        response = self.client.order_market_buy(symbol=symbol, quantity=qty)
        self.symbol_status[symbol] = {
            'status': 'long',
            'quantity': qty,
            'price': price
        }
        return response

    def create_market_sell(self, symbol):
        last_order = list(filter(lambda o: o['side'] == 'BUY', self.client.get_all_orders(symbol=symbol)))[-1]
        qty = last_order['executedQty']
        buy_price = float(last_order['cummulativeQuoteQty'])

        response = self.client.order_market_sell(symbol=symbol, quantity=qty)

        # DO PnL estimation and save it
        if response['status'] == 'FILLED':
            sell_price = float(response['cummulativeQuoteQty'])
            profit = round((sell_price - buy_price) / buy_price, 4)
            logging.info('SOLD {}: {} @ {} - Profit: {}%\n'.format(symbol, qty, sell_price, profit*10))
            self.symbol_status[symbol] = {
                'status': 'short',
                'quantity': qty,
                'price': sell_price
            }
        return response

    def estimate_quantity(self, symbol, total, current_price):
        info = requests.get('https://www.binance.com/api/v1/exchangeInfo')
        data = json.loads(info.text)
        sym = list(filter(lambda x: x['symbol'] == symbol, data['symbols']))[0]
        lot_info = list(filter(lambda x: x['filterType'] == 'LOT_SIZE', sym['filters']))[0]

        min_qty = float(lot_info['minQty'])
        max_qty = float(lot_info['maxQty'])
        step_size = lot_info['stepSize']
        qty = round(total / current_price, 8)
        if qty >= min_qty:
            approximator = step_size.find('1') - 1
            qty = math.floor(qty * 10 ** approximator) / float(10 ** approximator)
            return qty
        elif qty > max_qty:
            return max_qty
        else:
            return 0

    def buying_allowed(self, symbol):
        # If symbol not traded yet, add to the symbol status dictionary
        if symbol not in self.symbol_status:
            self.symbol_status[symbol] = {
                'status': 'short',
                'quantity': 0,
                'price': 0
            }
        return True if self.symbol_status[symbol]['status'] == 'short' else False

    # COULD ALSO CHECK THAT QUANTITY IS SAME AS LAST BUY (?)
    def selling_allowed(self, symbol):
        return True if symbol in self.symbol_status and self.symbol_status[symbol]['status'] == 'long' else False