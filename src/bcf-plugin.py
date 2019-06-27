import sys

# detection if this script is run inside FreeCAD
try:
    import FreeCAD
except:
    pass
else:
    if FreeCAD.GuiUp:
        import FreeCADGui as FGui
        from PySide import QtCore, QtGui

def check_dependencies():
    try:
        import dateutil
    except:
        print("Could not find the module `python-dateutil`. Install it through"\
                " pip\n\tpip install python-dateutil\nYou also might want to"\
                "install it in a virtual environment. To create and initialise"\
                "said env execute\n\tpython -m venv <NAME>\n\tsource"\
                " ./<NAME>/bin/activate", file=sys.stderr)
        return False
    else:
        try:
            import xmlschema
        except:
            print("Could not find the module `xmlschema`. Install it through"\
                    " pip\n\tpip install python-dateutil\nYou also might want to"\
                    " install it in a virtual environment. To create and initialise"\
                    " said env execute\n\tpython -m venv <NAME>\n\tsource"\
                    " ./<NAME>/bin/activate", file=sys.stderr)
            return False

    return True



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
      bcf.writer.addUpdate(project: Project, element, prevVal)

The internal data structure implements interfaces that make it easy to operate
on a project. So have a look into ./interfaces if you are interested.
TODO: add documentation on the interfaces part.
            """
    #print(help_str)
    if not check_dependencies():
        exit(1)

    import frontend.programmaticInterface as plugin
    project = plugin.openProject("./bcf/test_data/Issues_BIMcollab_Example.bcf.original")
    topics = plugin.getTopics()
    a = lambda x: x[1].index
    print([ a(topic) for topic in topics ])
    comments = plugin.getComments(topics[0][1])
    print(comments)
