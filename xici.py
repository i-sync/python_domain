#!/usr/bin/env python

from bs4 import BeautifulSoup
import threading
import urllib.request
import urllib.error
import json
import os
import time
import http.cookiejar

base_url = 'http://www.kuaidaili.com/free/inha/{}/'
headers = [
    ('Host','www.kuaidaili.com'),
    ('User-Agent', 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'),
    ('DNT', '1'),
    ('Upgrade-Insecure-Requests','1')
]

lock_json = threading.Lock()
lock_proxy = threading.Lock()
lock_accessed = threading.Lock()
lock_fail_proxy = threading.Lock()

json_data = []
proxy = []
fail_proxy = []
accessed = []

def init():
    with open('files/proxy.json', 'r') as f:
        data = f.readline().strip('\n')
        proxy.extend(json.loads(data))
        #print(proxy)

    print('proxy count:{}'.format(len(proxy)))

    with open('files/fail_proxy.txt', 'r') as f:
        for line in f.readlines():
            fail_proxy.append(line.strip('\n'))
    print('fail_proxy count: {}'.format(len(fail_proxy)))


    with open('files/accessed.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip(' \n')
            if line != '':
                accessed.append(int(line))

    print('init finish....')

def fail(host):
    with lock_fail_proxy:
        with open('files/fail_proxy.txt', 'a+') as f:
            f.write(host + '\n')

def get_proxy():
    '''
    get a worked proxy
    :return: proxy
    '''
    with lock_proxy:
        current_proxy = None
        if len(proxy) > 0:
            current_proxy = proxy.pop()
            #while current_proxy['type'] != 'http' or current_proxy['host'] in fail_proxy:
            while current_proxy['host'] in fail_proxy:
                if len(proxy) > 0:
                    current_proxy = proxy.pop()
                else:
                    current_proxy = None
                    print('proxy pool is empty...')
                    break
        else:
            print('proxy pool is empty...')

    return current_proxy

def put_proxy(x):
    with lock_proxy:
        proxy.append(x)

def start(pages):

    for page in pages:

        if page in accessed:
            continue

        current_proxy = get_proxy()
        if current_proxy is None:
            return
        '''
            while current_proxy is None:
            print('no proxy to use, sleep 60s ... proxy count:{}'.format(len(proxy)))
            time.sleep(60)
            current_proxy = get_proxy()
        '''
        try:
            url = base_url.format(page)
            print(url)
            #headers['Referer'] = url

            cj = http.cookiejar.CookieJar()
            proxy_handler = urllib.request.ProxyHandler({current_proxy['type']: '{}://{}:{}'.format(current_proxy['type'],current_proxy['host'],current_proxy['port'])})
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.add_handler(proxy_handler)
            opener.addheaders = headers
            try:
                res = opener.open(url, timeout= 10)
            except Exception as e:
                fail(current_proxy['host'])
                print(e)
                raise ProxyException()
            '''
            req = urllib.request.Request(url, headers=headers)
            try:
                res = urllib.request.urlopen(req, timeout = 10)
            except Exception as e:
                print(e)
            '''

            data = res.read()
            html = data.decode('utf-8')

            soup = BeautifulSoup(html, 'html.parser')
            trs = soup.find(id='list').find_all('tr')
            #print(trs)
            while len(trs) > 1:
                tds = trs.pop().find_all('td')
                data = {'host': tds[0].string, 'port': int(tds[1].string), 'type': tds[3].string}
                with lock_json:
                    json_data.append(data)

            #success
            with lock_accessed:
                with open('files/accessed.txt', 'a+') as f:
                    f.write('{}\n'.format(page))

        except ProxyException as e:
            pass
        except Exception as e:
            print(e)
            put_proxy(current_proxy)

        time.sleep(5)

def do():
    init()
    count = 1400
    num = 100
    threads = []
    for i in range(0, 14):
        pages = range(i*num + 1, (i+1)*num + 1)
        threads.append(threading.Thread(target=start, args=(pages,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
    print('all doen...')

    print('data num:{}'.format(len(json_data)))

    #if os.path.exists('files/xici.json'):
    #   os.remove('files/xici.json')
    with open('files/xici.json', 'a+') as f:
        json.dump(json_data, f)

    print('OK')

class ProxyException(Exception):
    pass

def do1():
    init()
    start(range(888,895,3))
    print(json_data)

if __name__ == '__main__':
    do()