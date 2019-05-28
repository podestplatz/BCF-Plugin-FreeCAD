import sys
import unittest

from shutil import copyfile
from uuid import UUID
from xmlschema import XMLSchemaValidationError

sys.path.insert(0, "../bcf")
import reader
import project

class BuildProjectTest(unittest.TestCase):
    def setUp(self):
        self.fileDirectory = "./reader_tests/"
        self.bcfFile = "Issues-Example.bcf"

        self.extractionPath = reader.extractFileToTmp(self.fileDirectory+self.bcfFile)
        self.projectFilePath = self.extractionPath + "/" + "project.bcfp"
        self.projectSchemaPath = self.fileDirectory + "project.xsd"

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



if __name__ == "__main__":
    unittest.main()
