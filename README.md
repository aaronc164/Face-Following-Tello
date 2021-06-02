# Face-Following-Tello
Python code for a Ryze Tello drone, allowing it to follow your face.

## Requirements
- Python 3.5+ with pip installed
- djitellopy - ```pip install djitellopy```
- OpenCV - ```pip install opencv-python```
- Your PC will need to be connected to the Tello's network. To do that, turn the Tello on and connect to it via your PC's WiFi settings.

## Usage
Clone the repo and run **Drone.py**.
Press the *Takeoff* button, then use the *Up* and *Down* buttons to adjust height. Finally, press the *Toggle Face Recognition* button to start recognising your face.
The *DESTROY!* button will launch the Tello at your face, once it locks on.
