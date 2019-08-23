from datetime import datetime
from datetime import date
import shutil
import picamera
import time
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
    with open("ed/eLists/employeeList.txt","r+",encoding ="UTF-8") as f: #open employeeList for reading, enable bufffer
        print("[INFO] employeeList.txt found!")
        lines = f.read()            #get all listings from employeeList
        lines = lines.split("\n")   #separate each listing
        print("[INFO] Sorting employeeList.txt...")
        lines.sort()                #sort list by alphabetical order according to department
        print("[INFO] Sorting complete!")
    
    with open("ed/eLists/employeeListSorted.txt","w+",encoding ="UTF-8") as f:
        print("[INFO] Writing sorted to employeeListSorted.txt")
        f.write('\n'.join(lines))
        print("[INFO] File write complete!")
    return lines

def getLogName():
    #Get current date and time to be used for logs
    dateToday = (date.today()).strftime("%d-%B-%Y")
    #create log name string according to the present date
    logname =("ed/eLogs/elogs-%s.xlsx" % dateToday)
    return logname

def logEmployee(name):
    logname = getLogName()
    if not os.path.exists(logname):
        lines = initializeLists()
        with open(logname,"w+",encoding ="UTF-8") as fileHandler:
            csvWriter = csv.writer(fileHandler)
            csvWriter.writerow(["Department","First Name","Last Name","Status","Time In","Time Out","Employee On Plant","Access"])
            for line in lines:
                csvRow = [line.split(",")[0],line.split(",")[1],line.split(",")[2],line.split(",")[3],None,None,"False",line.split(",")[4]]
                csvWriter.writerow(csvRow)
        print("[INFO] Employee log created successfully")
    
    if os.path.exists(logname):
        #Get last time logged in our logged out, check it to see if it's more than
        #ten minutes. If it is register it as an logged in logged out event accordingly
        #Otherwise, ignore and do not write to file
        index=0;
        with open(logname,"r",encoding ="UTF-8") as fileReader:
            csvReader =csv.reader(fileReader)
            lines = list(csvReader)
            for i, j in enumerate(lines):
                if j[1] == name.split( )[0]:
                    index = i
        fileReader.close()
        print("[INFO] Logging employee",name,"...")
        
        currentTime = datetime.now().strftime("%H:%M:%S")
        with open(logname,"w+",encoding ="UTF-8") as fileWriter:
    
            csvWriter = csv.writer(fileWriter)
            if lines[index][6] == "False":
                if lines[index][4] == "":
                    lines[index][4] = currentTime
                else:
                    lines[index][4] = lines[index][4] +","+currentTime
                lines[index][6] =  "True"
                csvWriter.writerows(lines)
                print("[INFO]",name,"logged in at: ",currentTime)

            elif lines[index][6] == "True":
                if lines[index][5] == "":
                    lines[index][5] = currentTime
                else:
                    lines[index][5] = lines[index][4] +","+currentTime
                lines[index][6] =  "False"
                csvWriter.writerows(lines)
                print("[INFO]",name,"logged out at: ",currentTime)

        fileWriter.close()
        print("[INFO] Log complete, closing file")
        return
    
def addEmployee(department,firstName,lastName,status,access):
    #get current time
    timeIn = datetime.now().strftime("%H:%M:%S")
    #set time out for new employee as empty
    timeOut = ""
    #format new employee data for writing to employeeList.txt
    employeeInfo = ("\n{},{},{},{},{}".format(department,firstName,lastName,status,access))
    #format new employee data to write to log
    employeeInfoCSV =("{},{},{},{},{},{},True,{}".format(department,firstName,lastName,status,timeIn,timeOut,access))

    #write new employee data to employeeList
    with open("ed/eLists/employeeList.txt","a+",encoding ="UTF-8") as f:
        print("[INFO] Writing sorted to employeeList.txt")
        f.writelines(employeeInfo)
        print("[INFO] File write complete!")
        
    #get log name for current day
    logname = getLogName()
    #initialize empty list to hold all departments in CSV file
    departmentsInCSV =[]
    #open CSV file and fill list with all department entries
    with open(logname,"r",encoding ="UTF-8") as fileReader:
        csvReader =csv.reader(fileReader)
        lines = list(csvReader)
        for i, j in enumerate(lines):
            departmentsInCSV.append(j[0])
    #determine number of lines in CSV file
    lengthofCSV = len(departmentsInCSV)
    
    #get index of first occurence of department that new employee belongs to
    firstIndexOfDepartment = departmentsInCSV.index(department)
    
    #get index of last occurence of department that new employee belongs to
    lastIndexOfDepartment = (len(departmentsInCSV) - 1) - departmentsInCSV[::-1].index(department) 
    
    #slice orignal list with boundaries of first & last occurence of new employee's department
    departmentsInCSV = lines[firstIndexOfDepartment:lastIndexOfDepartment+1]
    
    #initialize temporary list to hold all rows with new employee's department
    tempArr=[]
    for departments in departmentsInCSV:
        tempArr.append(','.join(departments))
    
    #append employee information to temporary list
    tempArr.append(''.join(employeeInfoCSV))
    
    #sort temporary list according to first name
    tempArr.sort()
    
    #write updated department slice, along with all original content to new log
    with open(logname,"w+",encoding ="UTF-8") as fileHandler:
        csvWriter = csv.writer(fileHandler)
        csvWriter.writerows(lines[0:firstIndexOfDepartment]) #content before slice
        for row in tempArr:
            csvWriter.writerow(row.split(",")) #sliced content
        csvWriter.writerows(lines[lastIndexOfDepartment+1:lengthofCSV]) #content after slice
    return 

def deleteEmployee(name):
    firstName = name.split(" ")[0]
    lastName = name.split(" ")[1]
    print("[INFO] Deleting employee {} {} from employeeList.txt...".format(firstName, lastName))
    print("[INFO] Opening employeeList.txt...")
    tempArr = []
    with open("ed/eLists/employeeList.txt","r+",encoding ="UTF-8") as f: #open employeeList for reading, enable bufffer
        print("[INFO] employeeList.txt found!")
        lines = f.read()            #get all listings from employeeList
        lines = lines.split("\n")   #separate each listing
        f.seek(0)                   #reset pointer
        f.truncate()                #invalidate file contents
        employeeFound = False
        print("[INFO] Searching Employee List...")

        for line in lines:          #get each line in employee list
            # match the first and last name in that file with the input name
            if ((line.split(",")[1] + line.split(",")[2]) != firstName + lastName):
                tempArr.append(line) #if does not match, append it to a temporary list
            if ((line.split(",")[1] + line.split(",")[2]) == firstName + lastName):
                print("[INFO] Record found, deleting record")
                employeeFound = True
        #attach newline to every row in the file and write list contents to file
        f.write('\n'.join(tempArr)) 
        if not employeeFound:
            print("[ERROR] No employee record matching that name was found") #else update console
    
    #we need to delete all the images for that employee
    employeeImageDirectory = ("dataset/{}".format(name))
    try:
        if os.path.exists(employeeImageDirectory):
            print("[INFO] {} images found! Deleting...".format(name))
            shutil.rmtree(employeeImageDirectory)
            print("[INFO] {} images deleted..".format(name))
        if not os.path.exists(employeeImageDirectory):
            print("[ERROR] No images were found matching this employee")
    except:
        print("[ERROR]")
    
    return

def takeEmployeeImage(name):
    employeeDataSet = ("dataset/{}".format(name))
    if not os.path.exists(employeeDataSet):
        print("[INFO]" )
        os.makedirs(employeeDataSet)
    
    if os.path.exists(employeeDataSet):
        pictureCount=1
        with picamera.PiCamera() as camera:
            camera.resolution = (1920,1080)
            camera.start_preview()
            # Camera warm-up time
            time.sleep(2)
            print("[INFO] Press c + enter to capture image or e + enter to exit capture mode")
            print("[INFO] Six images will be collected. Facial maps must be rebuilt manually")
            while (pictureCount < 7):
                keypress = input()
                if keypress == "c":
                    pictureName = ('{}/00000{}.jpg'.format(employeeDataSet,pictureCount))
                    print("[INFO] Taking picture: ",pictureCount)
                    camera.capture(pictureName)
                    pictureCount = pictureCount + 1
                if keypress == "e":
                    print("[INFO] Breaking execution of capture mode. Any image captured will be saved")
                    break
            print("[INFO] Six images captured. Initiate facial map rebuild soon")
    return
#############################-Main script starts here-########################

initializeLogDirectories()
initializeLists()

#logEmployee("David Ramjit")
#logEmployee("Simeon Ramjit")
deleteEmployee("Kelsey Ramjit")
#logEmployee("Keri Gobin")
#addEmployee("Mechanical","Kesley","Ramjit","Full-Time","Granted")

#takeEmployeeImage("Kelsey Ramjit")
