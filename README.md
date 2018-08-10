# ARTIK-LED-Mask-Client
ARTIK LED Mask Python3 client-side application on ubuntu 16.04 LTS

[Android Application](https://github.com/LunaTK/ARTIK-LED-Mask-android-app)

## Dependencies
* requests
* paho.mqtt
* pyrebase

## Configuration
You have to configure

* [Artik Cloud Developer](https://developer.artik.cloud) : Define your own device type. <br/>
Use [artik_cloud_device_manifest_v5.json](artik_cloud_device_manifest_v5.json)

* [Config.json](config.json) : device_id, device_token for ARTIK Cloud.

* [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech/docs/quickstart-protocol) : Set the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the file path of the JSON file that contains your service account key.

## Usage
```shell
    python3 led_mask.py
```