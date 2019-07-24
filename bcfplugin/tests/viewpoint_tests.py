def setCameraSettings(project, vC):

    firstTopic = project.topicList[0]
    firstViewpintRef = firstTopic.viewpoints[0]
    viewpoint = firstViewpintRef.viewpoint

    camSettings = None
    if viewpoint.oCamera is not None:
        camSettings = viewpoint.oCamera
        vC.setOCamera(camSettings)
    elif viewpoint.pCamera is not None:
        camSettings = viewpoint.pCamera
        vC.setPCamera(camSettings)

    #vC.setCamera(camSettings.viewPoint, camSettings.direction,
            #camSettings.upVector)



import sys
sys.path.append("/home/patrick/projects/freecad/plugin/env/lib/python3.7/site-packages")
import bcfplugin
import bcfplugin.programmaticInterface
import bcfplugin.frontend.viewController as vC
FreeCAD.open(u"/home/patrick/projects/freecad/plugin/bcf-examples/clippingPlane_bernd/bcfexample1.FCStd")

bcfplugin.programmaticInterface.openProject("/home/patrick/projects/freecad/plugin/bcf-examples/bcfexmple_bernd.bcf")
project = bcfplugin.programmaticInterface.curProject

setCameraSettings(project, vC)
