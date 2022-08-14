import queue
import sys
import json

import sounddevice as sd
from vosk import Model, KaldiRecognizer


from thymio import Thymio
_thymio = None

def init_thymio():
    print('To create new Thymio interface')
    _thymio = Thymio()
    print('To start Thymio interface')
    try:
        r = _thymio.start()
        if r>0:
            print('Thymio interface has been started successfully')
            return _thymio
        else:
            print('Thymio interface could not be started')
            return None
    except Exception as ex :
        print(str(ex))
        return None

## Download Model(s) from https://alphacephei.com/vosk/models
MODEL_FOLDER=r".\vosk\models\vosk-model-en-us-0.22-lgraph"

'''This script processes audio input from the microphone and displays the transcribed text.'''
    
# list all audio devices known to your system
# You may uncomment the following 2 lines for debugging
# print("Display input/output devices")
# print(sd.query_devices())


# get the samplerate - this is needed by the Kaldi recognizer
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

# display the default input device
print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

# setup queue and callback function
q = queue.Queue()

def recordCallback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))
    
# build the model and recognizer objects.
print("===> Build the model and recognizer objects.  This will take a few minutes.")
model = Model(MODEL_FOLDER)
recognizer = KaldiRecognizer(model, samplerate)
recognizer.SetWords(False)


print("===> Begin recording. Press Ctrl+C to stop the recording ")
try:
    with sd.RawInputStream(dtype='int16', channels=1,callback=recordCallback):
        while True:
            data = q.get()        
            if recognizer.AcceptWaveform(data):
                recognizerResult = recognizer.Result()
                # convert the recognizerResult string into a dictionary  
                resultDict = json.loads(recognizerResult)
                if not resultDict.get("text", "") == "":
                    #Ahmad - Integrate Thymio to speech recognition
                    print(recognizerResult)
                    #Try re-initialize the thymio interface
                    if _thymio is None:
                        _thymio = init_thymio()
                    else:
                        _thymio.on_command(resultDict.get("text", ""))
                else:
                    print("no input sound")
            #sd.sleep(500)

except KeyboardInterrupt:
    print('===> Finished Recording')
except Exception as e:
    print(str(e))
