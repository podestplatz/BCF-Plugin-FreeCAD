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
import interfaces.hierarchy as hierarchy


def setupBCFFile(testFile, testFileDir, testTopicDir, testBCFName):

    os.system("cp {} {}/{}/markup.bcf".format(testFile,
        testFileDir, testTopicDir))
    os.system("cd ./search_tests && zip -q {} {}/markup.bcf".format(testBCFName,
        testTopicDir))

    return os.path.join(testFileDir, testBCFName)


class SearchObjectTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./search_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_search_test.bcf" ]


    def test_searchComment(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        commentToSearch = p.topicList[0].comments[0]
        searchResult = p.searchObject(commentToSearch)

        self.assertTrue(searchResult is not None and
                commentToSearch.id == searchResult.id)


    def test_searchFile(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        fileToFind = p.topicList[0].header.files[0]
        searchResult = p.searchObject(fileToFind)

        self.assertTrue(searchResult is not None and
                fileToFind.id == searchResult.id)


    def test_searchIsExternal(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        externalToFind = p.topicList[0].header.files[1]._external
        searchResult = p.searchObject(externalToFind)

        if searchResult == None:
            project.debug("Did not find anything")
        self.assertTrue(searchResult is not None and
                externalToFind.id == searchResult.id)


if __name__ == "__main__":
    unittest.main()
