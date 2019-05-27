import sys
import os
from zipfile import ZipFile

def readFile(path: str):

    """
    Tries to open the supplied file (`path`) and returns the ZipFile object.
    If an exception is raised `None` is returned.
    """

    if not os.path.exists(str):
        raise ValueError

    file = None
    try:
        file = ZipFile(path)
    except Exception as e:
        print("The supplied BCF file ({}) could not be opened.\nError:\
                {}".format(path, str(e)))
        return None

    return file

def getDirectories(zipFile: ZipFile):

    """
    Reads out all directory names that are in the zipFile and returns a list of
    strings, where each string represents the name of one directory.
    """

    if zipFile is None:
        raise ValueError

    zipDirectories = list()
    for member in zipFile.infolist():
        if member.filename[-1:] == "/":
            zipDirectories.append(member.filename)

    return zipDirectories

def openProject(zipFile: ZipFile):

    """
    Looks for a project.bcfp file and returns a file handle if found
    """

    if zipFile is None:
        raise ValueError

    projectFileInfo = [ member for member in zipFile.infolist()
                    if "project.bcfp" in member.filename]

    if projectFileInfo is not []:
        return zipFile.open(projectFileInfo[0].filename)
    return None


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        raise ValueError
    with ZipFile(sys.argv[1]) as zipFile:
        print(getDirectories(zipFile))
        print(openProject(zipFile))

