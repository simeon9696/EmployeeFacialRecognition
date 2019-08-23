# USAGE
# python pi_face_recognition.py --cascade haarcascade_frontalface_default.xml --encodings encodings.pickle

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from datetime import datetime
from datetime import date
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import csv
import os

################################Function Definitions##########################
def initializeLogDirectories():
    #create directory for logs if it doesn't exist
    current_directory = os.getcwd()
    final_directory =os.path.join(current_directory, r'ed/eLogs')
    if os.path.exists(final_directory):
        print("[INFO] 'ed/eLogs' directory found")
    if not os.path.exists(final_directory):
        print("[INFO] Directory 'ed/eLogs' does not exist")
        print("[INFO] Creating 'ed/eLogs' directory")
        os.makedirs(final_directory)
        print("[INFO] 'ed/eLogs' directory created successfully")


    final_directory =os.path.join(current_directory, r'ed/eLists')
    if os.path.exists(final_directory):
        print("[INFO] 'ed/eLists' directory found")
    if not os.path.exists(final_directory):
        print("[INFO] Directory 'ed/eLists' does not exist")
        print("[INFO] Creating 'ed/eLists' directory")
        os.makedirs(final_directory)
    return
    


def initializeLists():
    print("[INFO] Opening employeeList.txt...")
    with open("ed/eLists/employeeList.txt","r+") as f: #open employeeList for reading, enable bufffer
        print("[INFO] employeeList.txt found!")
        lines = f.read()            #get all listings from employeeList
        lines = lines.split("\n")   #separate each listing
        print("[INFO] Sorting employeeList.txt...")
        lines.sort()                #sort list by alphabeticcal order according to dept
        print("[INFO] Sorting complete!")
    
    with open("ed/eLists/employeeListSorted.txt","w+") as f:
        print("[INFO] Writing sorted to employeeListSorted.txt")
        f.write('\n'.join(lines))
        print("[INFO] File write complete!")
    return lines


def logEmployee(name,lines):
    #Get current date and time to be used for logs
    dateToday = (date.today()).strftime("%d-%B-%Y")
    #create log name string according to the present date
    logname =("ed/eLogs/elogs-%s.xlsx" % dateToday)

    if not os.path.exists(logname):
        with open(logname,"w+") as fileHandler:
            csvWriter = csv.writer(fileHandler)
            csvWriter.writerow(["Department","First Name","Last Name","Status","Time In","Time Out","Employee On Plant"])
            for line in lines:
                csvRow = [line.split(",")[0],line.split(",")[1],line.split(",")[2],line.split(",")[3],None,None,"False"]
                csvWriter.writerow(csvRow)
        print("[INFO] Employee log created successfully")
    
    if os.path.exists(logname):
        #Get last time logged in our logged out, check it to see if it's more than
        #ten minutes. If it is register it as an logged in logged out event accordingly
        #Otherwise, ignore and do not write to file
        index=0;
        with open(logname,"r") as fileReader:
            csvReader =csv.reader(fileReader)
            lines = list(csvReader)
            for i, j in enumerate(lines):
                if j[1] == name.split( )[0]:
                    index = i
        fileReader.close()
        print("[INFO] Logging employee",name,"...")
        
        currentTime = datetime.now().strftime("%H:%M:%S")
        with open(logname,"w+") as fileWriter:
    
            csvWriter = csv.writer(fileWriter)
            if lines[index][6] == "False":
                lines[index][4] = lines[index][4] +","+currentTime
                lines[index][6] =  "True"
                csvWriter.writerows(lines)
                print("[INFO]",name,"logged in at: ",currentTime)

            elif lines[index][6] == "True":
                lines[index][5] = lines[index][5] +","+ currentTime
                lines[index][6] =  "False"
                csvWriter.writerows(lines)
                print("[INFO]",name,"logged out at: ",currentTime)

        fileWriter.close()
        print("[INFO] Log complete, closing file")
        return
#############################-Main script starts here-########################

initializeLogDirectories()
fileContent = initializeLists()



# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--cascade", required=True,
    help = "path to where the face cascade resides")
ap.add_argument("-e", "--encodings", required=True,
    help="path to serialized db of facial encodings")
args = vars(ap.parse_args())

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(args["encodings"], "rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# loop over frames from the video file stream
while True:
    # grab the frame from the threaded video stream and resize it
    # to 500px (to speedup processing)
    frame = vs.read()
    frame = imutils.resize(frame, width=500)
    
    # convert the input frame from (1) BGR to grayscale (for face
    # detection) and (2) from BGR to RGB (for face recognition)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # detect faces in the grayscale frame
    rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
        minNeighbors=5, minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE)

    # OpenCV returns bounding box coordinates in (x, y, w, h) order
    # but we need them in (top, right, bottom, left) order, so we
    # need to do a bit of reordering
    boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

    # compute the facial embeddings for each face bounding box
    encodings = face_recognition.face_encodings(rgb, boxes)
    names = []

    # loop over the facial embeddings
    for encoding in encodings:
        # attempt to match each face in the input image to our known
        # encodings
        matches = face_recognition.compare_faces(data["encodings"],
            encoding)
        name = "Unknown"

        # check to see if we have found a match
        if True in matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            name = max(counts, key=counts.get)
            #logEmployee(name,fileContent)

        # update the list of names
        names.append(name)

    # loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # draw the predicted face name on the image
        cv2.rectangle(frame, (left, top), (right, bottom),
            (0, 255, 0), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
            0.75, (0, 255, 0), 2)

    # display the image to our screen
    #cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
