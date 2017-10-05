import requests


def sendfile():
    api_url = 'http://127.0.0.1:8069/sign/set_signature'
    payload = {'dbname': 'prodsrtrunkfirma', 'token': 'd7P2wsgToSzpXiG4giwR'}
    with open('toverify.zip') as z:
        payload['zfile'] = z.read().encode('base64')
        z.close()
    r = requests.post(api_url, params=payload)
    # Rises if status != 200
    # FIXME: it needs more love
    r.raise_for_status()
    print r

if __name__ == "__main__":
    sendfile()
