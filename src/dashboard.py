import pandas as pd
from datetime import date, datetime
import seaborn as sns
from three_commas_helper import get_trades
import config

pd.set_option('display.width', 1200)
pd.set_option('max.columns', 1200)

# trades = pd.read_excel('SmartTrades.xlsx')
trades_data = get_trades(api_key=config.THREE_COMMAS_API_KEY, api_secret=config.THREE_COMMAS_API_SECRET)
trades = pd.DataFrame(trades_data)[['id', 'account_id', 'account_name', 'units_to_buy', 'total', 'average_buy_price',
                                    'average_sell_price', 'current_price', 'closed_at', 'created_at', 'profit_percentage',
                                    'from_currency_code', 'to_currency_code', 'status',
                                    'smart_trade_steps', 'stop_loss_price_condition', 'stop_loss_sell_order_price',
                                    'take_profit_price_condition', 'take_profit_sell_order_price', 'take_profit_steps',
                                    'trailing_stop_loss_last_price', 'trailing_stop_loss_last_price_updated_at',
                                    'trailing_take_profit_last_price', 'trailing_take_profit_last_price_updated_at',
                                    'trailing_take_profit_step', 'updated_at']]

for col in ['units_to_buy', 'total', 'average_buy_price', 'average_sell_price', 'current_price', 'profit_percentage']:
    trades[col] = trades[col].astype(float)

# Convert datetimes to just dates
trades['created_at'] = pd.to_datetime(trades['created_at']).dt.date
trades['closed_at'] = pd.to_datetime(trades['closed_at']).dt.date

finished_trades = trades[trades['status'].str.find('finished') != -1]
open_trades = trades[trades['status'] == 'bought']

# trades = trades[trades['Date closed'] > '2018-11-10']
finished_trades = finished_trades[finished_trades['closed_at'] > date(2019, 1, 1)]
finished_trades['profit'] = finished_trades['total'] * (finished_trades['profit_percentage'] / 100)
finished_trades['cum_profit'] = finished_trades['profit'].cumsum()

daily_avg = finished_trades.groupby('closed_at').mean()
#daily_avg['Date closed'] = daily_avg['Date closed'].astype('datetime64')
daily_avg['MadeProfit'] = daily_avg['Profit %'] > 0
daily_avg['CumMadeProfit'] = daily_avg['MadeProfit'].cumsum()
daily_avg['DayCount'] = list(range(1, daily_avg.shape[0]+1))
daily_avg['CumSuccessRate'] = daily_avg['CumMadeProfit'] / daily_avg['DayCount']
print('Daily Sucess: {}', daily_avg.MadeProfit.sum() / daily_avg.shape[0])

daily_avg['Profit %'].plot()


