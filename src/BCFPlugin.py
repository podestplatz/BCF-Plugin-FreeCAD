import sys
import bcf.util as util

def check_dependencies():
    available = True
    try:
        import dateutil
    except:
        pkg = "dateutil"
        available = False
    else:
        try:
            import xmlschema
        except:
            pkg = "xmlschema"
            available = False

    if not available:
        util.printErr("Could not find the module `xmlschema`. Install it through"\
                " pip\n\tpip install {}\nYou also might want to"\
                " install it in a virtual environment. To create and initialise"\
                " said env execute\n\tpython -m venv <NAME>\n\tsource"\
                " ./<NAME>/bin/activate".format(pkg))
        util.printInfo("If you already have it installed inside a virtual environment" \
                ", no problem we just need to modify the `sys.path` variable a"\
                " bit. python inside FreeCAD, unfortunately, is not aware by" \
                " default, of a virtual environment. To do that you have to " \
                " execute a few steps:\n"\
                "\t1. find the folder in which your venv is located,\n"\
                "\t2. find out with which python version FreeCAD was compiled,\n"\
                "\t3. execute `sys.path.append('/path/to/venv/lib/python<VERSION>/site-packages')`"\
                "\nIf that fails, try to run `import sys` and execute it"\
                " again.")
    return available


def setup():
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
        return

    import frontend.programmaticInterface as plugin

    project = plugin.openProject("./bcf/test_data/Issues_BIMcollab_Example.bcf.original")
    topics = plugin.getTopics()
    a = lambda x: x[1].index
    util.printInfo([ a(topic) for topic in topics ])

    viewpoints = plugin.getViewpoints(topics[0][1])
    util.printInfo(viewpoints)

    comments = plugin.getComments(topics[0][1], viewpoints[0][1])
    util.printInfo(comments)

    files = list()
    for (topicUUID, topic) in topics:
        files.append(plugin.getRelevantIfcFiles(topic))
    util.printInfo(files)


# detection if this script is run inside FreeCAD
try:
    import FreeCAD
except:
    pass
else:
    util.FREECAD = True
    if FreeCAD.GuiUp:
        import FreeCADGui as FGui
        from PySide import QtCore, QtGui
        util.GUI = True

if check_dependencies():
    import frontend.programmaticInterface as plugin


"""
If run in the command line a little help shall be printed on what the user is
able to do and how.
"""
if __name__ == "__main__":
    setup()

