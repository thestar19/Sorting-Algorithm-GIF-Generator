import sys

#Define basic trace_function
def show_trace(event=""):
    print("An error has occured, printing useful info:")
    print(sys.version)
    print(sys.version_info)
    print(event)
    sys.exit(0)

#Carefully import stuff
try:
    from random import randint
    from time import time
    from algs import algorithmsDict
    import display as display
    from os import rmdir, walk, getcwd, system, mkdir, remove,path
    from gc import collect
    import imageio.v3 as iio
    #import av #Temporary, this should be changed to only import needed functions
    import pygame
except ImportError:
    show_trace()


#Global variables
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

TEXTLOG = []
TEXTLOG_UPDATE = True
DEBUG = False
CURRENT_OUTPUT_FORMATS = ["GIF","MP4"]

#printL types:
# 1 = normal log message
# 2 = reserved for progress indication
# 3 = Warning message
# 4 = Reserved for debug use

#Generating gifs requires placing files in subfolder and then loading them.
#This deletes everything except gif
def deleteTempFiles():
    try:
        myFiles = []
        myDir = []
        for pathnames,dirnames,filenames in walk("pictures"):
            myFiles.extend(filenames)
            myDir.extend(dirnames)
        for files in myFiles:
            remove("pictures/" + files)
        for directories in myDir:
            rmdir("pictures/" + directories)
    except:
        raise EIO("Could not delete files in subfolder!")

# For some uses, having an existing sorting.gif file is a problem
# Therefore, this function deletes that file using os lib
def deleteExistingFile(name):
    if path.exists(name):
        try:
            remove(name)
            printL(1, f"Removed {name}")
        except:
            printL(3,f"Could not remove {name}")

#Call function with type according to above (eg 0 for normal log)
# and a string with whatever should be added to log
def printL(type,addition):
    global TEXTLOG
    global TEXTLOG_UPDATE
    TEXTLOG_UPDATE = True
    TEXTLOG.append((type,addition))

# Function that correctly inserts new progress item into log
def printProgress(progress):
    global TEXTLOG
    global TEXTLOG_UPDATE
    TEXTLOG_UPDATE = True
    #Insert at pos 0
    TEXTLOG.insert(0,(2, progress))

# Prints progress bar, only to be called if
# in log values of type 2 exists and terminal is clear
def printProgressBar(currentValue):
    print("Progress:" +  str(currentValue) + "%")
    print("""[""",end="")
    progressCounter = 0
    for i in range(0,int(currentValue),5):
        print("""#""",end="")
        progressCounter +=1
    for i in range(0,20-progressCounter):
        print("""·""", end="")
    print("""]""")

def printSign():
    print("""
 _______         _______         _______ 
(  ____ \       (  ___  )       (  ____ |
| (    \/       | (   ) |       | (    \/
| (_____  _____ | (___) | _____ | |      
(_____  )(_____)|  ___  |(_____)| | ____ 
      ) |       | (   ) |       | | \_  )
/\____) |       | )   ( |       | (___) |
\_______)       |/     \|       (_______)
                                         """)

def printLimitations(myType):
    printL(myType,"Limitations exceeded. For reference see below")
    printL(myType,"Current program limitations:")
    printL(myType,"Size < 1000")
    printL(myType, "if display values in bar, Size < 20")
    printL(myType,"Loops must be < 9999, set to 0 for Inf")
# Given a type, removes all entries of that type from log

def checkVersionOfPYAV():
    with iio.imopen("temp.mp4","w",plugin="pyav") as newVideo:
        exists = False
        for attr in dir(newVideo):
            if "init_video_stream" == attr:
                exists = True
        if exists:
            printL(4,"Correct version of pyav detected")
            #This is kinda wierd, but is really just so control-flow works correctly.
            return
        else:
            print("Incorrect version of pyav detected")
            print("Exiting program")
    deleteExistingFile("temp.mp4")
    sys.exit(0)

def deleteType(theType):
    global TEXTLOG
    counter = 0
    while True:
        if counter >= len(TEXTLOG)-2:
            return True
        type,value = TEXTLOG[counter]
        if type == theType:
            TEXTLOG.pop(counter)
            counter = counter-3
        counter +=1

# Function that clears terminal and write new info.
# To activate, set textLogUpdate = True, usually it will run shortly
def updateDisplay():
    global TEXTLOG
    global TEXTLOG_UPDATE
    # Without this, much resources would be wasted on rewriting log terminal display
    if not TEXTLOG_UPDATE:
        return -1
    TEXTLOG_UPDATE = False
    #runTime = time.strftime("%H:%M:%S", time.localtime(time.time() - startUpTime - 60 * 60))
    system("clear")
    printSign()
    #print(str(runTime))
    maxProgress = -1
    for type,value in TEXTLOG:
        if type == 2:
            if value > maxProgress:
                maxProgress = value
    if -1 < maxProgress < 100:
        printProgressBar(maxProgress)
        print("--------------------------------------------")
    for type,value in TEXTLOG:
        if type == 1:
            print(value)
        if type == 3:
            print(f"{bcolors.WARNING} Warning: {value} {bcolors.ENDC}")
        if type == 4 and DEBUG:
            print(f"{bcolors.OKBLUE} Debug: {value} {bcolors.ENDC}")

def writeGifFile(listOfImages,numberOfLoops):
    newGif = iio.imopen('sorting.gif', "w", plugin="pillow")
    newGif.write(listOfImages, duration=int(display.delay), loop=numberOfLoops, optimize=True)
    newGif.close()

# Create GIF using existing files
def createGIF(counter,SCREENSHOT_FILENAME):
    updateDisplay()
    #Idea is that pictures are generated with numbers 0 to some MAX
    printL(1,"Trying to generate GIF, this may freeze the program and take a while")
    fileNames = []
    for i in range(0,counter):
        fileNames.append(f"{SCREENSHOT_FILENAME}{str(i)}.jpg")
    #This will start to load in individual pictures into gif engine
    numberOfLoops = 0
    deleteExistingFile("sorting.gif")
    printL(1, f"Adding {str(display.delay)} ms delay for each image in GIF")
    printL(4, "Accurate gif settings is applied \n Therefore every frame from animation will be in GIF.")
    printL(4, "This increases time to generate, but also more accurately displays how sorting function works.")
    printL(4, f"Total number of recorded images: {str(len(fileNames))}")
    updateDisplay()
    listOfImages = []
    for (counter, filename) in enumerate(fileNames):
        if counter % 100 == 1:
            updateDisplay()
        listOfImages.append(iio.imread(filename))
        printProgress(int(((counter) / len(fileNames)) * 100*0.7))
    printL(1, "Writing GIF to disk")
    writeGifFile(listOfImages, display.loopBox.get_value())
    printProgress(100)
    updateDisplay()
    #Del latest list, this does NOT decrease current RAM usage,
    #but makes next round use the same memory area instead
    printL(1,"Cleaning up remaining files")
    del listOfImages
    del fileNames
    collect()
    printL(1,"GIF generation complete as sorting.gif")
    #Delete all files in folder
    deleteTempFiles()
    deleteType(2)
    updateDisplay()

# Create MP4 using existing files
def createMP4(counter,SCREENSHOT_FILENAME):
    updateDisplay()
    #Idea is that pictures are generated with numbers 0 to some MAX
    printL(1,"Trying to generate MP4, this may freeze the program and take a while")
    fileNames = []
    for i in range(0,counter):
        fileNames.append(f"{SCREENSHOT_FILENAME}{str(i)}.jpg")
    #This will start to load in individual pictures into gif engine
    numberOfLoops = 0
    deleteExistingFile("sorting.mp4")
    printL(1, f"Adding {str(display.delay)} ms delay for each image in MP4")
    printL(4, "Accurate MP4 settings is applied \n Therefore every frame from animation will be in MP4.")
    printL(4, "This increases time to generate, but also more accurately displays how sorting function works.")
    printL(4, f"Total number of recorded images: {str(len(fileNames))}")
    printL(4,f"Ignoring looping options because MP4 format does not support")
    updateDisplay()
    with iio.imopen("sorting.mp4","w",plugin="pyav") as newVideo:
        newVideo.init_video_stream("mpeg4",fps=30)
        frameCounter = int((display.delay * 30)/1000) #Formula to get number of repeat images for delay
        if frameCounter < 1:
            frameCounter = 1
        for (counter, filename) in enumerate(fileNames):
            if counter % 100 == 1 or counter < 200:
                updateDisplay()
            aFrame = iio.imread(filename) #So we don't read it more than once
            for _ in range(frameCounter):
                newVideo.write_frame(aFrame)
            printProgress(int(((counter) / len(fileNames)) * 100))
    printL(1, "Writing MP4 to disk")
    printProgress(100)
    updateDisplay()
    #Del latest list, this does NOT decrease current RAM usage,
    #but makes next round use the same memory area instead
    printL(1,"Cleaning up remaining files")
    del fileNames
    collect()
    printL(1,"MP4 generation complete as sorting.mp4")
    #Delete all files in folder
    deleteTempFiles()
    deleteType(2)
    updateDisplay()

#Given a list of filenames, it returns what number the highest file has.
def getMaxNumber(files):
    currentMax  = -1
    for item in files:
        myNumber = int(item[len(SCREENSHOT_FILENAME):len(item)-4])
        if myNumber > currentMax:
            currentMax = myNumber
    return currentMax

#Given a picture counter & screenshot item, takes and saves a picture of animation
def takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot):
    if not display.includeSettingsInOutput:
        pygame.image.save(screenshot, f"{SCREENSHOT_FILENAME}{str(GIF_picture_counter)}.jpg")
    else:
        pygame.image.save(display.screen, f"{SCREENSHOT_FILENAME}{str(GIF_picture_counter)}.jpg")

# We need a place to write pictures currently
# Yes, this is bad design.
# Checks if picture folder exists, and if not it is created.
def createPicturesFolder():
    myDir = []
    for pathnames,dirnames,filenames in walk(getcwd()):
            myDir.extend(dirnames)
    for directory in myDir:
        if directory == "pictures":
            return -1
    try:
        mkdir("pictures")
    except:
        raise Exception("Could not create pictures folder")

def main():
    updateDisplay()
    printL(4,"Function import and program load completed")
    SCREENSHOT_FILENAME = "pictures/screenshot" #+ a counter number + JPG
    
    numbers = []
    running = True
    display.algorithmBox.add_options(list(algorithmsDict.keys()))
    display.outputFormatBox.add_options(CURRENT_OUTPUT_FORMATS)

    alg_iterator = None
    
    #One keeps track of how many files have been created, the other when to skip images
    GIF_picture_counter = 0
    GIF_skip_image_counter = 0

    #Used for rendering window
    GIF_WINDOW_SIZE = (900, 400)
    
    #Just to make sure nothing from prev runs is left
    deleteTempFiles()
    
    #Create pictures if it does not exists
    createPicturesFolder()
    
    while running:
        updateDisplay()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and display.do_sorting:
                display.paused = not display.paused
                display.timer_space_bar = time()

            display.updateWidgets(event)

        if display.playButton.isActive: # play button clicked
            try:
                if int(display.sizeBox.text) > 1000 or \
                        (display.displayValuesInOutput and int(display.sizeBox.text) > 49) and \
                        (display.loopBox.get_value() < 9999):
                    # This is limitation because of RAM. size = 100 needs 2GB of RAM, so 120 is for some reason significantly higher
                    printL(3,("Halting output creation"))
                    printLimitations(3)
                else:
                    printL(1,"-------------------------------")
                    printL(1,("Creating animation"))
                    GIF_picture_counter = 0
                    GIF_picture_counter = 0
                    display.do_sorting = True
                    display.playButton.isActive = False
                    current_alg = display.algorithmBox.get_active_option()
                    display.numBars = int(display.sizeBox.text)
                    if display.numBars > 20 and display.displayValuesInOutput:
                        printL(3,"Will not render values in bars because number of bars > 20")
                    numbers = [randint(10, 400) for i in range(display.numBars)]  # random list to be sorted
                    alg_iterator = algorithmsDict[current_alg](numbers, 0, display.numBars - 1)  # initialize iterator
                display.playButton.isActive = False
            except ValueError:
                printL(4,"Text in size field is not a number")

        if display.stopButton.isActive: # stop button clicked
            printL(1,("Stopping animation"))
            display.stopButton.isActive = False
            display.do_sorting = False
            display.paused = False
            try: # deplete generator to display sorted numbers
                while True:
                    numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
            except StopIteration:
                pass
            #Delete temp files. No gif is possible because early stop
            deleteTempFiles()
            GIF_picture_counter = 0
            GIF_skip_image_counter = 0
                
        #GIF may need own thing
        screenshot = pygame.Surface(GIF_WINDOW_SIZE)
        screenshot.blit(display.screen, (0,0))
        
        if display.do_sorting and not display.paused: # sorting animation
            try:
                numbers, redBar1, redBar2, blueBar1, blueBar2 = next(alg_iterator)
                display.drawInterface(numbers, redBar1, redBar2, blueBar1, blueBar2)
                #Pictures needs to be generated and saved temporarily
                if int(display.sizeBox.text) <= 200:
                    takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot)
                    GIF_picture_counter +=1
                #If size > 200, then we need to take drastically less pictures
                else:
                    if int(GIF_skip_image_counter) % int(5) == 1:
                        takePicture(SCREENSHOT_FILENAME,GIF_picture_counter,screenshot)
                        GIF_picture_counter +=1
                        GIF_skip_image_counter = 0
                    GIF_skip_image_counter +=1
                    
            except StopIteration:
                #If program stops because end of sorting, gif needs to be created if selected
                #Create green bars
                a_set = set(range(display.numBars))
                display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)
                #Make sure they are saved for a second
                takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
                GIF_picture_counter += 1
                takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
                GIF_picture_counter += 1
                takePicture(SCREENSHOT_FILENAME, GIF_picture_counter, screenshot)
                GIF_picture_counter += 1
                # Call function for GIF
                if display.outputFormatBox.get_active_option() == "GIF":
                    createGIF(GIF_picture_counter,SCREENSHOT_FILENAME)
                else:
                    createMP4(GIF_picture_counter,SCREENSHOT_FILENAME)
                #Reset counter
                GIF_picture_counter = 0
                GIF_skip_image_counter = 0
                # Turn off sorting
                display.do_sorting = False
                
        elif display.do_sorting and display.paused: # animation paused
            display.drawInterface(numbers, -1, -1, -1, -1)
        else: # no animation
            a_set = set(range(display.numBars))
            display.drawInterface(numbers, -1, -1, -1, -1, greenRows=a_set)

if __name__ == '__main__':
    available_args = ["-f","-d","-s","-include"]
    if sys.argv[1] == "help" or sys.argv[1] == "HELP" or sys.argv[1] == "Help":
        print(f"Sorting Algorithm GIF Generator by TheStar19")
        print(f"A fork of Sorting Algorithm Visualizer by LucasPilla")
        print(f"Available args:{available_args}")
        sys.exit(0)
    if sys.argv[1] == "-v" or sys.argv[1] == "-V":
        printL(4,"Debug enabled")
        DEBUG = True
    #Check if correct software is installed
    checkVersionOfPYAV()
    #Check for any args in program init
    if len(sys.argv) > 2:
        all_args = sys.argv.copy()
        all_args.pop(0)
        print("--------------------")
        instructions = []
        while True:
            if len(all_args) > 1:
                if all_args[0] in available_args:
                    instructions.append((all_args.pop(0),all_args.pop(0)))
                else:
                    print(f"Incorrects arg options")
                    print(f"Available args:{available_args}")
                    sys.exit(0)
            else:
                break
        output_format = "GIF"
        output_delay = 1
        output_size = 100
        for inst,value in instructions:
            print(inst)
            #Check for output format
            if inst == "-f" and value in CURRENT_OUTPUT_FORMATS:
                output_format = value
            elif inst == "-f" :
                print(f"Incorrect args, -f value {value} is not supported")
                break
            #Check for delay value
            elif inst == "-d" and 1 < int(value) < 3000:
                output_delay = int(value)
            elif inst == "-d" :
                print(f"Incorrect args, -d value {value} is not an int between 1 and 3000")
                break
            #Check for size value
            elif inst == "-s" and 5 < int(value) < 1000:
                output_size = int(value)
            elif inst == "-s":
                print(f"Incorrect args, -s value {value} is not an int between 5 and 1000")
                break
            #Check for including numbers in bars or entire GUI
            elif inst == "-include" and value == "numbers":
                output_size = int(value)
            elif inst == "-include":
                print(f"Incorrect args, -include value {value} is not text \"numbers\"")
                break
        sys.exit()
        #all_args = sys.argv.split[]
    main()


