CRYPTO_SIGNALS_API = 'https://cryptoqualitysignals.com/api/getSignal/'
CRYPTO_SIGNALS_API_KEY = 'FREE'
CRYPTO_SIGNALS_TARGET_LEVEL = 2     # CryptoSignals usually offers 3 different price targets (1=conservative, 3=risky)

THREE_COMMAS_API_KEY = '<YOUR_API_KEY>'
THREE_COMMAS_API_SECRET = '<YOUR_SECRET_KEY>'

BASE_ORDER_BTC = 0.0015
MAX_STOP_LOSS = 0.05    # max allowed % stop loss (i.e. 0.05 -> if stop loss price >5%, it will be set to 5%) 0=disabled
DEFAULT_RISK_REWARD_RATIO = 1.0 / 2     # if stop loss is not defined by trade, this parameter will set it 
                                        # (1.0/2 means 2:1 risk-reward ratio, 1.0/3 = 3:1, etc.)

LOGGING_FILE = 'log.txt'
