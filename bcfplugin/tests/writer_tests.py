import os
import sys
import copy
import pprint
import difflib
import unittest
import xmlschema
import dateutil.parser
import xml.etree.ElementTree as ET

from uuid import UUID, uuid4
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
import rdwr.interfaces.hierarchy as hierarchy

def setupBCFFile(testFile, testFileDir, testTopicDir, testBCFName):

    cmd = "cp {} {}/{}/markup.bcf".format(testFile,
        testFileDir, testTopicDir)
    project.debug("Executing: {}".format(cmd))
    os.system(cmd)

    cmd = "cd ./writer_tests && zip -q {} {}/markup.bcf".format(testBCFName,
        testTopicDir)
    project.debug("Executing: {}".format(cmd))
    os.system("cd ./writer_tests && zip -q {} {}/markup.bcf".format(testBCFName,
        testTopicDir))

    return os.path.join(testFileDir, testBCFName)


def compareFiles(checkFile, testFileDir, testTopicDir, testBCFName):

    testFilePath = os.path.join(util.getSystemTmp(), testBCFName,
                testTopicDir)
    if checkFile.startswith("markup"):
        testFilePath = os.path.join(testFilePath, "markup.bcf")
    elif checkFile.startswith("viewpoint"):
        testFilePath = os.path.join(testFilePath, "viewpoint.bcfv")

    checkFilePath = os.path.join(testFileDir, checkFile)

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


class AddElementTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./writer_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_add_comment_test.bcf",
                "markup_add_comment_modification_test.bcf",
                "markup_add_lone_viewpoint_test.bcf",
                "markup_add_full_viewpoint_test.bcf",
                "", # dummy element to keep both lists equal in length
                "markup_add_file_test.bcf",
                "markup_add_file_attribute_test.bcf",
                "markup_add_file_attribute2_test.bcf",
                "markup_add_doc_ref_attribute_test.bcf",
                "markup_add_bim_snippet_attribute_test.bcf",
                "markup_add_label_test.bcf",
                "markup_add_assigned_to_test.bcf"
                ]
        self.checkFiles = ["markup_add_comment_check.bcf",
                "markup_add_comment_modification_check.bcf",
                "markup_add_lone_viewpoint_check.bcf",
                "markup_add_full_viewpoint_check.bcf",
                "viewpoint_add_full_viewpoint_check.bcfv",
                "markup_add_file_check.bcf",
                "markup_add_file_attribute_check.bcf",
                "markup_add_file_attribute2_check.bcf",
                "markup_add_doc_ref_attribute_check.bcf",
                "markup_add_bim_snippet_attribute_check.bcf",
                "markup_add_label_check.bcf",
                "markup_add_assigned_to_check.bcf"
                ]
        self.testFileDestinations = [os.path.join(self.markupDestDir, "markup.bcf"),
                os.path.join(self.markupDestDir, "viewpoint.bcfv"),
                os.path.join(self.markupDestDir, "viewpoint2.bcfv")]


    def tearDown(self):

        path = os.path.join(util.getSystemTmp(), self.testBCFName)
        rmtree(path)


    def test_addMarkup(self):

        """
        Tests the addition of a whole new markup object. This should result in
        the creation of a new folder as well as a new markup.bcf file and a new
        viewpoint file.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        newMarkup = copy.deepcopy(p.topicList[0])
        newMarkup.containingObject = p
        newMarkup.state = s.State.States.ADDED
        newMarkup.topic.xmlId = uuid4() # generate random uuid
        p.topicList.append(newMarkup)
        writer.addElement(newMarkup)

        folderPath = os.path.join(util.getSystemTmp(), self.testBCFName,
                str(newMarkup.topic.xmlId))
        folderExists = os.path.exists(folderPath)
        if not folderExists:
            project.debug("Folder does not exist")

        markupFilePath = os.path.join(folderPath, "markup.bcf")
        markupFileExists = os.path.exists(markupFilePath)
        if not markupFileExists:
            project.debug("Markup file does not exist")

        self.assertTrue(markupFileExists and folderExists)


    def test_addComment(self):

        """
        Tests the addition of a comment.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeComment = copy.deepcopy(markup.comments[0])
        prototypeComment.comment = "hello this is me mario!"
        prototypeComment.state = s.State.States.ADDED
        markup.comments.append(prototypeComment)

        writer.addElement(prototypeComment)

        (equal, diff) = compareFiles(self.checkFiles[0], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_comment.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            print("writer_tests.{}(): copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            print("Following is the diff between the file that was generated"\
                    " and the prepared file:")
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addCommentModification(self):

        """
        Tests the addition of modification data to an existing comment
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[1])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        comment = markup.comments[0]
        comment.modAuthor = "fleopard@bim.col"
        comment.modDate = dateutil.parser.parse("2014-10-16T13:10:56+00:00")
        writer.addElement(comment._modAuthor)
        writer.addElement(comment._modDate)

        (equal, diff) = compareFiles(self.checkFiles[1], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_comment_modification.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            print("writer_tests.{}(): copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            print("Following is the diff between the file that was generated"\
                    " and the prepared file:")
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addViewpointReference(self):

        """
        Tests whether a viewpoint reference can be added without having a new
        viewpoint file created.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[2])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeViewpointRef = copy.deepcopy(markup.viewpoints[0])
        prototypeViewpointRef.xmlId = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
        prototypeViewpointRef.viewpoint = None
        prototypeViewpointRef.state = s.State.States.ADDED
        markup.viewpoints.append(prototypeViewpointRef)
        writer.addElement(prototypeViewpointRef)

        (equal, diff) = compareFiles(self.checkFiles[2], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_lone_viewpoint.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            print("writer_tests.{}(): copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    self.test_add_viewpointreference.__name__))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addViewpoint(self):

        """
        Tests the correct addition of a complete new viewpoint including a new
        viewpoint reference in markup
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[3])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        project = reader.readBcfFile(testFile)

        markup = project.topicList[0]
        prototypeViewpointRef = copy.deepcopy(markup.viewpoints[0])
        prototypeViewpointRef.file = "viewpoint2.bcfv"
        prototypeViewpointRef.state = s.State.States.ADDED
        prototypeViewpointRef.viewpoint.state = s.State.States.ADDED
        markup.viewpoints.append(prototypeViewpointRef)
        writer.addElement(prototypeViewpointRef)

        (vpRefEqual, vpRefDiff) = compareFiles(self.checkFiles[3], self.testFileDir, self.testTopicDir, self.testBCFName)
        (vpEqual, vpDiff) = compareFiles(self.checkFiles[4], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not vpRefEqual:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_full_viewpoint.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            print("writer_tests.{}(): copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                        self.test_add_viewpoint.__name__))
            pprint.pprint(vpRefDiff)

        if not vpEqual:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "viewpoint_add_full_viewpoint.bcfv")
            copyfile(self.testFileDestinations[2], wrongFileDestination)
            print("writer_tests.{}(): copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            print("writer_tests.{}(): Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                        self.test_add_viewpoint.__name__))
            pprint.pprint(vpDiff)
        self.assertTrue(vpRefEqual and vpEqual)


    def test_addFile(self):

        """
        Tests the addition of a file element in the header node
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[5])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        m = p.topicList[0]
        header = m.header
        newFile = markup.HeaderFile(ifcProjectId = "abcdefghij",
            ifcSpatialStructureElement = "klmnopqrs",
            isExternal = False,
            filename = "this is some file name",
            time = dateutil.parser.parse("2014-10-16T13:10:56+00:00"),
            reference = "/path/to/the/file",
            containingElement = header,
            state = s.State.States.ADDED)
        header.files.append(newFile)
        project.debug("type of newFile is"
                " {}".format(
                    type(newFile)))

        writer.addElement(newFile)

        (equal, diff) = compareFiles(self.checkFiles[5], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_file.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(self.test_add_file.__name__,
                        wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    self.test_add_viewpointreference.__name__,
                    wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addFileAttributes(self):

        """
        Tests the addition of the optional attributes to one of the file nodes
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[6])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        m = p.topicList[0]
        file = m.header.files[0]
        file.ifcProjectId = "aaaabbbbcccc"
        file._ifcProjectId.state = s.State.States.ADDED
        writer.addElement(file._ifcProjectId)

        (equal, diff) = compareFiles(self.checkFiles[6], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_file_attribute.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                   wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addFileAttributes2(self):

        """
        Tests the addition of the optional attributes to one of the file nodes
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[7])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        m = p.topicList[0]
        file = m.header.files[0]
        file.ifcSpatialStructureElement = "aaaabbbbcccc"
        file._ifcSpatialStructureElement.state = s.State.States.ADDED
        writer.addElement(file._ifcSpatialStructureElement)

        (equal, diff) = compareFiles(self.checkFiles[7], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_file_attribute2.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                    " and the prepared file:".format(wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addDocumentReferenceAttributes(self):

        """
        Tests the addition of the optional attributes to one of the document
        reference nodes.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[8])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        docRef = p.topicList[0].topic.docRefs[0]
        docRef.guid = "98b5802c-4ca0-4032-9128-b9c606955c4f"
        docRef._guid.state = s.State.States.ADDED
        writer.addElement(docRef._guid)

        (equal, diff) = compareFiles(self.checkFiles[8], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_doc_ref_attribute.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addBimSnippetAttribute(self):

        """
        Tests the addition of the optional attribute of BimSnippet
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[9])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        bimSnippet = p.topicList[0].topic.bimSnippet
        bimSnippet.external = True
        bimSnippet.state = s.State.States.ADDED
        writer.addElement(bimSnippet._external)

        (equal, diff) = compareFiles(self.checkFiles[9], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_bim_snippet.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addLabel(self):

        """
        Tests the addition of a label
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[10])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        t = p.topicList[0].topic
        newLabel = "Hello"
        t.labels.append(newLabel)
        writer.addElement(t.labels[-1])

        (equal, diff) = compareFiles(self.checkFiles[10], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_label.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


    def test_addAssignedTo(self):

        """
        Tests the addition of the AssignedTo node to a topic
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[11])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        t = p.topicList[0].topic
        t.assignee = "a@b.c"
        t._assignee.state = s.State.States.ADDED
        writer.addElement(t._assignee)

        (equal, diff) = compareFiles(self.checkFiles[11], self.testFileDir, self.testTopicDir, self.testBCFName)
        if not equal:
            wrongFileDestination = os.path.join(self.testFileDir, "error_files",
                    "markup_add_assignedTo.bcf")
            copyfile(self.testFileDestinations[0], wrongFileDestination)
            project.debug("copied erroneous file to"\
                    " {}".format(wrongFileDestination))
            project.debug("Following is the diff between the file that was generated"\
                " and the prepared file:".format(
                    wrongFileDestination))
            pprint.pprint(diff)
        self.assertTrue(equal)


class GetEtElementFromFileTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./writer_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_find_comment_test.bcf",
                "markup_find_comment2_test.bcf",
                "markup_find_label_by_text_test.bcf",
                "markup_find_file_by_attribute_test.bcf"
                ]
        self.checkFiles = ["markup_find_comment_check.bcf"
                ]
        self.testFileDestinations = [os.path.join(self.markupDestDir, "markup.bcf"),
                os.path.join(self.markupDestDir, "viewpoint.bcfv"),
                os.path.join(self.markupDestDir, "viewpoint2.bcfv")]


    def tearDown(self):

        path = os.path.join(util.getSystemTmp(), self.testBCFName)
        rmtree(path)


    def test_findComment(self):

        """
        Tests whether a comment can be found by its children
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        xmlfile = ET.parse(self.testFileDestinations[0])
        xmlroot = xmlfile.getroot()

        commentToFind = p.topicList[0].comments[1]
        finding = writer.getEtElementFromFile(xmlroot, commentToFind)

        expectedComment = list(xmlroot)[3]
        project.debug("writer_tests.test_findComment(): found comment:"\
                "\n\t{}\nand expected comment\n{}"\
                "\n=====".format(ET.tostring(finding),
                    ET.tostring(expectedComment)))

        self.assertEqual(ET.tostring(expectedComment), ET.tostring(finding))


    def test_findComment2(self):

        """
        Tests whether the right comment is found if the text of one child
        differs only by one character
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[1])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        xmlfile = ET.parse(self.testFileDestinations[0])
        xmlroot = xmlfile.getroot()

        expectedComment = list(xmlroot)[3]

        commentToFind = p.topicList[0].comments[1]
        finding = writer.getEtElementFromFile(xmlroot, commentToFind)

        project.debug("writer_tests.test_findComment2(): found comment:"\
                "\n\t{}\nand expected comment\n{}"\
                "\n=====".format(ET.tostring(finding),
                    ET.tostring(expectedComment)))

        self.assertEqual(ET.tostring(expectedComment), ET.tostring(finding))


    def test_findLabelByText(self):

        """
        Tests whether a label can be found just by the text it contains.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[2])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        xmlfile = ET.parse(self.testFileDestinations[0])
        xmlroot = xmlfile.getroot()

        topicEt = list(xmlroot)[1]
        expectedLabel = list(topicEt)[5]

        labelToFind = p.topicList[0].topic.labels[2]
        finding = writer.getEtElementFromFile(xmlroot, labelToFind)

        project.debug("writer_tests.test_findLabelByText(): found label:"\
                "\n\t{}\nand expected label\n{}"\
                "\n=====".format(ET.tostring(finding),
                    ET.tostring(expectedLabel)))

        self.assertEqual(ET.tostring(finding), ET.tostring(expectedLabel))


    def test_findFileByAttribute(self):

        """
        Tests whether a file node can be found solely by its specified
        attributes.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[3])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        xmlfile = ET.parse(self.testFileDestinations[0])
        xmlroot = xmlfile.getroot()

        headerEt = list(xmlroot)[0]
        expectedFile = list(headerEt)[3]

        fileToFind = p.topicList[0].header.files[3]
        finding = writer.getEtElementFromFile(xmlroot, fileToFind)

        project.debug("writer_tests.test_findFileByAttribute(): found file:"\
                "\n\t{}\nand expected file\n{}"\
                "\n=====".format(ET.tostring(finding),
                    ET.tostring(expectedFile)))

        self.assertEqual(ET.tostring(finding), ET.tostring(expectedFile))


def handleFileCheck(expectedFile, fileName, testFileDir, testTopicDir, testBCFName):

    """
    Compares the working file with `expectedFile`. If they are different then
    the working file is copied to `testFileDir/error.bcf` for human
    inspection. True is returned if both files are equal, false otherwise.
    """

    (equal, diff) = compareFiles(expectedFile, testFileDir, testTopicDir, testBCFName)
    if not equal:
        wrongFileDestination = os.path.join(testFileDir,
                "error.bcf")
        testFilePath = os.path.join(util.getSystemTmp(), testBCFName,
                testTopicDir, fileName)
        copyfile(testFilePath, wrongFileDestination)
        print("writer_tests.{}(): copied erroneous file to"\
                " {}".format(handleFileCheck.__name__,
                    wrongFileDestination))
        print("writer_tests.{}(): Following is the diff between the file that was generated"\
            " and the prepared file:".format(
                handleFileCheck.__name__,
                wrongFileDestination))
        pprint.pprint(diff)

    return equal


def printVimDiffCommand(testFileDir, checkFile):
    print("To view differences: \n"\
            "vim -d {}/{} {}/{}".format(testFileDir,
                "error.bcf",
                testFileDir,
                checkFile))


class DeleteElementTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./writer_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_delete_comment_test.bcf",
                "markup_delete_label_test.bcf",
                "markup_delete_ifcproject_test.bcf",
                "markup_delete_file_test.bcf",
                "markup_delete_viewpoint_test.bcf",
                "markup_delete_viewpoint_reference_test.bcf"
                ]
        self.checkFiles = ["markup_delete_comment_check.bcf",
                "markup_delete_label_check.bcf",
                "markup_delete_ifcproject_check.bcf",
                "markup_delete_file_check.bcf",
                "markup_delete_viewpoint_check.bcf",
                "markup_delete_viewpoint_reference_check.bcf"
                ]
        self.testFileDestinations = [os.path.join(self.markupDestDir, "markup.bcf"),
                os.path.join(self.markupDestDir, "viewpoint.bcfv"),
                os.path.join(self.markupDestDir, "viewpoint2.bcfv")]


    def tearDown(self):

        path = os.path.join(util.getSystemTmp(), self.testBCFName)
        rmtree(path)


    def test_deleteComment(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        commentToDelete = p.topicList[0].comments[0]
        commentToDelete.state = s.State.States.DELETED
        writer.deleteElement(commentToDelete)

        equal = handleFileCheck(self.checkFiles[0], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[0])

        self.assertTrue(equal, "Failed to delete comment" \
                " {}".format(commentToDelete))



    def test_deleteLabel(self):

        """
        Tests the deletion of the label <Label>mechanical</Label> from topic
        2e....
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[1])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        labelToDelete = p.topicList[0].topic.labels[2]
        labelToDelete.state = s.State.States.DELETED
        writer.deleteElement(labelToDelete)

        equal = handleFileCheck(self.checkFiles[1], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[1])

        self.assertTrue(equal, "Failed to delete label {}".format(labelToDelete))


    def test_deleteIfcProject(self):

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[2])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        fileToDeleteFrom = p.topicList[0].header.files[0]
        ifcProject = fileToDeleteFrom._ifcProjectId
        ifcProject.state = s.State.States.DELETED
        writer.deleteElement(ifcProject)

        equal = handleFileCheck(self.checkFiles[2], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[2])

        self.assertTrue(equal, "Failed to delete ifcProject attribute"\
                " {}".format(ifcProject))


    def test_deleteFile(self):

        """
        Tests the deletion of a File node inside a Header.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[3])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        fileToDelete = p.topicList[0].header.files[1]
        fileToDelete.state = s.State.States.DELETED
        writer.deleteElement(fileToDelete)

        equal = handleFileCheck(self.checkFiles[3], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[3])

        self.assertTrue(equal, "Failed to delete file {}".format(fileToDelete))


    def test_deleteViewpoint(self):

        """
        Tests whether the referenced viewpoint file gets deleted if the
        viewpoint reference is deleted AND the state of viewpoint is also
        DELETED.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[4])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        vpRefToDelete = p.topicList[0].viewpoints[0]
        vpRefToDelete.state = s.State.States.DELETED
        vpRefToDelete.viewpoint.state = s.State.States.DELETED
        writer.deleteElement(vpRefToDelete)

        vpFilePath = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir, "viewpoint.bcfv")
        stillExists = os.path.exists(vpFilePath)
        equal = handleFileCheck(self.checkFiles[4], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal or stillExists:
            printVimDiffCommand(self.testFileDir, self.checkFiles[4])

        self.assertTrue((not stillExists) and equal, "Failed to delete the "\
                "viewpoint and the accompanying file"\
                " {}".format(vpRefToDelete.viewpoint))


    def test_deleteViewpointReference(self):

        """
        Tests whether the first in the file testfiles[5] viewpoint reference can be deleted.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[5])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        vpRefToDelete = p.topicList[0].viewpoints[0]
        vpRefToDelete.state = s.State.States.DELETED
        writer.deleteElement(vpRefToDelete)

        equal = handleFileCheck(self.checkFiles[5], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[5])

        self.assertTrue(equal, "Failed to delete viewpoint Reference"\
                " {}".format(vpRefToDelete))


class ModifyElementTests(unittest.TestCase):

    def setUp(self):
        self.testFileDir = "./writer_tests"
        self.testTopicDir = "2e92784b-80fc-4e0e-ac02-b424dfd8e664"
        self.testBCFName = "Issues-Example.bcf"
        self.markupDestDir = os.path.join(util.getSystemTmp(), self.testBCFName,
                self.testTopicDir)
        self.testFiles = ["markup_modify_comment_test.bcf",
                "markup_modify_filename_test.bcf",
                "markup_modify_ifc_project_test.bcf"
                ]
        self.checkFiles = ["markup_modify_comment_check.bcf",
                "markup_modify_filename_check.bcf",
                "markup_modify_ifc_project_check.bcf"
                ]
        self.testFileDestinations = [os.path.join(self.markupDestDir, "markup.bcf"),
                os.path.join(self.markupDestDir, "viewpoint.bcfv"),
                os.path.join(self.markupDestDir, "viewpoint2.bcfv")]

    def test_modifyComment(self):

        """
        Tests the modification of the comment node inside a comment
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[0])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        commentToModify = p.topicList[0].comments[0]
        prevValue = commentToModify.comment
        commentToModify.comment = "Hello this is me mario"
        commentToModify._comment.state = s.State.States.MODIFIED
        writer.modifyElement(commentToModify._comment, prevValue)

        equal = handleFileCheck(self.checkFiles[0], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[0])

        self.assertTrue(equal, "Failed to modify {}"\
                "".format(commentToModify, commentToModify))


    def test_modifyFileName(self):

        """
        Tests the modification of the filename of the second file object
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[1])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        fileNameElement = p.topicList[0].header.files[1]._filename
        prevValue = fileNameElement.value
        fileNameElement.value = "Wassup with you?"
        fileNameElement.state = s.State.States.MODIFIED
        writer.modifyElement(fileNameElement, prevValue)

        equal = handleFileCheck(self.checkFiles[1], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[1])

        self.assertTrue(equal, "Failed to modify {}"\
                "".format(fileNameElement))


    def test_modifyIfcProject(self):

        """
        Tests the modification of the IfcProject attribute of the second file
        element.
        """

        srcFilePath = os.path.join(self.testFileDir, self.testFiles[2])
        testFile = setupBCFFile(srcFilePath, self.testFileDir, self.testTopicDir, self.testBCFName)
        p = reader.readBcfFile(testFile)

        ifcProjectAttribute = p.topicList[0].header.files[1]._ifcProjectId
        prevValue = ifcProjectAttribute.value
        ifcProjectAttribute.value = "bbbbbbbbbbbbbbbbbbbbbb"
        ifcProjectAttribute.state = s.State.States.MODIFIED
        writer.modifyElement(ifcProjectAttribute, prevValue)

        equal = handleFileCheck(self.checkFiles[2], "markup.bcf", self.testFileDir,
                self.testTopicDir, self.testBCFName)

        if not equal:
            printVimDiffCommand(self.testFileDir, self.checkFiles[2])

        self.assertTrue(equal, "Failed to modify {}"\
                "".format(ifcProjectAttribute))



if __name__ == "__main__":
    unittest.main()
