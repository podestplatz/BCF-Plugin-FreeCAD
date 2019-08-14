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

import sys
import os
if __name__ == "__main__":
    sys.path.insert(0, "../")
    sys.path.append("../../env/lib/python3.7/site-packages")
    FreeCAD.open(u"../../bcf-examples/clippingPlane_bernd/bcfexample1.FCStd")

import util

import programmaticInterface as pI
import frontend.viewController as vC


def setupBCFFile(testFile, testFileDir, topicDir, testBCFName):

    cmd = "cp {}/{} {}/{}/viewpoint.bcfv".format(testFileDir, testFile,
        testFileDir, topicDir)
    print("Executing: {}".format(cmd))
    os.system(cmd)

    cmd = "cd ./{} && zip -q {} {}/viewpoint.bcfv".format(testFileDir, testBCFName,
        topicDir)
    print("Executing: {}".format(cmd))
    os.system(cmd)

    return os.path.join(testFileDir, testBCFName)


def test_letLinesDraw():

    topics = [ topic[1] for topic in pI.getTopics() ]
    viewpoints = [ vp[1] for vp in pI.getViewpoints(topics[0]) ]
    vC.createLines(viewpoints[0].lines)


def test_addClipPlanes():

    topics = [ topic[1] for topic in pI.getTopics() ]
    viewpoints = [ vp[1] for vp in pI.getViewpoints(topics[0]) ]
    clippingPlanes = viewpoints[0].clippingPlanes
    clip = clippingPlanes[0]

    vC.createClippingPlane(clip)


#if __name__ == "__main__":
testFileDir = "viewController-tests"
testBCFFile = "bcfexmple_bernd.bcf"

setupBCFFile("viewpoint_with_lines.bcfv", "viewController-tests",
    "d7301aa6-3533-4031-b209-9e1c701802f5", "bcfexmple_bernd.bcf")
pI.openProject("./{}/{}".format(testFileDir, testBCFFile))

test_letLinesDraw()
test_addClipPlanes()
