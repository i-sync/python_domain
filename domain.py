#!/usr/bin/env python

import urllib.request
import urllib.error
import json
import random
import threading
import time
import re
from colors import PrintInColor

word3 = []
word4 = []
word5 = []
proxy = []
fail_proxy = []
fail_words = []

suffix = ['com','org', 'win','bid','pub','video','date','top','wang','vip','market','trade']
bash_url = 'http://checkdomain.xinnet.com/domainCheck?searchRandom={}&prefix={}&suffix=.{}'
#result
#null([{"searchRandom":2,"result":[{"yes":[],"no":[{"price":53,"flag":false,"productCode":"AEPDxin000200","prefix":"watt","originalNewPrice":128,"domainName":"watt.com","goodsCode":"GDxin000200","feeFlag":false,"suffix":".com","timeAmount":1}]}]}])
#null([{"searchRandom":2,"result":[{"yes":[{"price":16,"flag":false,"productCode":"AE2055812848402670","prefix":"watt","originalNewPrice":178,"domainName":"watt.pub","goodsCode":"50554363294238","feeFlag":false,"suffix":".pub","timeAmount":1}],"no":[]}]}])

lock_proxy = threading.Lock()
lock_fail_proxy = threading.Lock()
lock_result = threading.Lock()
lock_fail_words = threading.Lock()



def init():
    print('init...')
    with open('files/word3.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip(' \n')
            if line != '':
                word3.append(line)
    print('word3 count:{}'.format(len(word3)))

    with open('files/word4.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip(' \n')
            words = line.split(' ')
            word4.extend(words)
    print('word4 count:{}'.format(len(word4)))

    with open('files/word5.txt', 'r') as f:
        for line in f.readlines():
            line = line.strip(' \n')
            words = line.split(' ')
            word5.extend(words)

    print('word5 count:{}'.format(len(word5)))

    with open('files/proxy.json', 'r') as f:
        data = f.readline().strip('\n')
        proxy.extend(json.loads(data))
        #print(proxy)

    print('proxy count:{}'.format(len(proxy)))

    with open('files/fail_proxy.txt', 'r') as f:
        for line in f.readlines():
            fail_proxy.append(line.strip('\n'))
    print('fail_proxy count: {}'.format(len(fail_proxy)))

    with open('files/fail_words.txt', 'r') as f:
        for line in f.readlines():
            fail_words.append(line.strip('\n'))

    with open('files/result3.txt', 'r') as f:
        for line in f.readlines():
            line = re.split('\s+', line.strip(' \n'))[0]
            fail_words.append(line)

    with open('files/result4.txt', 'r') as f:
        for line in f.readlines():
            line = re.split('\s+', line.strip(' \n'))[0]
            fail_words.append(line)
    with open('files/result5.txt', 'r') as f:
        for line in f.readlines():
            line = re.split('\s+', line.strip(' \n'))[0]
            fail_words.append(line)
    print('fail_words count: {}'.format(len(fail_words)))

    print('init finish...')

def abort(flag, word):
    with open('files/abort{}.txt'.format(flag), 'w') as f:
        f.write(word)

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

def start(flag, words):
    print('start...')

    current_proxy = get_proxy()
    while current_proxy is None:
        print('first no proxy to use, sleep 60s ... proxy count:{}'.format(len(proxy)))
        time.sleep(60)
        current_proxy = get_proxy()

    for word in words:
        index = 0
        while index < len(suffix):
            suf = suffix[index]
            #check word and suffix if in fail list
            if '{}.{}'.format(word, suf) in fail_words:
                index += 1
                continue

            url = bash_url.format(random.randint(1,10), word, suf)
            print(url)
            req = urllib.request.Request(url)
            req.set_proxy('{}:{}'.format(current_proxy['host'], current_proxy['port']), current_proxy['type'])

            try:
                res = urllib.request.urlopen(req, timeout= 10)
            except Exception as e:
                fail(current_proxy['host'])
                current_proxy = get_proxy()
                while current_proxy is None:
                    #raise Exception('the proxy is empty...')
                    print('the proxy is empty, sleep 60s... proxy length: {}'.format(len(proxy)))
                    time.sleep(60)
                    current_proxy = get_proxy()
                continue

            data = res.read().decode('utf-8')
            #print(data)
            json_data = json.loads(data[5:-1])[0]['result'][0]
            yes = json_data['yes']
            if len(yes) > 0:
                PrintInColor.green(data)
                price = yes[0]['price']
                original_price = yes[0]['originalNewPrice']
                domain_ame = yes[0]['domainName']
                with lock_result:
                    with open('files/result{}.txt'.format(flag), 'a+') as f:
                        f.write('{:<15s}{:<10d}{:<10d}\n'.format(domain_ame, original_price, price))
            else:
                PrintInColor.red(data)
                with lock_fail_words:
                    with open('files/fail_words.txt', 'a+') as f:
                        f.write('{}.{}\n'.format(word, suf))
            index += 1

    #put current proxy to proxy pool
    plen = len(proxy)
    put_proxy(current_proxy)
    nlen = len(proxy)
    print('put proxy:{} into proxy pool, prev num:{} next num:{}.'.format(current_proxy['host'], plen,nlen))


def do():
    init()
    threads = []
    count = 50

    '''
    threadNum = len(word3) // count + (0 if len(word3) % count == 0 else 1)
    for i in range(threadNum):
        words = word3[i * count: (i+1)* count]
        threads.append(threading.Thread(target= start, args = (3, words,)))
    '''

    threadNum = len(word4) // count + (0 if len(word4) % count == 0 else 1)
    for i in range(threadNum):
        words = word4[i * count: (i+1)* count]
        threads.append(threading.Thread(target= start, args = (4, words,)))

    threadNum = len(word5) // count + (0 if len(word5) % count == 0 else 1)
    for i in range(threadNum):
        words = word5[i * count: (i+1)* count]
        threads.append(threading.Thread(target= start, args = (5, words,)))

    print('threads num: {}'.format(len(threads)))

    #sleep 5 second
    time.sleep(5)

    print('start threads...')
    for t in threads:
        t.start()

    # waitting all thread ends
    print('waitting all threads end...')
    for t in threads:
        t.join()

    print('all threads are done...')

if __name__ == '__main__':
    do()