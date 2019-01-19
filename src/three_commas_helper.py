import hmac
import hashlib
import requests
import json

base_url = 'https://3commas.io'


def create_headers(url, api_key, api_secret):
    signature = hmac.new(str.encode(api_secret), str.encode(url), hashlib.sha256)
    headers = {
        'APIKEY': api_key,
        'Signature': signature.hexdigest(),
        #'Content-type': 'application/json'
        #'Content-type': 'application/x-www-form-urlencoded'
    }
    return headers


def get_accounts(api_key, api_secret):
    accounts_endpoint = '/public/api/ver1/accounts'
    url = '{}{}'.format(base_url, accounts_endpoint)
    headers = create_headers(accounts_endpoint, api_key, api_secret)
    response = requests.get(url=url, headers=headers)
    response = json.loads(response.text)
    accounts = {acc['name'].lower(): acc['id'] for acc in response}
    return accounts


def get_finished_trades(api_key, api_secret, account_id=None, limit=999999):
    trades_endpoint = '/public/api/ver1/smart_trades'
    url = '{}{}'.format(base_url, trades_endpoint)
    params = {
        'api_key': api_key,
        'secret': api_secret,
        'scope': 'finished',
        'limit': limit
    }
    if account_id:
        params['account_id'] = account_id
    pairs = zip(params.keys(), params.values())
    pairs = ['{}={}'.format(p[0], p[1]) for p in pairs]
    paramstr = '&'.join(pairs)

    # params = 'account_id={}'.format(account_id)
    headers = create_headers('{}?{}'.format(trades_endpoint, paramstr), api_key, api_secret)
    # headers = create_headers(trades_endpoint, api_key, api_secret)
    response = requests.get(url=url, params=params, headers=headers)
    response = json.loads(response.text)
    return response
