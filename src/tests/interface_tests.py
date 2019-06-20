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
import bcf.frontendInterface as bFI
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
        self.testFiles = ["markup_interface_test.bcf" ]

    def test_deleteComment(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        commentToDelete = p.topicList[0].comments[0]
        newProject = bFI.deleteObject(p, commentToDelete)

        self.assertTrue(len(p.topicList[0].comments)==0)

    def test_deleteIfcProject(self):
        pass

    def test_deleteFile(self):
        pass

    def test_deleteHeader(self):
        pass

    def test_deleteLabel(self):
        pass

if __name__ == "__main__":
    unittest.main()
