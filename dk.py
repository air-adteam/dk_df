import requests
from lxml import etree
import re
import json
import os
import pickle
import time

class casService(object):
    def __init__(self,svr_session):
        self.cas_url = "https://ehall.hljeu.edu.cn/cas/login?service=https%3A%2F%2Fehall.hljeu.edu.cn%2F"
        self.svr_session = svr_session  #service_session
        self.session = requests.session() #cas session
        self.load_cascookies_from_file() #使用已有的cas-cookie(如果有的话)
        self.headers = {
              "Accept": "text/html, application/xhtml+xml, application/xml; q=0.9, */*; q=0.8",
              "Accept-Language": "zh_CN",
              "Connection": "keep-alive",
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363",
             }
    def Login(self,serviceUrl = "",username = None,password = None):
        response = self.svr_session.get(url=serviceUrl,allow_redirects=False)
        if response.status_code == 200:
            return True
        self.cas_url = response.headers["location"]
        cas_response = self.session.get(self.cas_url,allow_redirects = False)
        if cas_response.status_code == 200:#登录界面
            if username == None or password == None:
                print("cas_cookie not valid")
                username = input("plase input username:")
                password = input("plase input password:")
            loginhtml = etree.HTML(cas_response.text)
            execution_value = loginhtml.xpath("//form[@id='fm1']/input[@name='execution']/@value")
            auth_data =  {
                "_eventId" : "submit",
                "execution" : execution_value[0],
                "username" : username,
                "password" : password,
                "loginType" : '1',
                "encrypted" : 'true'
            }
            auth_response = self.session.post(self.cas_url,data = auth_data,allow_redirects = False)
            if auth_response.status_code == 302:
                url_with_ticket = auth_response.headers["location"]
                confirm_response = self.svr_session.get(url = url_with_ticket,allow_redirects = True)
                if confirm_response.status_code == 200:
                    print("logon on success")
                    self.write_cascookies_to_file()
                    return True
                else:
                    print("logon on failed")
            else:
                print('auth failed')
                return False
        else:
            print("cas cookies still valid")
            url_with_ticket = cas_response.headers["location"]
            confirm_response = self.svr_session.get(url = url_with_ticket,allow_redirects = True)
            if confirm_response.status_code == 200:
                print("nopassword login success")
                return True
            else:
                print("cas url_with_ticket error")
                return False

    def load_cascookies_from_file(self):
        if os.path.exists("cas_cookies.dat"):
            with open("cas_cookies.dat", 'rb') as f:
                self.session.cookies.update(pickle.load(f))
    def write_cascookies_to_file(self):
        with open("cas_cookies.dat",'wb') as f:
            pickle.dump(self.session.cookies,f)

def main():
    with open("data.json") as f:
        data = json.loads(f)
    session = requests.session()
    cas = casService(session)
    cas.Login('https://ehall.hljeu.edu.cn/xglyw/_web/_apps/poe/mrdk/api/add.rst?domainId=1&szd='+data['dw']+'&yxid=19&dwlb=精准定位&xm='+data['name']+'&cardid='+data['cardid']+'&yxbm='+data['xy']+'&dksj='+time.strftime('%Y-%m-%d',time.localtime(time.time()))+'08:00:00&dktw='+data['dkwd']+'&jkzt='+data['jkzt']+'&sfgfx='+data['sfgfx']+'&lzdq=&sfqzysbl='+data['sfgzysbl']+'&szdtext='+data['dw']+'&xrywz='+data['xyrwz']+'&sfdym='+data['sfdym']+'&sdzjsl='+data['sdzjsl']+'&cxqk='+data['cxqk']+'&yszz='+data['yszz']+'&stzz='+data['stzz']+'&zjhsrq='+data['zjhsrq']+'&ssqy='+data['ssqy']+'&zjhsxxdz='+data['zjhsxxdz']+'&agree=1',data['cardid'], data['password'])
    print(time.strftime('%Y-%m-%d',time.localtime(time.time()))+'健康打卡完成')

if __name__ == '__main__':
    main()