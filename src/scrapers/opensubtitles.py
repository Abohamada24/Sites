import requests

class OpenSubtitles:
    def __init__(self, username, password):
        self.api_url = 'https://api.opensubtitles.org/xml-rpc'
        self.token = self.login(username, password)

    def login(self, username, password):
        headers = {'Content-Type': 'application/xml'}
        data = {
            'jsonrpc': '2.0',
            'method': 'LogIn',
            'params': [username, password, 'en', 'OSTestUserAgent'],
            'id': 1
        }
        response = requests.post(self.api_url, json=data, headers=headers)
        return response.json()['result']['token']

    def search_subtitles(self, query):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }
        data = {
            'jsonrpc': '2.0',
            'method': 'SearchSubtitles',
            'params': [self.token, query],
            'id': 1
        }
        response = requests.post(self.api_url, json=data, headers=headers)
        return response.json()['result']

    def logout(self):
        headers = {'Content-Type': 'application/json'}
        data = {
            'jsonrpc': '2.0',
            'method': 'LogOut',
            'params': [self.token],
            'id': 1
        }
        requests.post(self.api_url, json=data, headers=headers)
        self.token = None

# Example usage:
# subtitles = OpenSubtitles('your_username', 'your_password')
# results = subtitles.search_subtitles('Inception')
# print(results)