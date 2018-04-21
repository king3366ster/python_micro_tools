
- loadData 设计可以自由组装替换，获取股票、比特币等交易
- Account 为交易类
  - 初始化类: ua = BaseAccount(current_date='2017-05-01')
  - 设置比较基准，同时可以依此获取交易基准时间： ua.set_benchmark('600000')
  - 设置买卖手续费：ua.set_order_cost(0.0003, 0.0013)
  - 设置最小交易额度：ua.set_min_mount(100)
  - 进入下一天：ua.turn_next_date()
  - 按金额买卖：ua.order_value('601360', 10000, order_type='buy')
  - 按份额买卖：ua.order_target('601360', 1000, order_type='buy')
  - 全仓买卖：ua.order_all('601360', order_type='buy')

- AccountExt 为扩展交易类
  - 扩展自定义的指标参数，用于买卖交易