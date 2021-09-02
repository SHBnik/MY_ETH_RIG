from requests import request, exceptions
from time import sleep
import json
import serial
import serial.tools.list_ports
import SecretData as sd
import time



fan_serial = None
fans_flag = [0,0,0,0,0,0,0,0,0,0,0,0]

last_time = 0


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




def Search_for_fan_serial_port():
    global fan_serial
    available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for port in available_ports:
        test_serial = serial.Serial(
            port = port[0],
            baudrate = 9600,
            timeout=1,
            xonxoff=0,
            rtscts=0
        )
        # Toggle DTR to reset Arduino
        test_serial.setDTR(False)
        sleep(1)
        # toss any data already received, see
        # http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.flushInput
        test_serial.flushInput()
        test_serial.setDTR(True)


        time_last = time.time()
        while True:
            if test_serial.inWaiting():
                text = test_serial.readline().decode('utf-8')
                if text.find('Arduino ON') != -1:
                    fan_serial = test_serial
                    print('!!!arduino port found on port %s!!!'%port[0])
                    break
                else:pass


            if time.time()-time_last > 10:
                print('!!!! this port is not arduino %s  !!!!'%port[0])
                break





def check_temp(fan,temp):
    global fans_flag,fan_serial
    for index,fan_value,temp_value in enumerate(zip(fan,temp)):
        if not fans_flag[index]:
            if fan_value > 60:
                fan_serial.write('%d,1\n'%index)
                fans_flag[index] = 1
        else:
            if fan_value < 43 and temp_value < 65:
                fan_serial.write('%d,0\n'%index)
                fans_flag[index] = 0
        


def main():
    global last_time
    cHive = Hive(sd.get_token())
    while True:
        if time.time() - last_time > 60:
            last_time = time.time()
            try:
                data = cHive.get_worker_info(sd.get_farm_id(),sd.get_worker_id())["miners_stats"]["hashrates"][0]
                fan_perc = data['fans']
                graphic_temp = data['temps']
                print(fan_perc,graphic_temp)
                check_temp(fan_perc,graphic_temp)
            except Exception as e:
                print('error in main loop',e) 


if __name__ == '__main__':
    Search_for_fan_serial_port()
    main()