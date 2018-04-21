# -*- coding:utf-8 -*-

import os
import pandas as pd

from Account import AccountBase

class AccountExt(AccountBase):
    def __init__(self, cash=100000, current_date=None):
        AccountBase.__init__(self, cash=cash, current_date=current_date)
    
    def get_ma5(self, security):
        df = self._read_data(security)
        if 'ma5' not in df:
            print 111
            roll = df.rolling(window=5)
            df_mean = roll['close'].mean()
            df.insert(len(df.columns), 'ma5', df_mean)
        return df[df['date']<=self.current_date].iloc[-1]['ma5']

def main():
    ua = AccountExt(cash=1000000, current_date='2017-05-01')
    ua.set_benchmark('600000')
    ua.set_order_cost(0.0003, 0.0013)
    ua.set_min_mount(100)

    stock_code = '601360'
    for i in range(0, 50):
        print i, ':', ua.get_curr_date()
        ma5 = ua.get_ma5(stock_code)
        close = ua.get_current_price(stock_code)['close']
        if close > ma5 * 1.00:
            ua.order_all(stock_code, order_type='buy')
        elif close < ma5 * 1.00:
            ua.order_all(stock_code, order_type='sell')
        market_value = ua.get_market_value()
        print market_value
        ua.turn_next_date()      

if __name__ == '__main__':
    main()

