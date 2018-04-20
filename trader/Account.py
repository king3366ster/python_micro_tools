# -*- coding:utf-8 -*-
import pandas as pd
import tushare as ts
import os

path_prefix = u'./data/'

# 账户上下文
class Context:
    portfolio = {}

# 证券基本信息
class Portfolio:
    def __init__(self, amount=0, price=0):
        self.amount = amount
        # 成本价
        self.cost_price = price
        self.market_value = self.amount * self.cost_price
    
    def add_share(self, amount=0, price=0):
        if (amount + self.amount) < 0:
            amount = -self.amount
        if self.amount + amount == 0:
            self.market_value = 0
            self.cost_price = 0
            self.amount = 0
        else:
            self.market_value += amount * price
            self.cost_price = (self.amount * self.cost_price + amount * price) / (self.amount + amount)
            self.amount = self.amount + amount
    
    def get_share(self):
        return self
    

class BaseAccount:
    def __init__(self, cash=100000, current_date=None):
        self.cash = cash
        self.current_date = current_date
        self.order_cost_buy = 0,0003
        self.order_cost_sell = 0.0013
        self.security_cache = {}
        self.set_order_cost(0, 0)
        self.set_slippage(0)
        self.benchmark_data = None
        # 最小成交金额
        self.min_deal_amount = 100
        self.context = Context()

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
        self.current_date = self.get_curr_date()
    
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

    def turn_next_date(self):
        next_date = self.get_next_date()
        self.current_date = next_date

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
    def order_target(self, security, amount=0, side='long', order_type='buy', order_date='close'):
        security_info = self.get_current_price(security)
        if security_info is None:
            return
        price = security_info[order_date]
        if order_type == 'buy':
            max_amount = int(self.cash / (price * self.min_deal_amount *  (1 + self.order_cost_buy))) * self.min_deal_amount
            amount = min(amount, max_amount)
            if security not in self.context.portfolio:
                self.context.portfolio[security] = Portfolio(amount=amount, price=price)
            else:
                self.context.portfolio[security].add_share(amount=amount, price=price)
            self.cash = self.cash - amount * price * (1 + self.order_cost_buy)
        elif order_type == 'sell':
            if security not in self.context.portfolio:
                amount = 0
            else:
                max_amount = self.context.portfolio[security].get_share().amount
                amount = min(amount, max_amount)
                self.context.portfolio[security].add_share(amount=-amount, price=price)
            self.cash += price * amount * (1 - self.order_cost_sell)

    # 按市价下单
    def order_value(self, security, value=0, side='long', order_type='buy', order_date='close'):
        security_info = self.get_current_price(security)
        if security_info is None:
            return
        price = security_info[order_date]
        if order_type == 'buy':
            value = min(value, self.cash)
            amount = int(value / (price * self.min_deal_amount *  (1 + self.order_cost_buy))) * self.min_deal_amount
            if security not in self.context.portfolio:
                self.context.portfolio[security] = Portfolio(amount=amount, price=price)
            else:
                self.context.portfolio[security].add_share(amount=amount, price=price)
            self.cash = self.cash - amount * price * (1 + self.order_cost_buy)
        elif order_type == 'sell':
            if security not in self.context.portfolio:
                amount = 0
            else:
                portfolio_amount = self.context.portfolio[security].get_share().amount
                amount = min(portfolio_amount, int(value / (price * self.min_deal_amount)) * self.min_deal_amount)
                self.context.portfolio[security].add_share(amount=-amount, price=price)
            self.cash += price * amount * (1 - self.order_cost_sell)

    def order_all(self, security, order_type='buy', order_date='close'):
        if order_type == 'buy':
            self.order_value(security, value=self.cash)
        elif order_type == 'sell':
            if security not in self.context.portfolio:
                amount = 0
            else:
                amount = self.context.portfolio[security].get_share().amount
            self.order_target(security, amount=amount, order_type='sell', order_date='close')
    
    def get_market_value(self):
        market_value = self.cash
        for security in self.context.portfolio:
            portfolio = self.context.portfolio[security].get_share()
            security_info = self.get_current_price(security)
            market_value += portfolio.amount * security_info['close'] * (1 - self.order_cost_sell)
        return market_value

def main():
    ua = BaseAccount(current_date='2017-05-01')
    ua.set_benchmark('600000')
    # print ua.get_curr_date()
    # print ua.get_prev_date()
    # print ua.get_next_date()
    # print ua.get_current_price('601360')
    print ua.get_curr_date()
    ua.order_value('601360', 10000, order_type='buy')
    print ua.get_market_value()
    ua.turn_next_date()
    # ua.order_target('601360', 1000, order_type='buy')
    ua.order_all('601360', order_type='buy')
    print ua.get_market_value()
    ua.turn_next_date()
    print ua.get_market_value()
    ua.turn_next_date()
    print ua.get_market_value()
    ua.turn_next_date()
    # ua.order_value('601360', 10000, order_type='sell')
    # ua.order_target('601360', 1000, order_type='sell')
    ua.order_all('601360', order_type='sell')
    print ua.get_market_value()
    ua.turn_next_date()
    print ua.get_market_value()

if __name__ == '__main__':
    main()

