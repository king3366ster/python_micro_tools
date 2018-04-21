# -*- coding:utf-8 -*-
import tushare as ts
import pandas as pd
import os
path_prefix = u'./data/'

def load_data (security):
    data_path = u'%s%s.csv' % (path_prefix, security)
    if os.path.exists(data_path):
        result = pd.read_csv(data_path)
    else:
        print 2222
        df = ts.get_k_data(security, index=False, start='2017-01-01')
        df.to_csv(data_path)
        result = df
    result.sort_values(by='date', ascending=True, inplace=True)
    return result
