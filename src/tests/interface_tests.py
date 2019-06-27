import os
import sys
import copy
import pprint
import difflib
import unittest
import xmlschema
import dateutil.parser
import xml.etree.ElementTree as ET

from uuid import UUID
from shutil import rmtree
from shutil import copyfile
from xmlschema import XMLSchemaValidationError

sys.path.insert(0, "../")
import bcf.uri as uri
import bcf.util as util
import bcf.topic as topic
import bcf.reader as reader
import bcf.writer as writer
import bcf.markup as markup
import interfaces.state as s
import bcf.project as project
import bcf.threedvector as tdv
import bcf.viewpoint as viewpoint
import bcf.modification as modification
import frontend.programmaticInterface as pI
import interfaces.hierarchy as hierarchy


def setupBCFFile(testFile, testFileDir, testTopicDir, testBCFName):

    os.system("cp {} {}/{}/markup.bcf".format(testFile,
        testFileDir, testTopicDir))
    os.system("cd ./interface_tests && zip -q {} {}/markup.bcf".format(testBCFName,
        testTopicDir))

    return os.path.join(testFileDir, testBCFName)


class DeleteObjectTest(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./interface_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = [ "markup_interface_test.bcf" ]


    def tearDown(self):
        dirPath = os.path.join(util.getSystemTmp(), self.testBCFName)
        project.debug("Deleted tree {}".format(dirPath))
        rmtree(dirPath)


    def test_deleteComment(self):

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Well something happened")

        commentToDelete = pI.curProject.topicList[0].comments[0]
        pI.deleteObject(commentToDelete)

        self.assertTrue(len(pI.curProject.topicList[0].comments)==0)


    def test_deleteIfcProject(self):

        """
        Checks whether after deletion of the IfcProject attribute, the
        attribute holds the default value or not.
        """

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].header.files[1]._ifcProjectId
        objectToDelete.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        newObject = newProject.topicList[0].header.files[1]._ifcProjectId
        newObjectValue = newObject.value
        defaultValue = newObject.defaultValue
        self.assertTrue(newObjectValue == defaultValue)


    def test_deleteFile(self):

        """
        Tests the deletion of a file node.
        """

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].header.files[0]
        objectToDelete.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        searchResult = newProject.searchObject(objectToDelete)
        self.assertTrue(len(newProject.topicList[0].header.files) == 1 and
                searchResult == None)


    def test_deleteHeader(self):

        """
        Tests the deletion of the complete Header element
        """

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].header
        objectToDelete.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        searchResult = newProject.searchObject(objectToDelete)
        self.assertTrue(newProject.topicList[0].header == None and
                searchResult == None)


    def test_deleteLabel(self):

        """
        Tests the deletion of a Label
        """

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].topic.labels[0]
        objectToDelete.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        labelList = newProject.topicList[0].topic.labels
        searchResult = newProject.searchObject(objectToDelete)
        self.assertTrue(len(labelList) == 2 and searchResult == None)


    def test_deleteViewpoint(self):

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].viewpoints[0]
        objectToDelete.state = s.State.States.DELETED
        objectToDelete.viewpoint.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        vpList = newProject.topicList[0].viewpoints
        searchResult = newProject.searchObject(objectToDelete)
        vpFilePath = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir, "viewpoint.bcfv")
        vpFileExists = os.path.exists(vpFilePath)

        project.debug("\n\tlen(vpList)={}\n\tsearchResult={}\n\t"\
                "vpFileExists={}".format(len(vpList), searchResult,
                    vpFileExists))
        self.assertTrue(len(vpList) == 0 and searchResult == None and
                not vpFileExists)


    def test_deleteViewpointReference(self):

        """
        Tests the deletion of a viewpoint reference while preserving the
        underlying viewpoint object
        """

        project.debug("+++++++++++++++++++")
        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        p = reader.readBcfFile(testFile)

        objectToDelete = p.topicList[0].viewpoints[0]
        objectToDelete.state = s.State.States.DELETED
        newProject = pI.deleteObject(p, objectToDelete)

        vpList = newProject.topicList[0].viewpoints
        searchResult = newProject.searchObject(objectToDelete)
        vpFilePath = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir, "viewpoint.bcfv")
        vpFileExists = os.path.exists(vpFilePath)

        project.debug("\n\tlen(vpList)={}\n\tsearchResult={}\n\t"\
                "vpFileExists={}".format(len(vpList), searchResult,
                    vpFileExists))
        self.assertTrue(len(vpList) == 0 and searchResult == None and
                vpFileExists)


if __name__ == "__main__":
    unittest.main()
