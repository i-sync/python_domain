#!/usr/bin/env python

import urllib.request
import re
import json
url = 'https://anvaka.github.io/common-words/static/data/{}/index.json'

def start():
    results = []
    langs = ['jsx', 'css', 'html', 'java', 'py', 'lua','php','rb','cpp','pl','cs','scala','go','sql','rs','lisp','clj','kt','cmake','swift','hs','ex','objc','fs','elm','purs','pas','r','erl','vim','groovy']
    for lang in langs:
        print(url.format(lang))
        res = urllib.request.urlopen(url.format(lang))
        data = res.read().decode('utf-8')
        json_data = json.loads(data)
        for d in json_data:
            if d['text'] not in results:
                results.append(d['text'])



    with open('files/special.txt', 'w') as f:
        json.dump([w for w in results if len(w) <= 8 ], f)

    print('OK')

if __name__ == '__main__':
    start()