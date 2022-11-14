#!/usr/bin/python3
from idlelib import browser

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import json
import easyocr
import numpy
from PIL import ImageEnhance
from PIL import Image  # 注意我的Image版本是pip3 install Pillow==4.3.0
from requests import session, post, adapters
import time
import datetime

adapters.DEFAULT_RETRIES = 5
username = 'mf22222222'  # 用户名
password = 'nicaicai'  # 密码


class Shibie:
    def __init__(self, img):
        self.img = img

    def read_captcha(self, img_byte):
        img = Image.open(img_byte).convert('L')
        enh_bri = ImageEnhance.Brightness(img)
        new_img = enh_bri.enhance(factor=1.5)
        image = numpy.array(new_img)
        reader = easyocr.Reader(['en'])
        horizontal_list, free_list = reader.detect(image, optimal_num_chars=4)
        character = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        allow_list = list(character)
        result = reader.recognize(image,
                                  allowlist=allow_list,
                                  horizontal_list=horizontal_list[0],
                                  free_list=free_list[0],
                                  detail=0)
        if len(result) == 0:
            return "0"
        else:
            return result[0]

    def validate_code(self):
        return self.read_captcha(self.img)


def get_data(JCRQ: str):
    old = datetime.datetime.strptime(JCRQ, "%Y-%m-%d %H")
    new = old + datetime.timedelta(days=2)
    now = datetime.datetime.now()
    if now > new:
        return new.strftime("%Y-%m-%d+%H")
    else:
        return old.strftime("%Y-%m-%d+%H")


def fillOneForm(wid, JCRQ, CURR_LOCATION, cookies):
    info = 'WID=' + wid
    info += '&CURR_LOCATION=' + CURR_LOCATION
    info += '&IS_TWZC=1'
    info += '&IS_HAS_JKQK=1'
    info += '&JRSKMYS=1'
    info += '&JZRJRSKMYS=1'
    info += '&SFZJLN=0'
    info += '&ZJHSJCSJ=' + get_data(JCRQ)
    link = 'http://ehallapp.nju.edu.cn/xgfw/sys/yqfxmrjkdkappnju/apply/saveApplyInfos.do?'
    link += info
    payload = {}
    headers = {
        'host': 'ehallapp.nju.edu.cn',
        'proxy-connection': 'keep-alive',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; LYA-AL00 Build/HUAWEILYA-AL00L; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.93 Mobile Safari/537.36 cpdaily/9.0.15 wisedu/9.0.15',
        'x-requested-with': 'com.wisedu.cpdaily.nju',
        'referer': 'http://ehallapp.nju.edu.cn/xgfw/sys/mrjkdkappnju/index.html',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': cookies
    }
    response = requests.request("GET", link, headers=headers, data=payload)
    res = json.loads(response.text)
    if res['code'] == '0':
        if res['msg'] == '成功':
            return 'Success!'
    return 'Failed.'


def fillTheForms(res, cookies):
    JCRQ = res[1]['ZJHSJCSJ']
    CURR_LOCATION = res[1]['CURR_LOCATION']
    form = res[0]
    print('Date: ' + form['TBRQ'] + '  ' + fillOneForm(wid=form['WID'], JCRQ=JCRQ, CURR_LOCATION=CURR_LOCATION,
                                                       cookies=cookies))


def DriverConfig():
    options = webdriver.ChromeOptions()
    options.binary_location="/opt/google/chrome/google-chrome"
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('blink-settings=imagesEnabled=true')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options)
    return driver


def LogIn(driver):
    driver.get('https://authserver.nju.edu.cn/authserver/login')
    time.sleep(2)
    while True:
        try:
            element = WebDriverWait(browser, 1).until(EC.presence_of_element_located((By.ID, "username")))
        finally:
            break
    driver.find_element_by_class_name("showPass").click()
    time.sleep(2)
    print("ok")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    ss = soup.find("img", {"id": "captchaImg"})
    if ss == None:
        return
    trynum = 0
    # 需要验证码时
    picurl = "code.png"
    driver.find_element(by=By.ID, value="captchaImg").screenshot(picurl)
    shibie = Shibie(img=picurl)
    captchaResponse = shibie.validate_code()
    print(captchaResponse)
    while trynum < 100:
        driver.find_element(by=By.ID, value="password").send_keys(password)
        driver.find_element(by=By.ID, value="username").send_keys(username)
        driver.find_element(by=By.ID, value="captchaResponse").send_keys(captchaResponse)
        driver.find_element(by=By.CLASS_NAME, value="auth_login_btn").click()
        driver.get('https://authserver.nju.edu.cn/authserver/login')
        time.sleep(1)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        ss = soup.find("img", {"id": "captchaImg"})
        if ss == None:
            break
        else:
            driver.find_element_by_class_name("showPass").click()
            time.sleep(1)
            driver.find_element(by=By.ID, value="captchaImg").screenshot("code.png")
            shibie = Shibie(img=picurl)
            captchaResponse = shibie.validate_code()
            trynum += 1
    if trynum >= 100:
        print("失败")


def GetList(cookies):
    url = "http://ehallapp.nju.edu.cn/xgfw//sys/yqfxmrjkdkappnju/apply/getApplyInfoList.do"
    payload = {}
    headers = {
        'host': 'ehallapp.nju.edu.cn',
        'proxy-connection': 'keep-alive',
        'accept': 'application/json, text/plain, */*',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; LYA-AL00 Build/HUAWEILYA-AL00L; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.93 Mobile Safari/537.36 cpdaily/9.0.15 wisedu/9.0.15',
        'x-requested-with': 'com.wisedu.cpdaily.nju',
        'referer': 'http://ehallapp.nju.edu.cn/xgfw/sys/mrjkdkappnju/index.html',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': cookies
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response


def GetCookie(driver):
    url = "https://ehallapp.nju.edu.cn/xgfw/sys/mrjkdkappnju/index.do"
    driver.get(url)
    time.sleep(2)
    cookiecontent = ''
    cookies = driver.get_cookies()
    for cookie in cookies:
        cookiecontent += cookie['name'] + '='
        cookiecontent += cookie['value'] + ';'
    return cookiecontent


def SubMit(response, cookies):
    res = json.loads(response.text)
    if res['code'] == '0':
        if res['msg'] == '成功':
            fillTheForms(res['data'], cookies)
    print('Completed')
    driver.quit()


if __name__ == '__main__':
    driver = DriverConfig()
    LogIn(driver)
    cookies = GetCookie(driver)
    response = GetList(cookies)
    SubMit(response, cookies)
