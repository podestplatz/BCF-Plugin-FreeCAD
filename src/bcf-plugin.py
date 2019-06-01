
# detection if this script is run inside FreeCAD
try:
    import FreeCAD
except:
    pass
else:
    if FreeCAD.GuiUp:
        import FreeCADGui as FGui
        from PySide import QtCore, QtGui




"""
If run in the command line a little help shall be printed on what the user is
able to do and how.
"""
if __name__ == "__main__":
    help_str = """
This module lets you to operate on BCF files. Therefore multiple modules
can be imported:
    - bcf.reader: lets you read in the desired BCF file. Most important function
      here is: bcf.reader.readBcfFile(absolutePathToFile: str) -> Project
      The returned object is of greatest importance since you want to operate on
      it.
    - bcf.writer: lets you write out the contents of an object of type `Project`
      to the desired path. Most important function is:
      bcf.writer.writeBcfFile(project: Project, desiredPath: str)

The internal data structure implements interfaces that make it easy to operate
on a project. So have a look into ./interfaces if you are interested.
TODO: add documentation on the interfaces part.
            """
    print(help_str)
