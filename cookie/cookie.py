# -*- coding: UTF-8 -*-
"""
datetime: 2017/11/16
by: pagewang
describe: qq auto login print cookie
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from time import sleep
import urllib2
import cv2
import numpy as np
import random
from db import InitMessages
from selenium.webdriver.common.keys import Keys
import sys
reload(sys)
sys.setdefaultencoding('utf8')

chrome_options = Options()
chrome_options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)

url1 = 'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid=501038301&target=self&s_url=http://im.qq.com/loginSuccess.html'
# url1 = 'http://im.qq.com/mobileqq/'
url2 = 'http://im.qq.com/loginSuccess.html'

mydb = InitMessages()
users = mydb.getAccounts()

successList = []
fail_count = 1

# users = None
# user = None
# username = None
# password = None
#
# with open('./testqq.txt') as f:
#     users = f.read()
#
# users = users.strip().replace('\r\n', '\n').split('\n')
#
# for i in range(len(users)):
#     user = users[i].split('----')
#     qq = user[0]
#     password = user[1]
#     users[i] = {'qq': qq, 'password': password}


def get_image_position():
    image1 = driver.find_element_by_id('slideBkg').get_attribute('src')
    image2 = driver.find_element_by_id('slideBlock').get_attribute('src')

    if image1 == None or image2 == None:
        return

    # ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:56.0) Gecko/20100101 Firefox/56.0'
    # us = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'

    content = urllib2.urlopen(image1).read()
    with open('./slide_bkg.png', 'wb') as f:
        f.write(content)
        f.close()

    content = urllib2.urlopen(image2).read()
    with open('./slide_block.png', 'wb') as f:
        f.write(content)
        f.close()

    block = cv2.imread('./slide_block.png', 0)
    template = cv2.imread('./slide_bkg.png', 0)

    cv2.imwrite('./template.jpg', template)
    cv2.imwrite('./block.jpg', block)
    block = cv2.imread('./block.jpg')
    block = cv2.cvtColor(block, cv2.COLOR_BGR2GRAY)
    block = abs(255 - block)
    cv2.imwrite('./block.jpg', block)

    block = cv2.imread('./block.jpg')
    template = cv2.imread('./template.jpg')

    result = cv2.matchTemplate(block,template,cv2.TM_CCOEFF_NORMED)
    x, y = np.unravel_index(result.argmax(),result.shape)
#    print x, y

    element = driver.find_element_by_id('tcaptcha_drag_thumb')

    ActionChains(driver).click_and_hold(on_element=element).perform()

    xoffset = int(y * 0.4 + 20)
    # track_list = getTrack(xoffset)
    #
    # for tack in track_list:
    #     ActionChains(driver).move_by_offset(xoffset=tack, yoffset=0).perform()
    #     sleep(random.randint(10, 50) / 200)
    #
    # ActionChains(driver).release(on_element=element).perform()
    ActionChains(driver).move_to_element_with_offset(to_element=element, xoffset=xoffset, yoffset=0).perform()
    sleep(1)
    ActionChains(driver).release(on_element=element).perform()
    sleep(3)


def parse_cookie(cookies, user):
#    print cookies
    skey = None
    uin = None

    for cookie in cookies:
#        print cookie
        if cookie['name'] == 'skey':
            skey = cookie['value']
        if cookie['name'] == 'uin':
            uin = cookie['value']

    f = open('./cookie.txt', 'a')
    cookie = 'skey=%s; uin=%s;\n' % (skey, uin)
    f.write(cookie)
    successList.append(user['qq'])

def getTrack(xoffset):
    pass
    list = []
    x = random.randint(1, 3)
    while xoffset - x >= 5:
        list.append(x)
        xoffset = xoffset - x
        x = random.randint(1, 3)
    for i in range(xoffset):
        list.append(1)
    return list

def login(user, tryCount):
    if tryCount == fail_count:
        mydb.updateFailedAccount(user['qq'])
        return
    driver.get(url1)
    sleep(1)
    driver.find_element_by_id('switcher_plogin').click()
    # driver.find_element_by_id('login').click()
    # driver.find_element_by_id('switcher_plogin').click()
    u = driver.find_element_by_id('u')

    if len(u.get_attribute('value')):
        u.clear()

    for s in user['qq']:
        u.send_keys(s)

    p = driver.find_element_by_id('p')
    for s in user['password']:
        p.send_keys(s)

    p.send_keys(Keys.ENTER)
    sleep(2)

    if driver.current_url == url2:
        parse_cookie(driver.get_cookies(), user)
    else:
        while True:
            if driver.current_url == url2:
                parse_cookie(driver.get_cookies(), user)
                return
            if driver.find_elements_by_css_selector('#err_m') and driver.find_element_by_id('err_m').text.encode('utf-8') == '你输入的帐号或密码不正确，请重新输入。':
                tryCount = tryCount + 1
                print('%s 被告知账号或密码不正确, 失败次数： %s' % (user['qq'], tryCount))
                login(user, tryCount)
                return

            if driver.find_elements_by_css_selector('#newVcodeArea') and driver.find_element_by_tag_name('iframe'):
                # try:
                driver.switch_to.frame(driver.find_element_by_tag_name('iframe'))
                # except:
                    # print('未知异常')

            if driver.find_elements_by_css_selector('#slideBkg'):
                get_image_position()
                driver.switch_to.default_content()
            sleep(1)


f = open('./cookie.txt', 'w')
f.close()

for i in range(len(users)):
    print(len(successList), mydb.limit)
    if len(successList) == mydb.limit:
        break
    login(users[i], 0)

mydb.updateAccounts(successList)
print 'cookie done'
driver.quit()
