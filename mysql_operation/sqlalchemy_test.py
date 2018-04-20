# -*- coding: utf-8 -*-
# http://docs.sqlalchemy.org/en/latest/core/type_basics.html
import sqlalchemy as sqa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()

# 定义User对象:
class LogTable(Base):
    # 表的名字:
    __tablename__ = 'wsw_404_log'
    # 表的结构:
    id = sqa.Column(sqa.Integer, primary_key=True)
    date = sqa.Column(sqa.String(40))
    ref = sqa.Column(sqa.String(512))
    url = sqa.Column(sqa.String(512))
    ip = sqa.Column(sqa.String(40))
    ua = sqa.Column(sqa.String(512))


# 初始化数据库连接:
engine = sqa.create_engine(
    'mysql://root:@localhost:3306/wordpress')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)

# 创建session对象:
session = DBSession()
# 创建新User对象:
# new_log = LogTable(date='Bob', ref='222', url='321', ip='10.10.0.21', ua='12')
# # 添加到session:
# session.add(new_log)
# # 提交即保存到数据库:
# session.commit()

# 创建Query查询，filter是where条件，最后调用one()返回唯一行，如果调用all()则返回所有行:
# log = session.query(LogTable).filter(LogTable.id == '5').one()
# print log.__dict__
logs = session.query(LogTable).order_by(sqa.desc(LogTable.id)).all()
print logs[0].__dict__

# session.delete(logs[0])
session.query(LogTable).filter(LogTable.id == 1).update({
    LogTable.ua: 'user  # 5'
})
session.commit()
# 关闭session:
session.close()
