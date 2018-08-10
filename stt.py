import requests
import json
import pyaudio
import wave
import gpio

# data = open('./introduce.wav', 'rb').read()

def transcript(data):
    response = requests.post(
        url='https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?model=ko-KR_NarrowbandModel',
        auth=('236f4487-fd5f-49ca-b286-6232520fa834', 'BryjOY7dZylp'),
        data=data, \
        headers={'Content-Type': 'audio/wav'})
    print('text type : ', type(response.text))
    # text = response.text.encode('utf-8').decode('utf-8')
    # print('response : ', text)
    response = json.loads(response.text)
    # transcript = response['results'][0]['alternatives'][0]['transcript']
    # print('transcript : ', response)
    return response

def recordWhenPress(gpio, timeout=10):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "./.mp3/record.wav"

    audio = pyaudio.PyAudio()
    btn_record = gpio

    try:
        print('음성 녹음 대기중')
        btn_record.wait(timeout=timeout)
    except:
        raise TimeoutError

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)
    print(str('음성 녹음 시작'))
    frames = []

    threshold = 800
    while True:
        for i in range(0, int(RATE / CHUNK)):
            data = stream.read(CHUNK)
            frames.append(data)
        if btn_record.read_value() == '1':
            break
    print('음성 녹음 완료')

    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    data = open(WAVE_OUTPUT_FILENAME, 'rb').read()
    data = transcript(data)

    print('you said : ', data)

    return data


def hasWord(script, word):
    word = word.replace(' ', '')
    for result in script['results']:
        for alternative in result['alternatives']:
            if alternative['transcript'].replace(' ', '').find(word) is not -1:
                return True
    return False
