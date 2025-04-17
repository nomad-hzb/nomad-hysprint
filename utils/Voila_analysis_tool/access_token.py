import requests
import getpass
import os

def get_token(url, name=None):
    try:
        return os.environ['NOMAD_CLIENT_ACCESS_TOKEN']
    except KeyError:
        user = user = name if name is not None else input("Username")
        print("Password:")
        password = getpass.getpass()
    
        # get token from the api:
        response = requests.get(f'{url}/auth/token', params=dict(username=user,password=password))
        if response.status_code == 401:
            raise Exception(response.json()["detail"])
        return response.json()['access_token']