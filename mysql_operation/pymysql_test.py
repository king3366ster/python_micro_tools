# -*- coding: utf-8 -*-

import pymysql

# 创建连接
conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    passwd='',
    db='wordpress',
    charset='utf8'
)

# 创建游标
cursor = conn.cursor()
  
# 执行SQL，并返回收影响行数
effect_row = cursor.execute('select * from wsw_404_log limit 5;')
print effect_row

# 获取剩余结果的第一行数据
row_1 = cursor.fetchone()
print row_1

# 获取剩余结果前n行数据
row_2 = cursor.fetchmany(3)
print row_2

# 移动游标
# cursor.scroll(1, mode='relative')  # 相对当前位置移动
cursor.scroll(0, mode='absolute')  # 相对绝对位置移动
# 获取剩余结果所有数据
row_3 = cursor.fetchall()
print row_3

# 执行SQL，并返回受影响行数
effect_row = cursor.execute(
    'update wsw_404_log set ua = "%s" where id = %d' % ('111',1))
  
# 执行SQL，并返回受影响行数,执行多次
effect_row = cursor.executemany("insert into wsw_404_log (ref, url, ip, ua)values(%s,%s,%s,%s)", [
                                ("u1", "u1pass", "11111", "123"), ("u2", "u2pass", "22222", "456")])

# 提交，不然无法保存新建或者修改的数据
conn.commit()


# 关闭游标
cursor.close()
# 关闭连接
conn.close()
