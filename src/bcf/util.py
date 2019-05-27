import urllib.request
from enum import Enum

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

#TODO: write error handling code, and document function
def retrieveWebFile(schema: Schema, storePath: str):
    fileUrl = __schemaMap[schema]
    print("Retrieving file from: {}".format(fileUrl))
    with urllib.request.urlopen(fileUrl) as response:
        schemaContent = response.read()
        with open(storePath, "wb+") as file:
            file.write(schemaContent)


if __name__ == "__main__":
    for key in __schemaMap:
        retrieveWebFile(key, "test{}".format(str(key)))
