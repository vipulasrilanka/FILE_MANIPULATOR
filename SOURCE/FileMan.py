# !/usr/bin/python

import os
import csv
import threading
import time

#All the file/folder actions are implemented in this class.
class ActionManager:

    # constructor function
    # This will initialize all the status maintainig variables and
    # will start the file/folder read thread.   
    def __init__(self, ActionSourceFoler,ActionDestinationFolder, RowID):
        self.ActionDestinationFolder = ActionDestinationFolder #--Save the Destination folder for this action round
        self.ActionSourceFoler = ActionSourceFoler #--------------Save the source folder for this action round
        self.FlagReadNextSubFolder = False #----This is a local implementation of a lock. Set to False to hold the thread.
        self.FlagNextSubFolderReady = False #---This is a local implementation of a lock. This will be set by the thread.
        self.KeepThreadAlive = True #---------------------Thread will exit if this flag is false.
        self.FlagSubFolderTraverseThreadExit = False #----Indicator for the existance of the thread.
        self.SubFolderReadThread = threading.Thread(target = self.SubFolderTraverseThread, args = (RowID, ))
        self.SubFolderReadThread.start() #----------------Start the thread

    # Distructor function
    # this will stop the file read thread
    def __del__(self):
        print("Action Manager Distruct called")
        self.KeepThreadAlive = False #Need to stop the thred
        self.FlagReadNextSubFolder = True #--Release the lock so that the thread can run.
        self.SubFolderReadThread.join() #wait for the thread to exit
        print("Action Manager Distructed...")

    # This thread goes through each sub folder and will update 
    # 'NextSubFolderPath' variable with the folder name.
    # This thread creates 'NextSubFolderPath' so this variable can not be 
    # accessed before this thread goes through one round.
    def SubFolderTraverseThread(self,arg):
        print("SubFolderTraverseThread started with", arg)
        while(self.FlagReadNextSubFolder == False): #--Wait for the lock to release
            time.sleep(0.01)
        # we come here as the FlagReadNextSubFolder is True. 
        self.FlagReadNextSubFolder = False #reset the Flag to prevent re-run
        print("SubFolderTraverseThread continue...")
        if(self.KeepThreadAlive == False): #---check for exit signal.
            print("#10001 - SubFolderTraverseThread - Parent is dead")
            self.FlagSubFolderTraverseThreadExit = True
            print("#10002 - exit From SubFolderTraverseThread")   #--Exit from thread.
            return()

        for root in os.walk(self.ActionSourceFoler, topdown=False):
            print (root[0])
            if (root[0] == self.ActionSourceFoler):
                print ("Root folder detected")
                break
            x = root[0].split("\\") #get the last sub folder
            print(x[1])
            self.NextSubFolderPath = os.path.join(self.ActionDestinationFolder,x[1]) #create the full path for the destination folder
            print("SubFolderTraverseThread",self.NextSubFolderPath) #print new folder path
            self.FlagNextSubFolderReady = True #-----Indicate that the folder name is ready.
            while(self.FlagReadNextSubFolder == False): #--Wait for the next lock release.
                time.sleep(0.01)
            # we come here as the FlagReadNextSubFolder is True.
            self.FlagReadNextSubFolder = False #reset the Flag to prevent re-run
            
            if(self.KeepThreadAlive == False): #---check for exit signal.
                print("SubFolderTraverseThread - Parent is dead")
                break
        if (self.KeepThreadAlive == True):
            print("SubFolderTraverseThread - No more Folders to report..!")
        self.FlagSubFolderTraverseThreadExit = True
        print("exit From SubFolderTraverseThread")   #--Exit from thread.

    # This function selects the next sub folder
    # NextSubFolderPath will point to the Destination folder
    def SelectNextSubFilder(self):
        print("Select Next SubFilder- Let the thread run once")
        self.FlagReadNextSubFolder = True #--Release the lock for the read thread to run
        while(self.FlagNextSubFolderReady == False): #Wait for the Folder name
            time.sleep(0.01)
            if(self.FlagSubFolderTraverseThreadExit == True):
                print("SubFolderTraverseThread Terminated.")            
                return(1)
        # we come here as the FlagNextSubFolderReady is True. 
        self.FlagNextSubFolderReady = False #reset the Flag
        print("SelectNextSubFilder -",self.NextSubFolderPath) #Print the folder name we got
        return(0)

    # This function will get the next sub folder name and create an empty folder 
    # in the destination folder path
    def MakeNextSubFolder(self):
        try:
            os.mkdir(self.NextSubFolderPath)
        except OSError:
            print ("Creation of the directory %s failed" % self.NextSubFolderPath)
            return(1)
        else:
            print ("Successfully created the directory %s " % self.NextSubFolderPath)
            return(0)

    # This function makes a folder by 'FolderName'
    # in the destination folder
    def MakeFolderofName(self,FolderName):
        #debug print("copy folder", FolderName)
        FolderPath = os.path.join(self.ActionDestinationFolder,FolderName)
        #debug print(FolderPath)
        try:
            os.mkdir(FolderPath)
        except OSError:
            print ("Creation of the directory %s failed" % FolderPath)
            return(1)
        else:
            print ("Successfully created the directory %s " % FolderPath)
            return(0)

    # This function makes copies of all folders 
    # in the destination folder. They all will be empty.
    def MakeAllFolders(self):
        #debug print("copy All folder")
        for root in os.walk(self.ActionSourceFoler, topdown=False):
            #debug print (root[0])
            x = root[0].split("\\") #get the last sub folder
            #debug print(x[1])
            FolderPath = os.path.join(self.ActionDestinationFolder,x[1]) #create the full path for the destination folder
            #debug print(FolderPath) #print new folder path
            try:
                os.mkdir(FolderPath)
            except OSError:
                print ("Creation of the directory %s failed" % FolderPath)
                return(1)
            else:
                print ("Successfully created the directory %s " % FolderPath)
        return(0)
    
    # Add other actions here.
    # <> #

#Actin list is managed by this class. This mainly handles the input CSV file
class AcitonListManager:

    RowNumber = 0 #Save the current row in interest
    MaxRow = 0  #Number of Rows in the excel sheet

    #init will read the full file and record the file name and the max row count.
    def __init__(self, ImportFileName):
        self.CSVFileName = ImportFileName
        with open(ImportFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                #debug print(', '.join(row))
                self.MaxRow += 1
            print("Total Rows", self.MaxRow)

    #This will read a specific raw and save the value in interestingrows variable.
    #interestingrows will have row zero (title) and values of the selected row
    def ReadRowDirect(self,DirectRowNumber):
        with open(self.CSVFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.interestingrows=[row for idx, row in enumerate(csv_reader) if idx in (0,DirectRowNumber)]
            #debug print(self.interestingrows)

    #This will read the Row saved in RowNumber and save the value in interestingrows variable.
    #interestingrows will have row zero (title) and values of the selected row 
    def ReadRow(self):
        with open(self.CSVFileName) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            self.interestingrows=[row for idx, row in enumerate(csv_reader) if idx in (0,self.RowNumber)]
            #debug print(self.interestingrows)

    #This will incrememt the value saved in RowNumber
    def NextRow(self):
        self.RowNumber = self.RowNumber+1
        #debug print(self.RowNumber)

    #This will decrememt the value saved in RowNumber
    def PreviousRow(self):
        if(self.RowNumber > 0):
            self.RowNumber = self.RowNumber-1
        #debug print(self.RowNumber)

    #This will Set the value saved in RowNumber
    def SetRow(self,DirectRowNumber):
        self.RowNumber = DirectRowNumber
        #debug print(self.RowNumber)


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
    print("Script folder -",ScriptDir)
    ImportCSVFileName = os.path.join(os.path.split(ScriptDir)[0], 'TEST','Import.csv')
    print("Try to get action list from", ImportCSVFileName)
    NextProcess = AcitonListManager(ImportCSVFileName) # construct the Action manager.
    # TO DO - Get the file name as an input parameter #

    while(NextProcess.RowNumber < (NextProcess.MaxRow-1)):  # We use MaxRow-1 as the Row Zero is the title row and each
                                                            # cycle process two lines.
        print(NextProcess.RowNumber, "<", NextProcess.MaxRow-1)
        i = 0 #save the iteration count
        j = 0 #save the posison of the Action list
        NextProcess.NextRow() #Next row. This moves to row 1
        NextProcess.ReadRow()
        #debug print("Next ROW",NextProcess.interestingrows)
        PrimeryIndex = NextProcess.interestingrows[1][0] #index is in the first column
        SourseFolder = NextProcess.interestingrows[1][1] #Source folder is in the second column
        DestinationFolder = NextProcess.interestingrows[1][2] #Destination folder is in the thrid column
        print("Source =", SourseFolder,"\nDestination =", DestinationFolder)
        for idx in NextProcess.interestingrows[0]: #-------------go through all the items in row
            #debug print(idx, i)
            if("Action" in idx ):# Look for Action in Title row.. if it's an action..
                Action[j] = NextProcess.interestingrows[1][i]# Get value from Row 1 and Save it in the action list            
                #debug print("Action -". Action[j]) # found one action.
                j += 1
            i += 1
        print("Action list =",Action) #print the action list
        DoAction = ActionManager(SourseFolder,DestinationFolder,PrimeryIndex) #construct the Action Manager
        time.sleep(0.05) #time for the thread to start.
        i = 0 # this is used to control the work flow
        while (i < 10):
            if (Action[i] == "NULL" ): #the empty actions will be null
                print("Action list done.!")
                DoAction.__del__() #distruct the Action manager.
                time.sleep(0.5)# let the thread exit
                break
            else:
                print(Action[i])
                if (Action[i] == "SELECT_NEXT_SUB_FOLDER_FROM_SRC"): #Select the next Sub Folder
                    if (DoAction.SelectNextSubFilder() == 1):
                        print("#30001 - File Selection error or task complete") # To Do - Differenciate between Folder Error and Exit
                        DoAction.__del__() #distruct the Action manager.
                        break
                elif (Action[i] == "COPY_SUB_FOLDER_FROM_SRC_TO_DEST"): #Copy the selected Sub Folder to Destination
                    if (DoAction.MakeNextSubFolder() == 1):
                        print("#30002 - Folder Creation Error - Exit..!")
                        DoAction.__del__() #distruct the Action manager.
                        return(1)
                elif (Action[i] == "SET_FILE_NAME_START_WITH"): #Set the start pattern to file name to match
                    print("SET_FILE_NAME_START_WITH")
                elif (Action[i] == "SET_FILE_TYPE"): #Set the file extension to match
                    print("SET_FILE_TYPE")
                elif (Action[i] == "COPY_ALL_FILES_OF_TYPE_TO_DEST_SUB_FOLDER"): #copy all files of type to sub folder
                    print("COPY_ALL_FILES_OF_TYPE_TO_DEST_SUB_FOLDER")
                elif (Action[i] == "COPY_ALL_FILES_OF_NAME_AND_TYPE_TO_DEST_SUB_FOLDER"): #Copy all files that match to sub foler
                    print("COPY_ALL_FILES_OF_TYPE_TO_DEST")
                elif (Action[i] == "COPY_ALL_FILES_OF_TYPE_TO_DEST"): # Copy all files of type from sub folder to destination
                    print("COPY_ALL_FILES_OF_TYPE_TO_DEST")
                elif (Action[i] == "SET_CSV_FILE_NAME"): #Set the file name for csv created at Destination folder
                    print("SET_CSV_FILE_NAME")
                elif (Action[i] == "ADD_FOLDER_NAME_TO_CSV"): #Add the selected sub foler name to CSV
                    print("ADD_FOLDER_NAME_TO_CSV")
                elif ("CREATE_FOLDER_NAME_IN_DEST=>" in Action[i]): # Repease action. Jump to action ID (ACTION_1. ACTION_2)
                    print ("Action =",Action[i])
                    DirectFileName = Action[i].split('>')
                    print("File Name =",DirectFileName[1])
                    if(DoAction.MakeFolderofName(DirectFileName[1]) == 1):
                        print("#30003 - Folder creation error - Exit..!")
                        DoAction.__del__() #distruct the Action manager.
                        return(1)
                elif ("ACTION" in Action[i]): # Repease action. Jump to action ID (ACTION_1. ACTION_2)
                    print ("Action =",Action[i])
                    ActionID = Action[i].split('_')
                    print("Action ID=",ActionID[1])
                    i = int(ActionID[1])-1 #store the Action ID to i. Action ID is Zero based so we need to -1
                    print(i)
                    continue #skip the increment of i
                else:
                    print("No Acition defined for", Action[i])
                i += 1


main()
