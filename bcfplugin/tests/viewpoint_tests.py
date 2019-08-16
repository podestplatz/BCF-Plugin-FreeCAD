"""
Copyright (C) 2019 PODEST Patrick

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

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
sys.path.append("../../env/lib/python3.7/site-packages")
import bcfplugin
import bcfplugin.programmaticInterface
import bcfplugin.frontend.viewController as vC
FreeCAD.open(u"../../bcf-examples/clippingPlane_bernd/bcfexample1.FCStd")

bcfplugin.programmaticInterface.openProject("../../bcf-examples/bcfexmple_bernd.bcf")
project = bcfplugin.programmaticInterface.curProject

setCameraSettings(project, vC)
