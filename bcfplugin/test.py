import sys
sys.path.append("/home/patrick/projects/freecad/plugin/env/lib/python3.7/site-packages")

import bcfplugin as plugin
plugin.openProject("/home/patrick/projects/freecad/plugin/bcfplugin/rdwr/test_data/Issues_BIMcollab_Example.bcf.original")

topics = [ topic[1] for topic in plugin.getTopics() ]
#plugin.addComment(topics[0], "hello world", "patrick@podest.co.at")
#plugin.getComments(topics[0])
plugin.addFile(topics[0], "aaaaaaaaaaaaaaaaaaaaaa", "", True, "home", "/home/patrick/10")
plugin.getRelevantIfcFiles(topics[0])
