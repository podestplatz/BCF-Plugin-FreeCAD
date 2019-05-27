import os
import urllib.request
from enum import Enum
from xmlschema import XMLSchema

class Schema(Enum):
    EXTENSION = 1
    VSINFO = 2 # viewpoint info
    MARKUP = 3
    PROJECT = 4
    VERSION = 5

__schemaSrc = "https://raw.githubusercontent.com/buildingSMART/BCF-XML/{0}/{1}Schemas/{2}"
__schemaVersion = "release_2_1"
__schemaMap = {
        Schema.EXTENSION: __schemaSrc.format(__schemaVersion,
            "Extension%20",
            "extensions.xsd"),
        Schema.PROJECT: __schemaSrc.format(__schemaVersion,
            "",
            "project.xsd"),
        Schema.MARKUP: __schemaSrc.format(__schemaVersion,
            "",
            "markup.xsd"),
        Schema.VERSION: __schemaSrc.format(__schemaVersion,
            "",
            "version.xsd"),
        Schema.VSINFO: __schemaSrc.format(__schemaVersion,
            "",
            "visinfo.xsd")}


def retrieveWebFile(schema: Schema, storePath: str):

    """
    Tries to retrieve the XML Schema Definition file, identified by `schema`
    from the url stored in `__schemaMap`. If the file could be loaded it is
    stored at `storePath`.
    Returns `None` if an error occurs or the path of the written file if
    successful.
    """

    fileUrl = __schemaMap[schema]
    try:
        with urllib.request.urlopen(fileUrl) as response:
            schemaContent = response.read()
            with open(storePath, "wb+") as file:
                file.write(schemaContent)
    except URLError as e:
        print("Could not retrieve {}".format(fileURL))
        print("Here is the stack trace {}".format(str(e)))
        return None
    except Exception as e:
        print("Error occured: {}".format(str(e)))
        return None
    else:
        return storePath


def schemaValidate(schemaPath: str, xmlFile: str):

    """
    Takes the schemaFile and loads it into the module xmlschema. With the
    resulting object `xmlFile` is checked whether it adheres to the
    specification or not.
    Returns a tuple: first element is a boolean value, and the second is a
    string containing the error message.
    """

    if not (os.path.exists(schemaPath) or os.path.exists(xmlFile)):
        raise ValueError

    schema = XMLSchema(schemaPath)
    valid = schema.is_valid(xmlFile)
    print("validating {} against {}".format(xmlFile, schemaPath))
    if valid:
        return (valid, "")
    else:
        try:
            # it is going to fail. I want the error message to return it
            schema.validate(xmlFile)
        except Exception as e:
            return (valid, str(e))


if __name__ == "__main__":
    for key in __schemaMap:
        retrieveWebFile(key, "test{}".format(str(key)))
    try:
        (valid, error) = schemaValidate("testSchema.PROJECT", "project.bcfp")
    except ValueError as e:
        print("One of the files does not exist. Here is the stack trace:\
                {}".format(str(e)))
    if valid:
        print("File is valid")
    else:
        print("File is not valid because:\n{}".format(error))
