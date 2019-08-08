import os
import sys
import copy
import pprint
import difflib
import logging
import unittest
import xmlschema
import dateutil.parser
import xml.etree.ElementTree as ET

from uuid import UUID
from shutil import rmtree
from shutil import copyfile
from xmlschema import XMLSchemaValidationError

sys.path.insert(0, "../../") # plugin root
sys.path.insert(0, "../") # source root
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
import rdwr.interfaces.hierarchy as hierarchy

logger = bcfplugin.createLogger(__name__)


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
        rmtree(dirPath)


    def test_deleteComment(self):

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


    def test_deleteCopiedComment(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath,
                self.testFileDir,
                self.testTopicDir,
                self.testBCFName)
        if pI.openProject(testFile) == pI.OperationResults.FAILURE:
            print("Could not open file")
            self.assertTrue(False)

        logger.debug("Id of created project is {}".format(id(pI.curProject)))
        topics = [ topic[1] for topic in pI.getTopics() ]
        comments = [ comment[1] for comment in pI.getComments(topics[0]) ]

        commentToDelete = comments[0]
        logger.debug("Id of the comment copy {}".format(id(commentToDelete)))
        pI.deleteObject(commentToDelete)

        self.assertTrue(len(pI.curProject.topicList[0].comments)==0)


    def test_deleteIfcProject(self):

        """
        Checks whether after deletion of the IfcProject attribute, the
        attribute holds the default value or not.
        """

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
        elementHierarchy = hierarchy.Hierarchy.checkAndGetHierarchy(objectToDelete)
        logger.debug("Hierarchy of element {}".format(elementHierarchy))

        newObject = pI.curProject.topicList[0].header.files[1]._ifcProjectId
        newObjectValue = newObject.value
        defaultValue = newObject.defaultValue
        self.assertTrue(newObjectValue == defaultValue)


    def test_deleteFile(self):

        """
        Tests the deletion of a file node.
        """

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

        self.assertTrue(len(vpList) == 0 and searchResult == None and
                not vpFileExists)


    def test_deleteViewpointReference(self):

        """
        Tests the deletion of a viewpoint reference while preserving the
        underlying viewpoint object
        """

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

        self.assertTrue(len(vpList) == 0 and searchResult == None and
                vpFileExists)


class GetTopicsTest(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./interface_tests"
        self.testBCFName = "Issues-Example_topics_test.bcf"


    def tearDown(self):
        dirPath = os.path.join(util.getSystemTmp(), self.testBCFName)
        try:
            rmtree(dirPath)
        except:
            pass


    def test_indexOrdering(self):

        """ Test the sorting of the topic List

        Topics with no index shall be displayed at the end of the list. No index
        is indicated by an index value of -1
        """

        pass


class ModifyElementTests(unittest.TestCase):

    def retrieveTopics(self):
        return [ topic[1] for topic in self.plugin.getTopics() ]


    def retrieveComments(self, topic):
        return [ comment[1] for comment in self.plugin.getComments(topic) ]


    def setUp(self):
        import bcfplugin as p
        self.plugin = p
        self.plugin.openProject("./interface_tests/Issues_BIMcollab_Example.bcf.original")
        self.topics = self.retrieveTopics()


    def tearDown(self):
        del self.plugin


    def test_modifiedCommentState(self):

        """ Test whether the state of the modified element is set back to
        ORIGINAL"""

        comments = self.retrieveComments(self.topics[0])
        commentToModify = comments[0]

        commentToModify.comment = "Hello my name is... Slim Shaaaaadyyyy"
        self.plugin.modifyElement(commentToModify, author="hello@bye.com")

        newTopics = self.retrieveTopics()
        newComments = self.retrieveComments(newTopics[0])
        updatedComment = newComments[0]

        logger.debug(updatedComment.state)
        self.assertTrue(updatedComment.state == s.State.States.ORIGINAL)


    def test_modifyComment(self):

        """ Test whether a comment text gets updated in the data model """

        comments = self.retrieveComments(self.topics[0])
        commentToModify = comments[0]

        newText = "Hello my name is... Slim Shaaaaadyyyy"
        newAuthor = "a@b.c"
        commentToModify.comment = newText
        self.plugin.modifyElement(commentToModify, author=newAuthor)

        newTopics = self.retrieveTopics()
        newComments = self.retrieveComments(newTopics[0])
        updatedComment = newComments[0]

        self.assertTrue(updatedComment.comment == newText and
                updatedComment.modAuthor == newAuthor)


    def test_modifyCommentWithoutAuthor(self):

        """ Test whether the author check for comments and topics works

        Expected: comment does not get updated.
        """

        comments = self.retrieveComments(self.topics[0])
        commentToModify = comments[0]

        oldText = commentToModify.comment
        commentToModify.comment = "Hello my name is... Slim Shaaaaadyyyy"
        self.plugin.modifyElement(commentToModify) # Note: no author is given

        newTopics = self.retrieveTopics()
        newComments = self.retrieveComments(newTopics[0])
        updatedComment = newComments[0]

        self.assertTrue(updatedComment.comment == oldText,
                "Comment text is {} != {}".format(updatedComment.comment,
                    oldText))


    def test_unsuccessfulUpdateProjectUpdates(self):

        """ Tests whether writer.projectUpdates is properly reset for an
        unsuccessful update. """

        updatesLength = len(writer.projectUpdates)

        comments = self.retrieveComments(self.topics[0])
        commentToModify = comments[0]

        oldText = commentToModify.comment
        commentToModify.comment = "Hello my name is... Slim Shaaaaadyyyy"
        self.plugin.modifyElement(commentToModify) # Note: no author is given

        equalInLength = (len(writer.projectUpdates) == updatesLength)
        self.assertTrue(equalInLength,
                "projectUpdates has some residues")


    def test_modifyCommentAuthor(self):

        """ Test the modification of the original author of a topic """

        testAuthor = "hello@kurt.com"
        topicToUpdate = self.topics[0]
        topicToUpdate.author = testAuthor

        self.plugin.modifyElement(topicToUpdate, "a@b.c")
        self.retrieveTopics()

        updatedTopic = self.topics[0]
        self.assertTrue(updatedTopic.author == testAuthor)


    def test_modifyLabel(self):

        """ Test the modification of a simple label """

        newLabelText = "hello my label"
        labelToUpdate = self.topics[0].labels[0]
        labelToUpdate.value = newLabelText

        self.plugin.modifyElement(labelToUpdate)
        self.retrieveTopics()

        updatedLabel = self.topics[0].labels[0]

        self.assertTrue(updatedLabel.value == newLabelText)


    def test_modifyDocumentReferenceAttribute(self):

        """ Test the modification of isExternal attribute """

        # search for a topic with at least one document reference
        i = 0
        while i < len(self.topics) and len(self.topics[i].docRefs) == 0:
            i += 1

        if i == len(self.topics):
            self.assertTrue(False, "No topic contains a document reference!")

        docRefToUpdate = self.topics[i].docRefs[0]
        external = not docRefToUpdate.external
        docRefToUpdate.external = external

        self.plugin.modifyElement(docRefToUpdate)
        self.retrieveTopics()

        updatedDocRef = self.topics[i].docRefs[0]
        self.assertTrue(updatedDocRef.external == external, "`isExternal` was"\
                " not updated properly")


    def test_modifyTopicStatus(self):

        topicIdx = 0
        topicToUpdate = self.topics[topicIdx]

        newStatus = "nearly done"
        topicToUpdate.status = newStatus
        self.plugin.modifyElement(topicToUpdate, "a@b.c")

        self.retrieveTopics()
        self.assertTrue(self.topics[topicIdx].status == newStatus,
                "Status of topic does not get updated properly.")

if __name__ == "__main__":
    unittest.main()
