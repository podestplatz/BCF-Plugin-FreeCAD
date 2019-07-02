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
import util as util
import rdwr.reader as reader
import rdwr.project as project
import rdwr.modification as modification
import rdwr.topic as topic
import rdwr.uri as uri
import rdwr.markup as markup
import rdwr.viewpoint as viewpoint
import rdwr.threedvector as tdv
import rdwr.interfaces.hierarchy as hierarchy


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
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"
        expectedModDate = dateutil.parser.parse("2017-10-10T14:24:31+00:00")
        expectedModAuthor = "fleopard@bim.col"
        expectedReferences = [
                topic.DocumentReference(
                    guid=UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
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
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                type="Inquiry",
                status="Active",
                docRefs=expectedReferences,
                priority="Normal",
                index=21,
                labels=expectedLabels,
                modDate = expectedModDate,
                modAuthor = expectedModAuthor,
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
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"
        expectedModDate = dateutil.parser.parse("2017-10-10T14:24:31+00:00")
        expectedModAuthor = "fleopard@bim.col"
        expectedLabels = [ "architecture" ]
        expectedDueDate = dateutil.parser.parse("2017-10-10T08:00:00+00:00")

        expectedTopic = topic.Topic(UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                title="Ceiling above reception",
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                type="Inquiry",
                status="Active",
                docRefs=[],
                priority="Normal",
                index=21,
                labels=expectedLabels,
                modDate = expectedModDate,
                modAuthor = expectedModAuthor,
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
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"

        expectedTopic = topic.Topic(UUID("0a36e3d6-97e9-47d6-ab4f-227990429f52"),
                title="Ceiling above reception",
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                type="",
                status="",
                docRefs=[],
                priority="",
                index=0,
                labels=[],
                modDate = None,
                modAuthor = "",
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
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"
        expectedComment = markup.Comment(
                UUID("2b1e79c8-9d2d-419d-887a-fcff8fec7595"),
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                comment = "Do you mean this one?",
                viewpoint = None,
                modDate = None,
                modAuthor = "")

        expectedCommentList = [ expectedComment ]

        # compare expected and actual
        for (a, b) in zip(expectedCommentList, actualMarkup.comments):
            self.assertEqual(a, b,
                    "\nExpected:\n{}\n\n\nActual:\n{}".format(a,
                    b))


    def test_completeComment(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.markupFiles[0])
        copyfile(srcFilePath, self.markupDestinationPath)

        actualMarkup = reader.buildMarkup(srcFilePath, self.markupSchemaPath)

        # building the expected comment object
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"
        expectedModDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedModAuthor = "bgreen@bim.col"
        expectedViewpoint = markup.ViewpointReference(
                id=UUID("b496c251-2729-4dee-94a1-085168d36512"),
                file=uri.Uri("viewpoint.bcfv"),
                snapshot=uri.Uri("snapshot.png"),
                index=2)
        expectedComment = markup.Comment(
                UUID("2b1e79c8-9d2d-419d-887a-fcff8fec7595"),
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                comment = "Do you mean this one?",
                viewpoint = expectedViewpoint,
                modDate = expectedModDate,
                modAuthor = expectedModAuthor)

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
        expectedCreationDate = dateutil.parser.parse("2014-10-16T14:35:29+00:00")
        expectedCreationAuthor = "bgreen@bim.col"
        expectedViewpoint = markup.ViewpointReference(
                id=UUID("b496c251-2729-4dee-94a1-085168d36512"),
                file=uri.Uri("viewpoint.bcfv"),
                snapshot=uri.Uri("snapshot.png"),
                index=-1)
        expectedComment = markup.Comment(
                UUID("2b1e79c8-9d2d-419d-887a-fcff8fec7595"),
                date = expectedCreationDate,
                author = expectedCreationAuthor,
                comment = "Do you mean this one?",
                viewpoint = expectedViewpoint,
                modDate = None,
                modAuthor = "")

        expectedCommentList = [ expectedComment ]

        # compare expected and actual
        for (a, b) in zip(expectedCommentList, actualMarkup.comments):
            self.assertEqual(a, b,
                    "\nExpected:\n{}\n\n\nActual:\n{}".format(a,
                    b))


class buildViewpointTest(unittest.TestCase):

    def setUp(self):

        self.fileDirectory = "./reader_tests/"
        self.bcfFile = "Issues-Example.bcf"

        # comments are contained in markup.bcf
        self.topicGuid = "0a36e3d6-97e9-47d6-ab4f-227990429f52"
        self.extractionPath = reader.extractFileToTmp(self.fileDirectory+self.bcfFile)
        self.viewpointFiles = ["viewpoint_complete.bcfv",
                "viewpoint_minimal.bcfv", "viewpoint_original.bcfv"]
        self.viewpointFilePath = map(
                lambda item: os.path.join(self.extractionPath, self.topicGuid, item),
                self.viewpointFiles)
        self.viewpointDestinationPath = os.path.join(util.getSystemTmp(),
                self.extractionPath,
                self.topicGuid,
                "viewpoint.bcfv")
        self.viewpointSchemaPath = self.fileDirectory + "visinfo.xsd"


    def tearDown(self):
        rmtree(self.extractionPath) # remove extracted zip


    def test_complete_viewpoint(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.viewpointFiles[0])
        copyfile(srcFilePath, self.viewpointDestinationPath)

        actualViewpoint = reader.buildViewpoint(srcFilePath,
                self.viewpointSchemaPath)

        # building the expected viewpoint object
        expectedExceptions = [
                viewpoint.Component(ifcId="0T_ZmDTXnD8vMdc6O2ywGw"),
                viewpoint.Component(ifcId="1R5DibLMjDRAjgX7wvDhFw")]

        expectedSelection = [
                viewpoint.Component(ifcId="2WxlJcqgXiHhEvEmREXH8o"),
                viewpoint.Component(ifcId="3WxlJcqgXiHhEvEmREXH8o"),
                viewpoint.Component(ifcId="4WxlJcqgXiHhEvEmREXH8o"),
                viewpoint.Component(ifcId="5WxlJcqgXiHhEvEmREXH8o")]

        expectedViewSetuphints = viewpoint.ViewSetupHints(
                openingsVisible=False,
                spacesVisible=False,
                spaceBoundariesVisible=False)

        expectedColouring = [
                viewpoint.ComponentColour(colour="AABBCC", components=expectedExceptions),
                viewpoint.ComponentColour(colour="DDEEFF", components=expectedExceptions)]

        expectedComponents = viewpoint.Components(
                visibilityDefault=False,
                visibilityExceptions=expectedExceptions,
                selection=expectedSelection,
                viewSetuphints=expectedViewSetuphints,
                colouring=expectedColouring
                )

        expectedOCamera = viewpoint.OrthogonalCamera(
                tdv.Point(31.831852245718924, 8.3991482482556918,
                    16.610063251737976),
                tdv.Direction(-0.33103085679096667,
                    0.53391253908149949, -0.77804625342185463),
                tdv.Direction(-0.40998798211340642,
                    0.66126078591306314, 0.62820699417963755),
                23.6)

        expectedPCamera = viewpoint.PerspectiveCamera(
                tdv.Point(31.831852245718924, 8.3991482482556918,
                    16.610063251737976),
                tdv.Direction(-0.33103085679096667,
                    0.53391253908149949, -0.77804625342185463),
                tdv.Direction(-0.40998798211340642,
                    0.66126078591306314, 0.62820699417963755),
                60)

        point = tdv.Point(-0.40998798211340642, 0.66126078591306314,
                0.62820699417963755)
        line = tdv.Line(start = point, end = point)
        expectedLines = [ line, line ]

        clippingPlane = viewpoint.ClippingPlane(location=point, direction=point)
        expectedClippingPlanes = [ clippingPlane, clippingPlane ]

        bitmap = viewpoint.Bitmap(format=viewpoint.BitmapFormat.JPG,
                reference="/path/to/bitmap",
                location=point,
                normal=point,
                upVector=point,
                height=10)
        expectedBitmaps = [ bitmap, bitmap, bitmap ]

        expectedViewpoint = viewpoint.Viewpoint(
                id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
                components=expectedComponents,
                oCamera=expectedOCamera,
                pCamera=expectedPCamera,
                lines=expectedLines,
                clippingPlanes=expectedClippingPlanes,
                bitmaps=expectedBitmaps)

        self.assertEqual(expectedViewpoint, actualViewpoint,
                "\n\nExpected:\n{}, \n\nActual:\n{}\n".format(
                    str(expectedViewpoint),
                    str(actualViewpoint)))


    def test_minimal_viewpoint(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.viewpointFiles[1])
        copyfile(srcFilePath, self.viewpointDestinationPath)

        actualViewpoint = reader.buildViewpoint(srcFilePath,
                self.viewpointSchemaPath)

        # building the expected viewpoint object
        expectedViewpoint = viewpoint.Viewpoint(
                id=UUID("a7230ae3-d17d-46fa-8fbd-775d1a0e3efb"),
                components=None,
                oCamera=None,
                pCamera=None,
                lines=list(),
                clippingPlanes=list(),
                bitmaps=list())

        self.assertEqual(expectedViewpoint, actualViewpoint,
                "\n\nExpected:\n{}, \n\nActual:\n{}\n".format(
                    str(expectedViewpoint),
                    str(actualViewpoint)))


    def tests_original_viewpoint(self):

        # copy the prepared project file to the temporary directory
        srcFilePath = os.path.join(self.fileDirectory, self.viewpointFiles[1])
        copyfile(srcFilePath, self.viewpointDestinationPath)

        actualViewpoint = reader.buildViewpoint(srcFilePath,
                self.viewpointSchemaPath)

        # building the expected viewpoint object
        expectedExceptions = [
                viewpoint.Component(ifcId="0T_ZmDTXnD8vMdc6O2ywGw"),
                viewpoint.Component(ifcId="1R5DibLMjDRAjgX7wvDhFw")]

        expectedSelection = [
                viewpoint.Component(ifcId="2WxlJcqgXiHhEvEmREXH8o")]

        expectedViewSetuphints = viewpoint.ViewSetupHints(
                openingsVisible=False,
                spacesVisible=False,
                spaceBoundariesVisible=False)

        expectedComponents = viewpoint.Components(
                visibilityDefault=False,
                visibilityExceptions=expectedExceptions,
                selection=expectedSelection,
                viewSetuphints=expectedViewSetuphints,
                colouring=list()
                )

        expectedPCamera = viewpoint.PerspectiveCamera(
                tdv.Point(31.831852245718924, 8.3991482482556918,
                    16.610063251737976),
                tdv.Direction(-0.33103085679096667,
                    0.53391253908149949, -0.77804625342185463),
                tdv.Direction(-0.40998798211340642,
                    0.66126078591306314, 0.62820699417963755),
                60)


        expectedViewpoint = viewpoint.Viewpoint(
                id=UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
                components=expectedComponents,
                oCamera=None,
                pCamera=expectedPCamera,
                lines=[],
                clippingPlanes=[],
                bitmaps=[])


class HierarchyTest(unittest.TestCase):

    def setUp(self):
        self.testFile = "../rdwr/test_data/Issues_BIMcollab_Example.bcf"
        self.proj = reader.readBcfFile(self.testFile)

    def test_comment_hierarchy(self):
        topic = self.proj.topicList[0]
        comment = topic.comments[0]

        expectedHierarchy = [ comment, topic, self.proj ]
        actualHierarchy = comment.getHierarchyList()

        self.assertEqual(expectedHierarchy, actualHierarchy,
                "\nExpected:\n{}\n\nActual:\n{}\n\n".format(expectedHierarchy,
                    actualHierarchy))


class readBcfFileTest(unittest.TestCase):

    def setUp(self):
        self.testFile = "../rdwr/test_data/Issues_BIMcollab_Example.bcf"
        self.proj = reader.readBcfFile(self.testFile)

    def test_viewpointreference(self):
        """
        This testcase shall test whether the `viewpoint` object inside
        `markup.viewpoint` (yes I am sorry for the unfortunate naming) object
        is assigned an actual object of type viewpoint
        """

        for markup in self.proj.topicList:
            for vpRef in markup.viewpoints:
                self.assertTrue(vpRef.viewpoint is not None)


if __name__ == "__main__":
    unittest.main()
