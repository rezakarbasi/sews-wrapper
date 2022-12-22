import urllib.parse
import requests
import json
import urllib.parse
import time

base_url = 'http://127.0.0.1'
port = "8080"

_ = lambda url: f"{base_url}:{port}{url}"

headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
}

class PishgamanClient:
    instance = None
    client = requests.Session()

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
                    self._token = f.readline()
            except:
                pass
        return self._token

    def _login(self):
        payload = urllib.parse.urlencode({
            'username': self.username,
            'password': self.password,
            'grant_type': 'password',
        })
        response = requests.request("POST", _("/token"), headers=headers, data=payload)
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
        data = urllib.parse.urlencode(data)
        print(data)
        res = requests.request("POST", _(url), data=data, headers=self.wrap_auth_header(headers))
        time.sleep(10)
        if res.status_code in [401, 403]:
            self._login()
            res = self.post(url, data, headers)
        return res
