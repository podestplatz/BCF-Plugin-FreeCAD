import copy
import bcf.writer as w
import bcf.project as p
from interfaces.identifiable import Identifiable
from interfaces.hierarchy import Hierarchy
from interfaces.state import State




def deleteObject(project, object):

    if not issubclass(type(object), Identifiable):
        raise ValueError("Cannot delete {} since it doesn't inherit from"\
            " interfaces.Identifiable".format(object))

    if not issubclass(type(object), Hierarchy):
        raise ValueError("Cannot delete {} since it seems to be not part of" \
            " the data model. It has to inherit from"\
            " hierarchy.Hierarchy".format(object))

    # find out the name of the object in its parent
    object.state = State.States.DELETED

    projectCpy = copy.deepcopy(project)
    newObject = projectCpy.searchObject(object)
    w.addProjectUpdate(projectCpy, newObject, None)
    result = w.processProjectUpdates()

    # `result == None` if the update could not be processed.
    # ==> `result == projectCpy` will be returned to stay on the errorenous
    # state and give the user the chance to fix the issue.
    if result is not None:
        return result[0]

    # otherwise the updated project is returned
    else:
        project.deleteObject(object)
        return project
