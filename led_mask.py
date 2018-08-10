import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import ssl
import time
from datetime import datetime
import firebase_manager
import random
import gpio
import tts
import threading
from os import listdir, system
from stt import recordWhenPress, hasWord

config = json.load(open('config.json','r'))
device_id = config['device_id']
device_token = config['device_token']
mask_uid = config['firebase_uid']
user_uid = None
id_token = None

ledState = False
lastData = {}

led_blue = gpio.GPIO(gpio.led_blue, 'out')
led_blue.write_value(0)

gpio.start_blinking_routine(gpio.led_red)

# The callback for when the client receives a CONNACK response from the server.

def build_timestamp():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

def build_led_pos():
    led_pos = []
    for _ in range(0, 25):
        led_pos.append(str(random.randint(0, 1)))
    return ''.join(led_pos)

def publish_payload(payload):
    tls_dict = {
        'ca_certs': None, 'certfile': None, 'keyfile': None, 'cert_reqs': ssl.CERT_REQUIRED,
        'tls_version': ssl.PROTOCOL_SSLv23, 'ciphers': None
    }

    publish.single('/v1.1/messages/ad14044bb436423d8dad442a449e119c',
               payload=payload, hostname="api.artik.cloud", port=8883,
               auth={'username': device_id,
                     'password': device_token},
               tls=tls_dict, transport="tcp")

def turnOffLED():
    global ledState
    print('turnOffLED')
    tts.text_to_speech('피부 개선을 종료 합니다')
    led_blue.write_value(0)
    publish_led_state('false')
    ledState = False
    generate_therapy_history()

def turnOnLED():
    global ledState
    print('turnOnLED')
    tts.text_to_speech('피부 개선을 시작 합니다')
    led_blue.write_value(1)
    publish_led_state('true')
    ledState = True

def startAnalysis():
    print('startAnalysis')
    tts.text_to_speech('피부 분석 시작')
    global lastData
    global ledState
    if not ledState:
        generate_analysis_history()
        tts.text_to_speech('피부 분석 완료')
        
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("/v1.1/actions/" + device_id)

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_publish(mqttc, obj, mid):
    print('mid: ', str(mid))

def on_message(client, userdata, msg):
    global lastData
    data = json.loads(msg.payload.decode())
    lastData = data
    action = data['actions'][0]['name']
    # print(msg.topic + " {}".format(data))
    if globals().get(action):
        globals()[action]()
    else:
        print('Undefined Action : %s' % action)

def publish_led_pos(led_pos):
    publish_payload('{"ledPosition" : "%s"}' % led_pos)

def publish_led_state(state):
    publish_payload('{"ledState" : %s}' % state)

def generate_therapy_history():
    global user_uid
    document = {
        'fields': {
            'date': {
                'timestampValue': build_timestamp()
            }
        }
    }
    firebase_manager.upload_therapy_document(document, user_uid, 'mask firebase token')
    

def generate_analysis_history():
    global user_uid
    def get_random_image_file():
        file_list = listdir('images/')
        return file_list[random.randint(0, len(file_list)-1)]

    img_file = get_random_image_file()
    led_pos = build_led_pos()
    document = {
        'fields': {
            'date': {
                'timestampValue': build_timestamp()
            },
            'led_pos': {
                'stringValue': led_pos
            },
            'image': {
                'stringValue': img_file
            }
        }
    }
    try:
        user_uid = lastData['actions'][0]['parameters']['user_id']
    except:
        pass
    firebase_manager.upload_file('%s/%s' % (user_uid, img_file), 'images/%s' % img_file, 'mask firebase token')
    firebase_manager.upload_analysis_document(document, user_uid, 'mask firebase token')
    publish_led_pos(led_pos)

def start_mqtt_client():
    mqtt_client = mqtt.Client()
    mqtt_client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,tls_version=ssl.PROTOCOL_SSLv23, ciphers=None)
    mqtt_client.username_pw_set(device_id, device_token)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_publish = on_publish
    mqtt_client.on_subscribe = on_subscribe

    mqtt_client.connect('api.artik.cloud', 8883, 60)
    # mqtt_client.loop_forever()
    mqtt_client.loop_start()

tts.text_to_speech('안녕하세요. 등록된 사용자를 불러옵니다.')

btn_yes = gpio.GPIO(config['btn_yes_pinnum'], 'in')
btn_no = gpio.GPIO(config['btn_no_pinnum'], 'in')

user_list = firebase_manager.get_user_lists(mask_uid)

if len(user_list) == 0:
    tts.text_to_speech('등록된 사용자가 없습니다. 작동을 종료합니다.')

i = 0
while True:
    tts.text_to_speech(user_list[i][1])
    tts.text_to_speech('님 이신가요?')

    try:
        reply = gpio.GPIO.wait_for([btn_yes, btn_no])
    except:
        pass

    if reply == btn_yes:
        tts.text_to_speech(user_list[i][1])
        tts.text_to_speech('님 환영합니다')
        user_uid = user_list[i][0]
        break
    elif reply == btn_no:
        i += 1
        i %= len(user_list)

start_mqtt_client()

tts.text_to_speech('버튼을 누르고 말을 해주세요')

while True:
    try:
        script = recordWhenPress(btn_yes)
    except:
        continue

    if hasWord(script, '분석') and hasWord(script, '시작'):
        startAnalysis()
    elif hasWord(script, '개선') and hasWord(script, '시작'):
        turnOnLED()
    elif hasWord(script, '개선') and hasWord(script, '종료'):
        turnOffLED()
    else:
        tts.text_to_speech('이해하지 못했습니다')
