import sys, os

def text_to_speech(text):
    if not os.path.exists('./.mp3/'):
        os.makedirs('./.mp3/')

    if ('%s.mp3' % text) not in os.listdir('.mp3/'):
        """Synthesizes speech from the input string of text."""
        from google.cloud import texttospeech
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.types.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.types.VoiceSelectionParams(
            language_code='ko-KR',
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

        audio_config = texttospeech.types.AudioConfig(
            audio_encoding=texttospeech.enums.AudioEncoding.MP3)

        response = client.synthesize_speech(input_text, voice, audio_config)

        # The response's audio_content is binary.
        with open('.mp3/%s.mp3' % text, 'wb') as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

    os.system('mpg123 ".mp3/%s.mp3"' % text)


if __name__ == '__main__':
    text_to_speech(sys.argv[1])
