import os
import sys
import unittest
import dateutil.parser
import xmlschema

from shutil import copyfile
from shutil import rmtree
from uuid import UUID
from xmlschema import XMLSchemaValidationError

sys.path.insert(0, "../")
import bcf.reader as reader
import bcf.project as project
import bcf.modification as modification
import bcf.topic as topic
import bcf.uri as uri
import bcf.util as util
import bcf.markup as markup


class BuildProjectTest(unittest.TestCase):
    def setUp(self):
        self.fileDirectory = "./reader_tests/"
        self.bcfFile = "Issues-Example.bcf"

        self.extractionPath = reader.extractFileToTmp(self.fileDirectory+self.bcfFile)
        self.projectFilePath = self.extractionPath + "/" + "project.bcfp"
        self.projectSchemaPath = self.fileDirectory + "project.xsd"


    def tearDown(self):
        rmtree(self.extractionPath) # remove extracted zip


    def test_project_without_name(self):

        """
        Takes the prepared project-without-name.bcfp file, in whicht he project
        node does not have a name, and checks whether the object gets created
        accordingly
        """

        # copy the prepared project file to the temporary directory
        srcFilePath = self.fileDirectory + "/project-without-name.bcfp"
        copyfile(srcFilePath, self.projectFilePath)

        expectedProject = project.Project(
                UUID("14b6afe9-866c-494a-97d6-ddb44971814e"),
                "",
                None)
        resultingProject = reader.buildProject(self.projectFilePath,
                self.projectSchemaPath)
        self.assertEqual(expectedProject, resultingProject)

    def test_project_with_two_names(self):

        """
        Input: project-with-two-names.bcfp, a project file that has two names
        specified, normal project.xsd
        Expected Output: XMLSchemaValidationError
        """

        # copy the prepared project file to the temporary directory
        srcFilePath = self.fileDirectory + "/project-with-two-names.bcfp"
        copyfile(srcFilePath, self.projectFilePath)

        with self.assertRaises(XMLSchemaValidationError):
            reader.buildProject(self.projectFilePath, self.projectSchemaPath)

    def test_empty_project_file_path(self):

        """
        Input: empty project file path, normal project.xsd
        Output: None
        """

        self.assertIsNone(reader.buildProject("", self.projectSchemaPath))

    def test_empty_project_schema_path(self):

        """
        Input: empty project schema path, normal project.bcfp
        Output: None
        """

        self.assertIsNone(reader.buildProject(self.projectFilePath, ""))

    def test_empty_project_file(self):

        """
        Input: project-empty.bcfp, just a empty file, normal project.xsd
        Output: Exception
        """

        # copy the prepared project file to the temporary directory
        srcFilePath = self.fileDirectory + "project-empty.bcfp"
        copyfile(srcFilePath, self.projectFilePath)

        with self.assertRaises(BaseException):
            reader.buildProject(self.projectFilePath, self.projectSchemaPath)

    def test_empty_schema_file(self):

        """
        Input: normal project.bcfp but empty project.xsd file
        Output: Exception
        """

        self.projectSchemaPath = self.fileDirectory + "project-empty.xsd"
        with self.assertRaises(BaseException):
            reader.buildProject(self.projectFilePath, self.projectSchemaPath)


class buildTopicTest(unittest.TestCase):
    def setUp(self):
        self.fileDirectory = "./reader_tests/"
        self.bcfFile = "Issues-Example.bcf"

        self.topicGuid = "0a36e3d6-97e9-47d6-ab4f-227990429f52"
        self.extractionPath = reader.extractFileToTmp(self.fileDirectory+self.bcfFile)
        self.markupFiles = ["topic_complete.bcf", "topic_13_comments.bcf",
                "topic_original.bcf", "topic_minimal.bcf"]
        self.markupFilePaths = map(
                lambda item: os.path.join(self.extractionPath, self.topicGuid, item),
                self.markupFiles)
        self.markupDestinationPath = os.path.join(util.getSystemTmp(),
                self.extractionPath,
                self.topicGuid,
                "markup.bcf")
        self.markupSchemaPath = self.fileDirectory + "markup.xsd"


    def tearDown(self):
        rmtree(self.extractionPath)


    def test_complete_topic(self):

        """
        Input: dictionary representation of the complete topic of the markup
        file in topic directory: 0a36e3d6-97e9-47d6-ab4f-227990429f52
        Output: Object of type Topic with contents as specified below
        """

        # create expected topic object
        expectedCreation = modification.Modification("bgreen@bim.col",
                dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedLastModification = modification.Modification("fleopard@bim.col",
                dateutil.parser.parse("2017-10-10T14:24:31+00:00"))
        expectedReferences = [
                topic.DocumentReference(
                    id=UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                    external=True,
                    reference=uri.Uri("/url/to/document"),
                    description="This is a description of the document") ]
        expectedLabels = [
                    "architecture",
                    "building",
                    "home" ]
        expectedDueDate = dateutil.parser.parse("2017-10-10T08:00:00+00:00")
        expectedRelatedTopics = [
                UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52")
                ]

        expectedTopic = topic.Topic(UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                title="Ceiling above reception",
                creation=expectedCreation,
                type="Inquiry",
                status="Active",
                refs=expectedReferences,
                priority="Normal",
                index=21,
                labels=expectedLabels,
                lastModification=expectedLastModification,
                dueDate=expectedDueDate,
                assignee="irenfroe@bim.col",
                description="This is just a sample description",
                stage="Preliminary Planning",
                relatedTopics=expectedRelatedTopics)

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[0])
        copyfile(srcFilePath, self.markupDestinationPath)

        # prepare for and execute buildTopic
        schema = xmlschema.XMLSchema(self.markupSchemaPath)
        markupDict = schema.to_dict(self.markupDestinationPath)
        actualTopic = reader.buildTopic(markupDict["Topic"])

        # compare expected and actual
        self.assertTrue(expectedTopic.__eq__(actualTopic),
                "Expected:\n{}\n\n\nActual:{}".format(expectedTopic,
                    actualTopic))


    def test_original_topic(self):

        """
        Input: dictionary representation of the original topic of the markup
        file in topic directory: 0a36e3d6-97e9-47d6-ab4f-227990429f52
        Output: Object of type Topic with contents as specified below
        """

        # create expected topic object
        expectedCreation = modification.Modification("bgreen@bim.col",
                dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedLastModification = modification.Modification("fleopard@bim.col",
                dateutil.parser.parse("2017-10-10T14:24:31+00:00"))
        expectedLabels = [ "architecture" ]
        expectedDueDate = dateutil.parser.parse("2017-10-10T08:00:00+00:00")

        expectedTopic = topic.Topic(UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                title="Ceiling above reception",
                creation=expectedCreation,
                type="Inquiry",
                status="Active",
                refs=[],
                priority="Normal",
                index=21,
                labels=expectedLabels,
                lastModification=expectedLastModification,
                dueDate=expectedDueDate,
                assignee="irenfroe@bim.col",
                description="",
                stage="01. Design phase",
                relatedTopics=[])

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[2])
        copyfile(srcFilePath, self.markupDestinationPath)

        # prepare for and execute buildTopic
        schema = xmlschema.XMLSchema(self.markupSchemaPath)
        markupDict = schema.to_dict(self.markupDestinationPath)
        actualTopic = reader.buildTopic(markupDict["Topic"])

        # compare expected and actual
        self.assertTrue(expectedTopic.__eq__(actualTopic),
                "Expected:\n{}\n\n\nActual:{}".format(expectedTopic,
                    actualTopic))


    def test_minimal_topic(self):

        """
        Input: dictionary representation of the minimal topic of the markup file
        in topic directory: 0a36e3d6-97e9-47d6-ab4f-227990429f52
        Output: Object of type Topic with contents as specified below
        """

        # create expected topic object
        expectedCreation = modification.Modification("bgreen@bim.col",
                dateutil.parser.parse("2014-10-16T14:35:29+00:00"))

        expectedTopic = topic.Topic(UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                title="Ceiling above reception",
                creation=expectedCreation,
                type="",
                status="",
                refs=[],
                priority="",
                index=0,
                labels=[],
                lastModification=None,
                dueDate=None,
                assignee="",
                description="",
                stage="",
                relatedTopics=[])

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[3])
        copyfile(srcFilePath, self.markupDestinationPath)

        # prepare for and execute buildTopic
        schema = xmlschema.XMLSchema(self.markupSchemaPath)
        markupDict = schema.to_dict(self.markupDestinationPath)
        actualTopic = reader.buildTopic(markupDict["Topic"])

        # compare expected and actual
        self.assertTrue(expectedTopic.__eq__(actualTopic),
                "Expected:\n{}\n\n\nActual:{}".format(expectedTopic,
                    actualTopic))


class buildCommentTest(unittest.TestCase):

    def setUp(self):

        self.fileDirectory = "./reader_tests/"
        self.bcfFile = "Issues-Example.bcf"

        # comments are contained in markup.bcf
        self.topicGuid = "0a36e3d6-97e9-47d6-ab4f-227990429f52"
        self.extractionPath = reader.extractFileToTmp(self.fileDirectory+self.bcfFile)
        self.markupFiles = ["comment_complete.bcf", "comment_minimal.bcf",
                "comment_original.bcf"]
        self.markupFilePaths = map(
                lambda item: os.path.join(self.extractionPath, self.topicGuid, item),
                self.markupFiles)
        self.markupDestinationPath = os.path.join(util.getSystemTmp(),
                self.extractionPath,
                self.topicGuid,
                "markup.bcf")
        self.markupSchemaPath = self.fileDirectory + "markup.xsd"


    def tearDown(self):
        rmtree(self.extractionPath) # remove extracted zip


    def test_minimalComment(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[1])
        copyfile(srcFilePath, self.markupDestinationPath)

        actualMarkup = reader.buildMarkup(srcFilePath, self.markupSchemaPath)

        # building the expected comment object
        expectedCreation = modification.Modification(author="bgreen@bim.col",
                date=dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedComment = markup.Comment(
                creation = expectedCreation,
                comment = "Do you mean this one?",
                viewpoint = None,
                lastModification = None)

        expectedCommentList = [ expectedComment ]

        # compare expected and actual
        self.assertEqual(expectedCommentList, actualMarkup.comments,
            "\nExpected:\n{}\n\n\nActual:{}".format(expectedCommentList,
                actualMarkup.comments))


    def test_completeComment(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[0])
        copyfile(srcFilePath, self.markupDestinationPath)

        actualMarkup = reader.buildMarkup(srcFilePath, self.markupSchemaPath)

        # building the expected comment object
        expectedCreation = modification.Modification(author="bgreen@bim.col",
                date=dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedModification = modification.Modification(author="bgreen@bim.col",
                date=dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedViewpoint = markup.ViewpointReference(
                id=UUID("b496c251-2729-4dee-94a1-085168d36512"),
                file=uri.Uri("viewpoint.bcfv"),
                snapshot=uri.Uri("snapshot.png"),
                index=2)
        expectedComment = markup.Comment(
                creation = expectedCreation,
                comment = "Do you mean this one?",
                viewpoint = expectedViewpoint,
                lastModification = expectedModification)

        expectedCommentList = [ expectedComment, expectedComment ]

        # compare expected and actual
        for (a, b) in zip(expectedCommentList, actualMarkup.comments):
            self.assertEqual(a, b,
                    "\nExpected:\n{}\n\n\nActual:\n{}".format(a,
                    b))


    def test_originalComment(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[2])
        copyfile(srcFilePath, self.markupDestinationPath)

        actualMarkup = reader.buildMarkup(srcFilePath, self.markupSchemaPath)

        # building the expected comment object
        expectedCreation = modification.Modification(author="bgreen@bim.col",
                date=dateutil.parser.parse("2014-10-16T14:35:29+00:00"))
        expectedViewpoint = markup.ViewpointReference(
                id=UUID("b496c251-2729-4dee-94a1-085168d36512"),
                file=uri.Uri("viewpoint.bcfv"),
                snapshot=uri.Uri("snapshot.png"),
                index=0)
        expectedComment = markup.Comment(
                creation = expectedCreation,
                comment = "Do you mean this one?",
                viewpoint = expectedViewpoint,
                lastModification = None)

        expectedCommentList = [ expectedComment ]

        # compare expected and actual
        for (a, b) in zip(expectedCommentList, actualMarkup.comments):
            self.assertTrue(a.__eq__(b),
                    "\nExpected:\n{}\n\n\nActual:\n{}".format(a,
                    b))


if __name__ == "__main__":
    unittest.main()
