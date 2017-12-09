#!/usr/bin/python

# TODO: use argparse lib

import sys, os, re, shutil, admin, ctypes

backgroundPath = os.path.join("C:/Windows/System32/oobe/info/Backgrounds/", "backgroundDefault.jpg")


class disableFileSystemRedirection:
    _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
    _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

    # enables access to system32 files
    def __enter__(self):
        self.old_value = ctypes.c_long()
        self.success = self._disable(ctypes.byref(self.old_value))

    def __exit__(self, type, value, traceback):
        if self.success:
            self._revert(self.old_value)


def static_var(varname, value):
    def decorate(func):
        setattr(func, varname, value)
        return func

    return decorate


@static_var("stage", 0)
def printStage(info):
    printStage.stage += 1

    print("[STEP " + str(printStage.stage) + "] " + info)


def displayHelp():
    print("""Login background wallpaper changer
    
    Actions:
    <>              Display (this) help menu
    -h
    --help
    
    <FILEPATH>      Set FILEPATH
    -f              
    --file          
    
    -d              Set default Windows 7 wallpaper
    --default       
    """)


def setDefaultBackground():
    if os.path.exists(backgroundPath):
        shutil.move(backgroundPath, backgroundPath + "_BKP")
        printStage("Created backup of background file: " + backgroundPath + "_BKP")

    printStage("Set default background")


def getFilePath():
    if re.match(re.compile("(-f|--file)", re.IGNORECASE), sys.argv[1]):
        if len(sys.argv) < 3:
            print("ERROR: File path not specified")
            exit(1)
        return os.path.abspath(sys.argv[2])
    else:
        return os.path.abspath(sys.argv[1])


def getSizeInKB(file):
    return os.path.getsize(file) / 1024


def replaceLoginBackgroundWallpaper(filePath):
    if os.path.exists(backgroundPath):
        shutil.move(backgroundPath, backgroundPath + "_BKP")
        printStage("Created backup of background file: " + backgroundPath + "_BKP")

    shutil.copyfile(filePath, backgroundPath)
    printStage("Replaced background")


def enableSystemFilesAccess():
    disableFileSystemRedirection().__enter__()
    testPath = 'C:\\Windows\\System32\\oobe\\info\\Backgrounds'
    # testPath = 'C:\\Windows\\System32\\GroupPolicy\\Machine'
    if not os.path.exists(testPath):
        print("ERROR: Cannot access system32 files!")
        exit(1)


def checkIfFilePathIsValid(filePath):
    if not os.path.exists(filePath):
        print("ERROR: Invalid input file!")
        exit(1)


def checkIfFileSizeIsValid(filePath):
    if getSizeInKB(filePath) >= 256:
        print("WARNING: File size should be less than 256KB (Windows 7 restriction).\n"
              "Operation might be not successful\n\n")
        while True:
            choice = input("Continue? [Y/N] ")
            if re.match("(?i)(y|yes)", choice):
                return
            else:
                exit(0)

def main():
    if len(sys.argv) == 1 or re.match(re.compile("(-h|--help)", re.IGNORECASE), sys.argv[1]):
        displayHelp()
        exit(0)

    printStage("Checked user priviliges.")

    enableSystemFilesAccess()
    printStage("Checked access to system files.")

    if re.match(re.compile("(-d|--default)", re.IGNORECASE), sys.argv[1]):
        setDefaultBackground()
        printStage("Finished!")
        exit(0)

    filePath = getFilePath()

    checkIfFilePathIsValid(filePath)
    printStage("Checked, if input file is valid.")

    checkIfFileSizeIsValid(filePath)
    printStage("Checked. if input file size is valid.")

    replaceLoginBackgroundWallpaper(filePath)

    printStage("Finished!")


if __name__ == "__main__":
    main()
