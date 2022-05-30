import _thread
from itertools import count
import os
import random
import sys
from textwrap import indent
import time
from urllib import response

import jsons
import requests

requests.packages.urllib3.disable_warnings()

from util import CommonUtil


class WechatLogin:

    def __init__(self):
        self.session = requests.session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'Referer': 'https://mp.weixin.qq.com/'
        }
        self.QRImgPath = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'QRcode.jpg'

        self.username = input("请输入用户名：")
        self.password = input("请输入密码：")
        self.token = ''

    def weixin_login(self):
        url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin"
        params = {
            'username': self.username,
            'pwd': CommonUtil.md5(self.password),
            'imgcode': '',
            'f': 'json'
        }
        response = self.session.post(url, data=params, headers=self.headers, verify=False)
        if response.status_code == 200:
            target = response.content.decode('utf-8')
            # print(target)
            self.get_weixin_login_qrcode()

    def get_weixin_login_qrcode(self):
        url = "https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=getqrcode&param=4300"
        response = self.session.get(url, headers=self.headers, verify=False)
        # target = response.content.decode('utf-8')
        # print(target)
        self.tip = 1
        with open(self.QRImgPath, 'wb') as f:
            f.write(response.content)
            f.close()
        # 打开二维码
        if sys.platform.find('darwin') >= 0:
            os.subprocess.call(['open', self.QRImgPath])  # 苹果系统
        elif sys.platform.find('linux') >= 0:
            os.subprocess.call(['xdg-open', self.QRImgPath])  # linux系统
        else:
            os.startfile(self.QRImgPath)  # windows系统
        print('请使用微信扫描二维码登录')

    def check_login(self):
        print("等待扫码登录......")
        while True:
            url = "https://mp.weixin.qq.com/cgi-bin/loginqrcode?action=ask&token=&lang=zh_CN&f=json&ajax=1"
            response = self.session.get(url, headers=self.headers, verify=False)
            json = jsons.loads(response.text)
            if json["status"] == 1:
                self.login()
                print("登录成功！")
                break
            time.sleep(5)

    def login(self):
        url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login"
        data = {
            'f': 'json',
            'ajax': 1,
            'random': random.random()
        }
        response = self.session.post(url, data=data, headers=self.headers, verify=False)
        # {"base_resp":{"err_msg":"ok","ret":0},"redirect_url":"/cgi-bin/home?t=home/index&lang=zh_CN&token=1502993366"}
        json = jsons.loads(response.text)
        redirect_url = json["redirect_url"]
        self.token = redirect_url[redirect_url.rfind("=") + 1:len(redirect_url)]
        # print("token:" + self.token)

    def checkDomain(self, domain):
        url = "https://mp.weixin.qq.com/misc/checkurl?url=http%3A%2F%2F"
        token = self.token
        url = url + domain + "&f=json&action=check&token=" + token + "&lang=zh_CN&f=json&ajax=1"
        # print(url)
        data = {
            # 'f': 'json',
            # 'action': 'check',
            # 'token': self.token,
            # 'lang': 'zh_CN',
            # 'ajax': 1,
            # 'random': random.random()
        }
        response = self.session.get(url, data=data, headers=self.headers, verify=False)

        resp = jsons.loads(response.text)

        # print(resp["base_resp"])
        return resp["base_resp"]

    def wrfile(self):
        output = open("./output.txt", "w")
        bad = open("./bad.txt", "w")
        count = 0
        with open("./input.txt", "r") as domain:
            for line in domain:
                count = count + 1
                if count % 10 == 0:
                    time.sleep(2)
                else:
                    if wechat.checkDomain(line)["ret"] == 0 and wechat.checkDomain(line)["err_msg"] == "ok":
                        output.write(line)
                    else:
                        bad.write(line)
            domain.close()
        output.close()
        bad.close()
        print("完成！！！")
        input()


if __name__ == '__main__':
    wechat = WechatLogin()
    wechat.weixin_login()
    wechat.check_login()
    wechat.wrfile()
