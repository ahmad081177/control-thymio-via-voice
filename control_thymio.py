#Managing queue of data
import queue
import sys
import json
#library for listening to the microphone
import sounddevice as sd
#Import the offline model and the offline recognizer from VOSK library
from vosk import Model, KaldiRecognizer


from thymio import Thymio

def init_thymio():
    """Initialize the Thymio connection"""

    print('To create new Thymio interface')
    _thymio = Thymio()
    print('To start Thymio interface')
    try:
        r = _thymio.start()
        if r==True:
            print('Thymio interface has been started successfully')
            return _thymio
        else:
            print('Thymio interface could not be started')
            return None
    except Exception as ex :
        print(str(ex))
        return None
#Initialize the Thymio interface
_thymio = init_thymio()


## Download Model(s) from https://alphacephei.com/vosk/models
MODEL_FOLDER=r".\vosk\models\vosk-model-en-us-0.22-lgraph"

'''This script processes audio input from the microphone and displays the transcribed text.'''

# get the samplerate - this is needed by the Kaldi recognizer
device_info = sd.query_devices(sd.default.device[0], 'input')
samplerate = int(device_info['default_samplerate'])

# display the default input device
print("===> Initial Default Device Number:{} Description: {}".format(sd.default.device[0], device_info))

# setup queue and callback function
q = queue.Queue()

def recordCallback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block.
    Saves the audio block to a queue."""

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
    # start the recording thread, and listens to the microphone
    with sd.RawInputStream(dtype='int16', channels=1,callback=recordCallback):
        while True:
            # get the next audio block from the queue
            data = q.get()
            # recognize the speech in the audio block
            if recognizer.AcceptWaveform(data):
                # returns a list of possible transcripts
                recognizerResult = recognizer.Result()
                # convert the recognizerResult string into a dictionary  
                resultDict = json.loads(recognizerResult)
                if not resultDict.get("text", "") == "":
                    #Integrate Thymio to speech recognition
                    print(recognizerResult)
                    #Try re-initialize the thymio interface if it fails
                    if _thymio is None:
                        _thymio = init_thymio()
                    #If the thymio interface is initialized, send the command to the thymio
                    else:
                        _thymio.on_command(resultDict.get("text", ""))
                else:
                    print("no input sound")
# if Ctrl+C is pressed, stop the recording thread and finish
except KeyboardInterrupt:
    print('===> Finished Recording')
except Exception as e:
    print(str(e))
