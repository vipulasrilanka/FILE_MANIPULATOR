# !/usr/bin/python

import os
import csv
import threading
import time
import logging

Program_Version = "0.00.001"
Program_Status = "Beta" 
A = [1,2,3,4,5]

# enable logging for all functions.
logging.basicConfig(filename='debug.log',format='%(asctime)s | %(levelname)s | %(message)s',level=logging.DEBUG)
# add the version info to the log.
logging.debug('FileMan vesion %s %s',Program_Version, Program_Status)

#All the file/folder actions are implemented in this class.
class ActionManager:

    # constructor function
    # This will initialize all the status maintainig variables and
    # will start the file/folder read thread.   
    def __init__(self, ActionSourceFoler,ActionDestinationFolder, RowID):
        logging.debug("Action Manager Init called") #------debug message
        self.ActionDestinationFolder = ActionDestinationFolder #--Save the Destination folder for this action round
        self.ActionSourceFoler = ActionSourceFoler #--------------Save the source folder for this action round
        self.FlagReadNextSubFolder = False #----This is a local implementation of a lock. Set to False to hold the thread.
        self.FlagNextSubFolderReady = False #---This is a local implementation of a lock. This will be set by the thread.
        self.KeepThreadAlive = True #---------------------Thread will exit if this flag is false.
        self.FlagSubFolderTraverseThreadExit = False #----Indicator for the existance of the thread.
        self.SubFolderReadThread = threading.Thread(target = self.SubFolderTraverseThread, args = (RowID, ))
        self.SubFolderReadThread.start() #----------------Start the thread
        logging.debug("Action Manager starting the SubFolderReadThread..") #------debug message

    # Distructor function
    # this will stop the file read thread
    def __del__(self):
        logging.debug("Action Manager Distruct called") #------debug message
        self.KeepThreadAlive = False #Need to stop the thred
        self.FlagReadNextSubFolder = True #--Release the lock so that the thread can run.
        self.SubFolderReadThread.join() #wait for the thread to exit
        logging.debug("Action Manager Distructed...") #--------debug message

    # This thread goes through each sub folder and will update 
    # 'NextSubFolderPath' variable with the folder name.
    # This thread creates 'NextSubFolderPath' so this variable can not be 
    # accessed before this thread goes through one round.
    # If you set the "FlagReadNextSubFolder" to "True", this thread will run once and
    # will update the 'NextSubFolderPath' and will set 'FlagNextSubFolderReady' flag.
    # Make sure you set the "FlagNextSubFolderReady' to false before this setp for tracking.
    # The arg is not used now, and we just pass the row number of the active action rule for debugging needs.
    def SubFolderTraverseThread(self,arg):
        logging.debug("SubFolderTraverseThread started with %s", arg) #---------------debug message
        while(self.FlagReadNextSubFolder == False): #--Wait for the lock to release
            time.sleep(0.01)
        # we come here as the FlagReadNextSubFolder is True. 
        self.FlagReadNextSubFolder = False #reset the Flag to prevent re-run
        logging.debug("SubFolderTraverseThread continue...") #------------------------debug message
        if(self.KeepThreadAlive == False): #---check for exit signal.
            logging.debug("#10001 - SubFolderTraverseThread - Parent is dead") #------debug message
            self.FlagSubFolderTraverseThreadExit = True
            logging.debug("#10002 - exit From SubFolderTraverseThread") #-------------debug message
            return() #----Exit from thread.

        for root in os.walk(self.ActionSourceFoler, topdown=False):
            logging.debug (root[0]) #-------------------------------------------------debug message
            if (root[0] == self.ActionSourceFoler):
                logging.debug ("Root folder detected") #------------------------------debug message
                break
            x = root[0].split("\\") #get the last sub folder
            logging.debug(x[1]) # ---------------------------------------------------debug message
            self.NextSubFolderPath = os.path.join(self.ActionDestinationFolder,x[1]) #create the full path for the destination folder
            logging.info("SubFolderTraverseThread %s",self.NextSubFolderPath) #-----INFO: print new folder path
            self.FlagNextSubFolderReady = True #-----Indicate that the folder name is ready.
            while(self.FlagReadNextSubFolder == False): #--Wait for the next lock release.
                time.sleep(0.01)
            # we come here as the FlagReadNextSubFolder is True.
            self.FlagReadNextSubFolder = False #reset the Flag to prevent re-run
            
            if(self.KeepThreadAlive == False): #---check for exit signal.
                logging.debug("#10003 SubFolderTraverseThread - Parent is dead") # debug message
                break
        if (self.KeepThreadAlive == True):
            logging.debug("SubFolderTraverseThread - No more Folders to report..!")
        self.FlagSubFolderTraverseThreadExit = True
        logging.debug("exit From SubFolderTraverseThread")   #--Exit from thread.

    # This function selects the next sub folder
    # NextSubFolderPath will point to the Destination folder
    def SelectNextSubFilder(self):
        logging.debug("Select Next SubFilder- Let the thread run once")
        self.FlagReadNextSubFolder = True #--Release the lock for the read thread to run
        while(self.FlagNextSubFolderReady == False): #Wait for the Folder name
            time.sleep(0.01)
            if(self.FlagSubFolderTraverseThreadExit == True):
                logging.warning("SubFolderTraverseThread Terminated.")#---------debug warning.            
                return(1)
        # we come here as the FlagNextSubFolderReady is True. 
        self.FlagNextSubFolderReady = False #reset the Flag
        logging.info("SelectNextSubFilder - %s",self.NextSubFolderPath) #-------Report the folder name we got
        return(0)

    # This function will get the next sub folder name and create an empty folder 
    # in the destination folder path
    def MakeNextSubFolder(self):
        logging.info("MakeNextSubFolder - %s",self.NextSubFolderPath) #--------Debug message
        print("Creating ", self.NextSubFolderPath)#----Print folder name info to the console
        try:
            os.mkdir(self.NextSubFolderPath)
        except OSError:
            logging.critical("Creation of the directory %s failed", self.NextSubFolderPath) #---Error message
            return(1)
        else:
            logging.info("Successfully created the directory %s ", self.NextSubFolderPath) #----debug message
            return(0)

    # This function makes a folder by 'FolderName'
    # in the destination folder
    # This function is not fully tested yet
    def MakeFolderofName(self,FolderName):
        logging.debug("MakeFolderofName - %s",FolderName) #--------------------------Debug message
        FolderPath = os.path.join(self.ActionDestinationFolder,FolderName)
        logging.info(FolderPath)
        print("Creating ",FolderPath)#----Print folder name info to the console
        try:
            os.mkdir(FolderPath)
        except OSError:
            logging.critical("Creation of the directory %s failed", FolderPath) #----Error message
            return(1)
        else:
            logging.info("Successfully created the directory %s ", FolderPath) #-----debug message
            return(0)

    # This function makes copies of all folders 
    # in the destination folder. They all will be empty.
    # This function is not fully tested yet.
    def MakeAllFolders(self):
        #debug print("copy All folder")
        for root in os.walk(self.ActionSourceFoler, topdown=False):
            logging.debug(root[0]) #-------------------------------------------------debug message
            x = root[0].split("\\") #get the last sub folder
            logging.debug(x[1])
            FolderPath = os.path.join(self.ActionDestinationFolder,x[1]) #create the full path for the destination folder
            logging.debug(FolderPath)  #---------------------------------------------debug message
            try:
                os.mkdir(FolderPath)
            except OSError:
                logging.critical("Creation of the directory %s failed", FolderPath) #----Error message
                return(1)
            else:
                logging.info("Successfully created the directory %s ", FolderPath) #-----debug message
                return(0)
    
    # Add other actions here.
    # <> #

#Actin list is managed by this class. This mainly handles the input CSV file
class AcitonListManager:

    RowNumber = 0 #Save the current row in interest
    MaxRow = 0  #Number of Rows in the excel sheet

    #init will read the full file and record the file name and the max row count.
    def __init__(self, ImportFileName):
        logging.debug("AcitonListManager init called")
        self.CSVFileName = ImportFileName
        with open(ImportFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                #debug print(', '.join(row))
                self.MaxRow += 1
            logging.debug("Total Rows %d", self.MaxRow) #--------------debug message

    #This will read a specific raw and save the value in interestingrows variable.
    #interestingrows will have row zero (title) and values of the selected row
    def ReadRowDirect(self,DirectRowNumber):
        with open(self.CSVFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.interestingrows=[row for idx, row in enumerate(csv_reader) if idx in (0,DirectRowNumber)]
            logging.debug('Read Diract Row - %s',self.interestingrows) #----------------------debug message

    #This will read the Row saved in RowNumber and save the value in interestingrows variable.
    #interestingrows will have row zero (title) and values of the selected row 
    def ReadRow(self):
        with open(self.CSVFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.interestingrows=[row for idx, row in enumerate(csv_reader) if idx in (0,self.RowNumber)]
            logging.debug('Read Row = %s',self.interestingrows) #----------------------debug message

    #This will incrememt the value saved in RowNumber
    def NextRow(self):
        self.RowNumber = self.RowNumber+1
        logging.debug('NextRow = %d',self.RowNumber) #--------------------------------debug message

    #This will decrememt the value saved in RowNumber
    def PreviousRow(self):
        if(self.RowNumber > 0):
            self.RowNumber = self.RowNumber-1
        logging.debug('PreviousRow = %d',self.RowNumber) #---------------------------debug message

    #This will Set the value saved in RowNumber
    def SetRow(self,DirectRowNumber):
        self.RowNumber = DirectRowNumber
        logging.debug('Set Raw = %d',self.RowNumber) #-------------------------------debug message


def main():
    SourseFolder = ""   #---------------------------Source folder name
    DestinationFolder = "" #------------------------Destination folder Name
    PrimeryIndex = 0    #---------------------------This holds the row number of the cvs
    Action = ["NULL","NULL","NULL","NULL","NULL","NULL","NULL","NULL","NULL","NULL"] #only 10 actions supported 
 
    #Here we are trying to open the CVS file.
    #Python behaves stranely when we call the os functins to get the directory where the script is.
    #So we have added some extra code as a workaround
    ScriptDir = os.path.dirname(__file__) #This is the foler with the script. We will search Import.csv in the .\TEST folder
    #Debug print("Script folder -",ScriptDir)
    if (ScriptDir == ""): #if you run this from the same folder that the script exist, you get an empty string in python 3.7.2
        ScriptDir = os.getcwd() # in that case we will use this function to get the absolute path
    logging.info("Script folder - %s",ScriptDir)
    ImportCSVFileName = os.path.join(os.path.split(ScriptDir)[0], 'TEST','Import.csv') #-----debug message
    logging.info("Try to get action list from %s", ImportCSVFileName) #----------------------INFO
    print("Script CSV file = ", ImportCSVFileName) #-----------------------------------------Print the CSV FILE NAME
    NextProcess = AcitonListManager(ImportCSVFileName) # construct the Action manager.
    # TO DO - Get the file name as an input parameter #
    # TO DO - exit if the file does not exits.

    while(NextProcess.RowNumber < (NextProcess.MaxRow-1)):  # We use MaxRow-1 as the Row Zero is the title row and each
                                                            # cycle process two lines.
        logging.debug('RowNumber = %d , MaxRow-1 = %d',NextProcess.RowNumber, NextProcess.MaxRow-1) #------------------------debug message
        i = 0 #save the iteration count
        j = 0 #save the posison of the Action list
        NextProcess.NextRow() #Next row. This moves to row 1
        NextProcess.ReadRow()
        #debug print("Next ROW",NextProcess.interestingrows)
        PrimeryIndex = NextProcess.interestingrows[1][0] #index is in the first column
        SourseFolder = NextProcess.interestingrows[1][1] #Source folder is in the second column
        DestinationFolder = NextProcess.interestingrows[1][2] #Destination folder is in the thrid column
        logging.debug('Source = %s Destination = %s', SourseFolder, DestinationFolder)
        for idx in NextProcess.interestingrows[0]: #-------------go through all the items in row
            #debug print(idx, i)
            if("Action" in idx ):# Look for Action in Title row.. if it's an action..
                Action[j] = NextProcess.interestingrows[1][i]# Get value from Row 1 and Save it in the action list            
                #debug print("Action -". Action[j]) # found one action.
                j += 1
            i += 1
        logging.debug("Action list = %s",Action) #print the action list
        DoAction = ActionManager(SourseFolder,DestinationFolder,PrimeryIndex) #construct the Action Manager
        time.sleep(0.05) #time for the thread to start.
        i = 0 # this is used to control the work flow
        while (i < 10):
            if (Action[i] == "NULL" ): #the empty actions will be null
                logging.debug("Action list done.!") #------------------------debug message
                DoAction.__del__() #distruct the Action manager.
                time.sleep(0.5)# let the thread exit
                break
            else:
                logging.debug(Action[i]) #-----------------------------------debug message
                if (Action[i] == "SELECT_NEXT_SUB_FOLDER_FROM_SRC"): #Select the next Sub Folder
                    if (DoAction.SelectNextSubFilder() == 1):
                        logging.debug("#30001 - File Selection error or task complete") # To Do - Differenciate between Folder Error and Exit
                        DoAction.__del__() #distruct the Action manager.
                        break
                elif (Action[i] == "COPY_SUB_FOLDER_FROM_SRC_TO_DEST"): #Copy the selected Sub Folder to Destination
                    if (DoAction.MakeNextSubFolder() == 1):
                        logging.critical("#30002 - Folder Creation Error - Exit..!") # ---------------------Error message
                        DoAction.__del__() #distruct the Action manager.
                        return(1)
                elif (Action[i] == "SET_FILE_NAME_START_WITH"): #Set the start pattern to file name to match
                    logging.debug("SET_FILE_NAME_START_WITH") #---------------------------------------------debug message
                elif (Action[i] == "SET_FILE_TYPE"): #Set the file extension to match
                    logging.debug("SET_FILE_TYPE") #--------------------------------------------------------debug message
                elif (Action[i] == "COPY_ALL_FILES_OF_TYPE_TO_DEST_SUB_FOLDER"): #copy all files of type to sub folder
                    logging.debug("COPY_ALL_FILES_OF_TYPE_TO_DEST_SUB_FOLDER") #-----------------------------debug message
                elif (Action[i] == "COPY_ALL_FILES_OF_NAME_AND_TYPE_TO_DEST_SUB_FOLDER"): #Copy all files that match to sub foler
                    logging.debug("COPY_ALL_FILES_OF_TYPE_TO_DEST") #---------------------------------------debug message
                elif (Action[i] == "COPY_ALL_FILES_OF_TYPE_TO_DEST"): # Copy all files of type from sub folder to destination
                    logging.debug("COPY_ALL_FILES_OF_TYPE_TO_DEST") #---------------------------------------debug message
                elif (Action[i] == "SET_CSV_FILE_NAME"): #Set the file name for csv created at Destination folder
                    logging.debug("SET_CSV_FILE_NAME")#-----------------------------------------------------debug message
                elif (Action[i] == "ADD_FOLDER_NAME_TO_CSV"): #Add the selected sub foler name to CSV
                    logging.debug("ADD_FOLDER_NAME_TO_CSV") #-----------------------------------------------debug message
                elif ("CREATE_FOLDER_NAME_IN_DEST=>" in Action[i]): # Repease action. Jump to action ID (ACTION_1. ACTION_2)
                    logging.debug("Action = %s",Action[i]) #------------------------------------------------debug message
                    DirectFileName = Action[i].split('>')
                    logging.debug("File Name = %s",DirectFileName[1]) #-------------------------------------debug message
                    if(DoAction.MakeFolderofName(DirectFileName[1]) == 1):
                        logging.critical("#30003 - Folder creation error - Exit..!") #----------------------Error Message
                        DoAction.__del__() #distruct the Action manager.
                        return(1)
                elif ("ACTION" in Action[i]): # Repeat action. Jump to action ID (ACTION_1. ACTION_2)
                    logging.debug("Action = %s",Action[i]) #------------------------------------------------debug message
                    ActionID = Action[i].split('_')
                    logging.debug("Action ID= %s",ActionID[1]) #-----------------------------------------------debug message
                    i = int(ActionID[1])-1 #store the Action ID to i. Action ID is Zero based so we need to -1
                    logging.debug(i) #----------------------------------------------------------------------debug message
                    continue #skip the increment of i
                else:
                    logging.debug("No Acition defined for %s", Action[i]) #------------------------------------debug message
                i += 1


main()
