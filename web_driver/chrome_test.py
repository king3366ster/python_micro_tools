# -*- coding:utf-8 -*-
# https://seleniumhq.github.io/selenium/docs/api/py/api.html
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

dc = DesiredCapabilities.CHROME
dc['loggingPrefs'] = {'browser': 'ALL'}

# Optional argument, if not specified will search path.
driver = webdriver.Chrome('./chromedriver.exe', desired_capabilities=dc)
driver.get('https://www.baidu.com/');

# find_element_by_id
# find_element_by_name
# find_element_by_xpath
# find_element_by_link_text
# find_element_by_partial_link_text
# find_element_by_tag_name
# find_element_by_class_name
# find_element_by_css_selector
search_box = driver.find_element_by_id('kw')
# clear 清除元素的内容
# send_keys 模拟按键输入
# click 点击元素
# submit 提交表单
search_box.send_keys('600000')
search_box.submit()

# res = driver.execute_script('return new Date()')

for log in driver.get_log('browser'):
    print log
time.sleep(5)  # Let the user actually see something!

driver.quit()
