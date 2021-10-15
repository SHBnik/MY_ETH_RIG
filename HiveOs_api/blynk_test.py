
'''
#define BLYNK_TEMPLATE_ID "TMPLhIS8908P"
#define BLYNK_DEVICE_NAME "Quickstart Device"
#define BLYNK_AUTH_TOKEN "cluACxb4ZrIww8MIPJbJqcnX5zFbfD0J";
'''


import BlynkLib
import time

BLYNK_AUTH = 'cluACxb4ZrIww8MIPJbJqcnX5zFbfD0J'




# initialize Blynk
blynk = BlynkLib.Blynk(BLYNK_AUTH)
t = 0
@blynk.on("V*")
def blynk_handle_vpins(pin, value):
    global t
    print("V{} value: {}".format(pin, value))
    t = t+1
    blynk.virtual_write(13, t)

@blynk.on("connected")
def blynk_connected():
    print("Updating V1,V2,V3 values from the server...")
    blynk.sync_virtual(0,1,2,3,4,5,6,7,8,9,10,11,12)

while True:
    blynk.run()