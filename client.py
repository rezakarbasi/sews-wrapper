import urllib.parse
import requests
import json
import urllib.parse
from http import client as cl

base_url = 'http://127.0.0.1'
port = "8080"
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

class PishgamanClient:
    instance = None
    client = cl.HTTPConnection(base_url, port)

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = object.__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, username='war', password='1'):
        self.username = username
        self.password = password
        self._token = None

    
    @property
    def token(self):
        if not self._token:
            try:
                with open("token.txt") as f:
                    self.token = f.readline()
            except:
                pass
        return self._token

    def _login(self):
        url = f'{base_url}/token'
        payload = urllib.parse.urlencode({
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
        })
        response = requests.post(url, headers=headers, data=payload)
        json_response = json.loads(response.text)
        self._token = json_response['access_token']
        with open("token.txt", "w") as f:
            f.writelines(self.token)
        time.sleep(10)

    
    def wrap_auth_header(self, headers={}):
        return {
            'Content-Type': 'application/x-www-form-urlencoded',
            **headers,
            'Authorization': f'Bearer {self.token}'
        }

    def post(self, url, data, headers={}):
        payload = urllib.parse.urlencode(payload)
        res = self.client.post(url, data=data, headers=self.wrap_auth_header(headers))
        if res.status_code in [401, 403]:
            self._login()
            res = self.post(url, data, headers)
        return res
