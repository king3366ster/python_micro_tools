# -*- coding:utf-8 -*-
import pandas as pd
import tushare as ts
import os

path_prefix = u'./data/'


class BaseAccount:
    def __init__(self, cash=10000, current_date=None):
        self.security_cache = {}
        self.set_order_cost(0, 0)
        self.set_slippage(0)
        # 最小成交金额
        self.min_deal_amount = 100
        self.current_date = current_date
        self.benchmark_data = None

    def _read_data(self, security):
        if security in self.security_cache:
            return self.security_cache[security]
        data_path = u'%s%s.csv' % (path_prefix, security)
        if os.path.exists(data_path):
            result = pd.read_csv(data_path)
        else:
            df = ts.get_k_data(security, index=False, start='2017-01-01')
            df.to_csv(data_path)
            self.security_cache[security] = df
            result = df
        result.sort_values(by='date', ascending=True, inplace=True)
        self.security_cache[security] = result
        return result

    # 设置基准证券
    def set_benchmark(self, security):
        self.benchmark_data = self._read_data(security)
        self.benchmark_data.sort_values(by='date', ascending=True, inplace=True)
    
    # 获取上一交易日
    def get_prev_date(self):
        if self.benchmark_data.empty:
            raise 'benchmark has not been set'
        df = self.benchmark_data[self.benchmark_data['date']<self.current_date]
        return df.iloc[-1].date

    def get_curr_date(self):
        if self.benchmark_data.empty:
            raise 'benchmark has not been set'
        df = self.benchmark_data[self.benchmark_data['date']>=self.current_date]
        self.current_date = df.iloc[0].date
        return self.current_date

    # 获取下一交易日
    def get_next_date(self):
        if self.benchmark_data.empty:
            raise 'benchmark has not been set'
        df = self.benchmark_data[self.benchmark_data['date']>self.current_date]
        return df.iloc[0].date

    # 设置买卖手续费
    def set_order_cost(self, order_cost_buy, order_cost_sell):
        self.order_cost_buy = order_cost_buy
        self.order_cost_sell = order_cost_sell

    # 设置滑点
    def set_slippage(self, slippage):
        self.slippage = slippage

    def get_price(self, security, start_date=None, end_date=None, frequency='daily'):
        pass

    def get_current_price(self, security):
        if security not in self.security_cache:
            self.security_cache[security] = self._read_data(security)
        result = self.security_cache[security]
        df = result[result['date']<=self.current_date]
        if df.empty:
            return None
        else:
            return df.iloc[-1].to_dict()

    # 按目标股数下单 side long: 多单, short: 空单
    def order_target(self, security, amount, side='long'):
        pass

    # 按市价下单
    def order_value(self, security, value, side='long', order_type='buy', order_date='close'):
        security_info = self.get_current_price(security)
        if security_info is None:
            return
        price = security_info[order_date]
        print price
    
    def get_market_value(self):
        pass

def main():
    ua = BaseAccount(current_date='2017-05-01')
    ua.set_benchmark('600000')
    # print ua.get_curr_date()
    # print ua.get_prev_date()
    # print ua.get_next_date()
    # print ua.get_current_price('601360')
    ua.order_value('601360', 10000, order_type='buy')

if __name__ == '__main__':
    main()

