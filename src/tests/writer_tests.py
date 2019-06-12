import os
import sys
import copy
import pprint
import difflib
import unittest
import xmlschema
import dateutil.parser

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


class AddElementTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./writer_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_add_comment_test.bcf",
                "markup_add_comment_modification_test.bcf",
                "markup_add_lone_viewpoint_test.bcf"
                "markup_add_full_viewpoint_check.bcf",
                "", # dummy element to keep both lists equal in length
                ]
        self.checkFiles = ["markup_add_comment_check.bcf",
                "markup_add_comment_modification_check.bcf",
                "markup_add_lone_viewpoint_check.bcf",
                "markup_add_full_viewpoint_check.bcf",
                "viewpoint_add_full_viewpoint_check.bcfv"]
        self.testFileDestinations = [os.path.join(self.markupDestDir, "markup.bcf"),
                os.path.join(self.markupDestDir, "viewpoint.bcfv"),
                os.path.join(self.markupDestDir, "viewpoint2.bcfv")]


    def setupBCFFile(self, testFile):

        os.system("cp {} {}/{}/markup.bcf".format(testFile,
            self.testFileDir, self.testTopicDir))
        os.system("cd ./writer_tests && zip {} {}/markup.bcf".format(self.testBCFName,
            self.testTopicDir))

        return os.path.join(self.testFileDir, self.testBCFName)


    def compareFiles(self, checkFile):

        testFilePath = os.path.join(util.getSystemTmp(), self.testBCFName,
                    self.testTopicDir)
        if checkFile.startswith("markup"):
            testFilePath = os.path.join(testFilePath, "markup.bcf")
        elif checkFile.startswith("viewpoint"):
            testFilePath = os.path.join(testFilePath, "viewpoint.bcfv")

        checkFilePath = os.path.join(self.testFileDir, checkFile)

        with open(testFilePath, 'r') as testFile:
            with open(checkFilePath, 'r') as checkFile:
                testFileText = testFile.readlines()
                if testFileText[-1][-1] != "\n":
                    testFileText[-1] += "\n"
                checkFileText = checkFile.readlines()
                differ = difflib.Differ(charjunk=difflib.IS_CHARACTER_JUNK)
                resultDiffText = list(differ.compare(testFileText, checkFileText))
                resultList = [ False for item in resultDiffText if item[0] != ' ' ]

                if len(resultList)>0:
                    return (False, resultDiffText)
                else:
                    return (True, None)


    def test_add_comment(self):
        """
        Tests the addition of a comment.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = self.setupBCFFile(srcFilePath)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeComment = copy.deepcopy(markup.comments[0])
        prototypeComment.comment = "hello this is me mario!"
        prototypeComment.state = s.State.States.ADDED
        markup.comments.append(prototypeComment)

        writer.addElement(prototypeComment)

        (equal, diff) = self.compareFiles(self.checkFiles[0])
        if not equal:
            copyfile(self.testFileDestinations[0],
                    os.path.join(self.testFileDir, "error_files",
                    "markup_add_comment.bcf"))
            print("Following is the diff between the file that was generated"\
                    " and the prepared file:")
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_add_comment_modification(self):
        """
        Tests the addition of modification data to an existing comment
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[1])
        testFile = self.setupBCFFile(srcFilePath)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        comment = markup.comments[0]
        modifiedDate = dateutil.parser.parse("2014-10-16T13:10:56+00:00")
        modifiedAuthor = "fleopard@bim.col"
        mod = modification.Modification(author = modifiedAuthor,
                date = modifiedDate,
                modType = modification.ModificationType.MODIFICATION)
        comment.lastModification = mod
        comment.lastModification.state = s.State.States.ADDED
        writer.addElement(comment.lastModification._author)
        writer.addElement(comment.lastModification._date)

        (equal, diff) = self.compareFiles(self.checkFiles[1])
        if not equal:
            copyfile(self.testFileDestinations[0],
                    os.path.join(self.testFileDir, "error_files",
                    "markup_add_comment_modification.bcf"))
            print("Following is the diff between the file that was generated"\
                    " and the prepared file:")
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_add_viewpointreference(self):
        """
        Tests whether a viewpoint reference can be added without having a new
        viewpoint file created.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[2])
        testFile = self.setupBCFFile(srcFilePath)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeViewpointRef = copy.deepcopy(markup.viewpoints[0])
        prototypeViewpointRef.id = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        prototypeViewpointRef.viewpoint = None
        prototypeViewpointRef.state = s.State.States.ADDED
        markup.viewpoints.append(prototypeViewpointRef)
        writer.addElement(prototypeViewpointRef)

        (equal, diff) = self.compareFiles(self.checkFiles[2])
        if not equal:
            copyfile(self.testFileDestinations[0],
                    os.path.join(self.testFileDir, "error_files",
                    "markup_add_lone_viewpoint.bcf"))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    self.test_add_viewpointreference.__name__))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_add_viewpoint(self):
        """
        Tests the correct addition of a complete new viewpoint including a new
        viewpoint reference in markup
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[3])
        testFile = self.setupBCFFile(srcFilePath)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeViewpointRef = copy.deepcopy(markup.viewpoints[0])
        prototypeViewpointRef.file = "viewpoint2.bcfv"
        prototypeViewpointRef.state = s.State.States.ADDED
        prototypeViewpointRef.viewpoint.state = s.State.States.ADDED
        markup.viewpoints.append(prototypeViewpointRef)
        writer.addElement(prototypeViewpointRef)

        (vpRefEqual, vpRefDiff) = self.compareFiles(self.checkFiles[3])
        (vpEqual, vpDiff) = self.compareFiles(self.checkFiles[4])
        if not vpRefEqual:
            copyfile(self.testFileDestinations[0],
                    os.path.join(self.testFileDir, "error_files",
                    "markup_add_full_viewpoint.bcf"))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                        self.test_add_viewpoint.__name__))
            pprint.pprint(vpRefDiff)

        if not vpEqual:
            copyfile(self.testFileDestinations[2],
                    os.path.join(self.testFileDir, "error_files",
                    "viewpoint_add_full_viewpoint.bcfv"))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                        self.test_add_viewpoint.__name__))
            pprint.pprint(vpDiff)
        self.assertTrue(vpRefEqual and vpEqual)

    def test_add_file(self):
        """
        Tests the addition of a file element in the header node
        """
        self.assertTrue(True)

    def test_add_file_attributes(self):
        """
        Tests the addition of the optional attributes to one of the file nodes
        """
        self.assertTrue(True)

    def test_add_documentReference_attributes(self):
        """
        Tests the addition of the optional attributes to one of the document
        reference nodes.
        """
        self.assertTrue(True)

    def test_add_bimSnippet_attribute(self):
        """
        Tests the addition of the optional attribute of BimSnippet
        """
        self.assertTrue(True)

    def test_add_label(self):
        """
        Tests the addition of a label
        """
        self.assertTrue(True)

    def test_add_creation(self):
        """
        Tests the addition of creation data to a topic
        """
        self.assertTrue(True)

    def test_add_assignedTo(self):
        """
        Tests the addition of the AssignedTo node to a topic
        """
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
