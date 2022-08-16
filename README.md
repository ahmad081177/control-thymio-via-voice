## Control Thymio Robot via Voice Commands
Using vosk Speech to Text Library

## Abstract
This proof of concept combining a wireless Thymio II with a python software on computer to control the movements of the robot. Speech to text is performed on the computer, using vosk library with an offline model. Once the python application recognizes new voice, it turns it to text and based on the result, the python script decides what command to send to the Thymio robot.
First, let’s have some base knowledge on the pieces of the proof of the concept.

## Setup
* Install python v3 from https://www.python.org/downloads/
* Install the Thymio Suite from https://www.thymio.org/download-thymio-suite/
* Prepare new python environment:
  * In your command shell, run: python -m venv c:\work\thymio
  * Actibvate the environment by typing in the command shell: c:\work\thymio\Scripts\Activate.bat
  * Install required libraries by typing in the command shell: (thymio) c:\work\thymio> pip install vosk sounddevice tdmclient
  * Either download this repository to your local disk, say, c:\work\thymio\src\control-thymio-via-voice
  * Or: in your shell type: (thymio) c:\work\thymio> git clone https://github.com/ahmad081177/control-thymio-via-voice src
  * Download your desired VOSK model from: https://alphacephei.com/vosk/models to your local disk, say: c:\work\thymio\src\control-thymio-via-voice\vosk\models
  * Modify MODEL_FOLDER constant in control_thymio.py to reference the new model folder (from previous step)
* Run the software:
  * In your shell, type: (thymio) c:\work\thymio\src\control-thymio-via-voice>python control_thymio.py

### For more details, refer to: Control Thymio Robot via Voice Commands.docx

### Video at: https://youtu.be/3wKyVvp2RC0
