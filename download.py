#!/usr/bin/env python

import requests

CREDENTIALS = dict(
        username='YOUR JBOVLASTE USERNAME',
        password='YOUR JBOVLASTE PASSWORD',
)

# jbovlaste definitions language to download
LANG = 'en'

if __name__ == '__main__':
    s = requests.Session()
    r = s.post(
            'http://jbovlaste.lojban.org/login.html',
            data=CREDENTIALS,
    )
    r.raise_for_status()

    r = s.get(
            'http://jbovlaste.lojban.org/export/xml-export.html?lang=' + LANG,
    )

    r.raise_for_status()

    with open('vlasisku/data/jbovlaste.xml', 'wb') as f:
        f.write(r.text.encode('utf-8'))
