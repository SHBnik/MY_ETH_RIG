from requests import request, exceptions
from time import sleep
import json
import SecretData as sd


class Hive(object):

    def __init__(self, token):
        self.token = token

    def api_query(self, method, command, payload=None, params=None):

        if payload is None:
            payload = {}
        if params is None:
            params = {}
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }

        while True:
            try:
                s = request(method, 'https://api2.hiveos.farm/api/v2' + command, data=payload, params=params,
                            headers=headers, timeout=10)
            except exceptions.ConnectionError:
                print('exceptions.ConnectionError')
                sleep(15)
                continue
            except exceptions.Timeout:
                print('exceptions.Timeout')
                sleep(15)
                continue
            except exceptions.TooManyRedirects:
                print('exceptions.TooManyRedirects')
                sleep(1800)
                continue
            else:
                print(s)
                api = s.json()
                break

        return api

    def get_farms(self):
        return self.api_query('GET', '/farms')

    def get_worker_info(self,farm_id,worker_id):
        return self.api_query('GET', '/farms/' + farm_id + '/workers/' + worker_id)

    def edit_farm(self, farm_id, params):
        return self.api_query('PATCH', '/farms/' + farm_id, params)


def main():

    cHive = Hive(sd.get_token())
    data = cHive.get_worker_info(sd.get_farm_id(),sd.get_worker_id())["miners_stats"]["hashrates"][0]
    fan_perc = data['fans']
    graphic_temp = data['temps']
    print(fan_perc)
    print(graphic_temp) 


if __name__ == '__main__':
    main()