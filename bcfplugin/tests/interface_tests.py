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
import util as util
import rdwr.uri as uri
import rdwr.topic as topic
import rdwr.reader as reader
import rdwr.writer as writer
import rdwr.markup as markup
import rdwr.interfaces.state as s
import rdwr.project as project
import rdwr.threedvector as tdv
import rdwr.viewpoint as viewpoint
import rdwr.modification as modification
import programmaticInterface as pI
import rdwr.hierarchy as hierarchy


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
            print("Could not open file")
            self.assertTrue(False)

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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].header.files[1]._ifcProjectId
        objectToDelete.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)

        newObject = pI.curProject.topicList[0].header.files[1]._ifcProjectId
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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].header.files[0]
        objectToDelete.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)
        newProject = pI.curProject

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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].header
        objectToDelete.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)

        newProject = pI.curProject
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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].topic.labels[0]
        objectToDelete.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)
        newProject = pI.curProject

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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].viewpoints[0]
        objectToDelete.state = s.State.States.DELETED
        objectToDelete.viewpoint.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)
        newProject = pI.curProject

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
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        objectToDelete = pI.curProject.topicList[0].viewpoints[0]
        objectToDelete.state = s.State.States.DELETED
        pI.deleteObject(objectToDelete)
        newProject = pI.curProject

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


class GetTopicsTest(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./interface_tests"
        self.testBCFName = "Issues-Example_topics_test.bcf"


    def tearDown(self):
        dirPath = os.path.join(util.getSystemTmp(), self.testBCFName)
        project.debug("Deleted tree {}".format(dirPath))
        rmtree(dirPath)


    def test_indexOrdering(self):

        """ Test the sorting of the topic List

        Topics with no index shall be displayed at the end of the list. No index
        is indicated by an index value of -1
        """

        pass

if __name__ == "__main__":
    unittest.main()
