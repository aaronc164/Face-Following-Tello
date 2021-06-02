# Get those modules
from djitellopy.tello import Tello
import cv2
from tkinter import *
from threading import Thread
import time
from PIL import Image, ImageTk

# Very important variables
flyingEnabled = True

faceCenterPoint = None
screenSegmentsX = ((0, 320), (321, 640), (641, 960))
screenSegmentsY = ((0, 240), (241, 480), (481, 720))
currentSegmentX = None
currentSegmentY = None
faceArea = None
x, y, w, h = 0, 0, 0, 0
facesList = []
recognising = False
readyToCharge = False

yawVelocity = 0
yVelocity = 0
xVelocity = 0

running = True

# Makes the drone work
def takeoffSequence():
    global me
    me.send_rc_control(0, 0, 0, 0)
    me.takeoff()
    #time.sleep(2)
    #me.move_up(75)
    #me.send_command_without_return("up 75")

def landSequence():
    global me, recognising, recognisingLabel
    recognising = False
    recognisingLabel.config(text='Recognising: False')
    me.land()

# Control commands for drone
def up():
    global me
    me.move_up(50)

def down():
    global me
    me.move_down(50)

# Get THAT power
def battery():
    global me
    print(me.get_battery())

def tellDroneToWORK():
    while running:
        time.sleep(12)
        me.send_command_without_return("command")

# For removing the human population (in future)
def charge():
    global readyToCharge, me,recognising
    recognising = False
    recognisingLabel.config(text='Recognising: False')
    print('Human located, charging now')
    me.send_rc_control(0, 100, 0, 0)
    time.sleep(1)
    me.send_rc_control(0, 0, 0, 0)
    print('Human destroyed')
    recognising = True
    recognisingLabel.config(text='Recognising: True')
    readyToCharge = False

def chargeToCharge():
    global readyToCharge
    print('Locating human')
    readyToCharge = True

# Move the drone by itself.
def direction(xSegment, ySegment, area):
    global yVelocity, yawVelocity, xVelocity
    if xSegment == 1:
        yawVelocity = -45
    elif xSegment == 3:
        yawVelocity = 45
    else:
        yawVelocity = 0
    
    if ySegment == 1:
        yVelocity = 35
    elif ySegment == 3:
        yVelocity = -35
    else:
       yVelocity = 0

    if area > 4000:
        xVelocity = -30
    elif area < 2000:
        xVelocity = 30
    else:
       xVelocity = 0
       
    if readyToCharge:
        if xSegment == 2 and ySegment == 2:
            charge()
        else:
            if me.send_rc_control:
                me.send_rc_control(0, 0, yVelocity, yawVelocity)
    else:
        if me.send_rc_control:
            me.send_rc_control(0, xVelocity, yVelocity, yawVelocity)
    print(yVelocity, yawVelocity, xVelocity)

# Toggle face recognition (to stop 24/7 destruction)
def toggleRecognition():
    global recognising, me, recognisingLabel
    if not recognising:
        recognising = True
        recognisingLabel.config(text='Recognising: True')
    else:
        recognising = False
        me.send_rc_control(0, 0, 0, 0)
        recognisingLabel.config(text='Recognising: False')

# Setup tkinter window
tk = Tk()
tk.title("Ryze Tello Control Panel")
tk.resizable(0, 0)
canvas = Canvas(width=500, height=500, bd=0, highlightthickness=0)
canvas.pack()
tk.update()

# For facial detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Connect to Tello
me = Tello()
#me.connect() # Use when you want to feel important
me.send_command_without_return("command")

# Displays the buttons that launch the missile DRONE, NOT missile, definately not missile, no missiles here
if flyingEnabled:
    takeoffButton = Button(canvas, text="Takeoff", command=takeoffSequence)
    takeoffButton.pack()
    landButton = Button(canvas, text="Land", command=landSequence)
    landButton.pack()
    upButton = Button(canvas, text="Up", command=up)
    upButton.pack()
    downButton = Button(canvas, text="Down", command=down)
    downButton.pack()
    toggleButton = Button(canvas, text="Toggle Face Recognition", command=toggleRecognition)
    toggleButton.pack()
    recognisingLabel = Label(canvas, text='Recognising: False')
    recognisingLabel.pack()
    destroyButton = Button(canvas, text='DESTROY!', comman=chargeToCharge)
    destroyButton.pack()
else:
    # There is no flying
    noFlyingLabel = Label(canvas, text='Flying is not enabled.')
    noFlyingLabel.pack()

# Battery juice is tasty
batteryButton = Button(canvas, text="Battery?", command=battery)
batteryButton.pack()

# My favourite variable: "noImageImage"
noImageImage = PhotoImage(file="placeholder.gif")
imageLabel = Label(tk, image=noImageImage)
imageLabel.pack()
tk.update()

# Make the drone see you
me.streamoff()
me.streamon()

# LAUNCH
if flyingEnabled:
    takeoffSequence()

# Make the drone be in my command FOREVER
iAmInControlThread = Thread(target=tellDroneToWORK)
iAmInControlThread.daemon = True
iAmInControlThread.start()

while running:
    # Reads and detects the face
    frame_read = me.get_frame_read()
    frame = frame_read.frame
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Makes a rectangle
    try:
        x, y, w, h = faces[0]
        #facesList = [[], []]
        #for (x, y, w, h) in faces:
        #    facesList[0].append((x, y, w, h))
        #    facesList[1].append(w*h)
        #biggestFaceIndex = facesList[1].index(max(facesList[1]))
        #x, y, w, h = facesList[0][biggestFaceIndex]
        
        cx = int((x + x + w) / 2)
        cy = int((y + y + h) / 2)
        cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
        faceCenterPoint = (cx, cy)
        for i in range(0, len(screenSegmentsX)):
            x1 = screenSegmentsX[i][0]
            x2 = screenSegmentsX[i][1]
            if cx > x1 and x2 > cx:
                currentSegmentX = i + 1
            
        for i in range(0, len(screenSegmentsY)):
            y1 = screenSegmentsY[i][0]
            y2 = screenSegmentsY[i][1]
            if cy > y1 and y2 > cy:
                currentSegmentY = i + 1
        faceArea = int((w * h)/10)
    except:
        faceCenterPoint = None

    try:
        # Displays it via tkinter
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        img = img.resize((576, 432), Image.ANTIALIAS)
        imgtk = ImageTk.PhotoImage(image=img)
        imageLabel.configure(image=imgtk)
    except:
        pass

    if faceCenterPoint:
        #print(currentSegmentX, currentSegmentY, faceCenterPoint)
        if recognising and flyingEnabled:
            direction(currentSegmentX, currentSegmentY, faceArea)
    
    # Updates tkinter
    try:
        tk.update_idletasks()
        tk.update()
    except:
        break

running = False

# Lands the drone when program is finished
if flyingEnabled:
    try:
        landSequence()
    except:
        print("Drone already landed")

me.streamoff()
