import BlynkLib
from requests import request, exceptions
from time import sleep
import json
import serial
import serial.tools.list_ports
import SecretData as sd
import time



fan_serial = None
fans_flag = [0,0,0,0,0,0,0,0,0,0,0,0]
fans_force_flag = [0,0,0,0,0,0,0,0,0,0,0,0]
last_time = 0

blynk = BlynkLib.Blynk(sd.get_blynk_token())
blynk_Fan = [0,1,2,3,4,5,6,7,8,9,10,11]
Power = 12
blynk_Temp = [13,14,15,16,17,18,19,20,21,22,23,24]
blynk_Perc = [25,26,27,28,29,30,31,32,33,34,35,36]
blynk_LED = [37,38,39,40,41,42,43,44,45,46,47,48]
Power_LED = 49
Fan_ALL = 50


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
    port_found_flag = False
    available_ports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    for port in available_ports:
        if port_found_flag:
            break

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
        test_serial.flushInput()
        test_serial.setDTR(True)


        time_last = time.time()
        while True:
            if test_serial.inWaiting():
                text = test_serial.readline().decode('utf-8')
                if text.find('Arduino ON') != -1:
                    fan_serial = test_serial
                    print('!!!arduino port found on port %s!!!'%port[0])
                    port_found_flag = True
                    break
                else:pass


            if time.time()-time_last > 10:
                print('!!!! this port is not arduino %s  !!!!'%port[0])
                break





def check_temp(fan,temp):
    global fans_flag,fan_serial
    for index,(fan_value,temp_value) in enumerate(zip(fan,temp)):
        blynk.virtual_write(blynk_Temp[index], temp_value)
        blynk.virtual_write(blynk_Perc[index], fan_value)
        if not fans_force_flag[index]:
            if not fans_flag[index]:
                if fan_value > 60 or temp_value > 67:
                    # fan_serial.write('%d,1\n'%index)
                    fans_flag[index] = 1
                    blynk.virtual_write(blynk_LED[index], 1)
            else:
                if fan_value < 50 and temp_value < 70:
                    # fan_serial.write('%d,0\n'%index)
                    fans_flag[index] = 0
                    blynk.virtual_write(blynk_LED[index], 0)
        


@blynk.on("V*")
def blynk_handle_vpins(pin, value):
    global fans_force_flag,fan_serial
    print("V{} value: {}".format(pin, value))
    if pin == str(Power):
        blynk.virtual_write(Power_LED, value)
        # fan_serial.write('%s,%s\n'%(pin,value))
    elif pin == str(Fan_ALL):
        for i in range(len(fans_flag)):
            fans_force_flag[i] = value
            blynk.virtual_write(blynk_LED[i], value)
            # fan_serial.write('%d,%s\n'%(i,value))
    else:
        fans_force_flag[int(pin)] = value
        blynk.virtual_write(blynk_LED[int(pin)], value)
        # fan_serial.write('%s,%s\n'%(pin,value))

@blynk.on("connected")
def blynk_connected():
    blynk.sync_virtual(0,1,2,3,4,5,6,7,8,9,10,11,12,50)



def main():
    global last_time , blynk
    cHive = Hive(sd.get_token())
    while True:
        #   update blynk
        blynk.run()


        #   update HIVE
        if time.time() - last_time > 10:
            last_time = time.time()
            # try:/
            data = cHive.get_worker_info(sd.get_farm_id(),sd.get_worker_id())["miners_stats"]["hashrates"]
            data_SHB = data[0]
            data_SHN = data[1]
            fan_perc = data_SHN['fans'] + data_SHB['fans']
            graphic_temp = data_SHN['temps'] + data_SHB['temps']
            
            print(data_SHN['invalid_shares'])
            SHB_invshare = [int(i) for i in data_SHB['invalid_shares']]
            SHN_invshare = [int(i) for i in data_SHN['invalid_shares']]
            invalid_share = SHB_invshare + SHN_invshare #sum([SHB_invshare,SHN_invshare])
            # print(invalid_share)
            # print(fan_perc,graphic_temp)
            print(data)
            # check_temp(fan_perc,graphic_temp)
            
            # except Exception as e:
            #     print('error in main loop',e) 


if __name__ == '__main__':
    # Search_for_fan_serial_port()
    main()