def setupBCFFile(fileName, testFileDir, topicDir, testBCFName):

    cmd = "cp {}/{} {}/{}/viewpoint.bcfv".format(testFileDir, testFile,
        testFileDir, testTopicDir)
    project.debug("Executing: {}".format(cmd))
    os.system(cmd)

    cmd = "cd ./viewController-tests && zip -q {} {}/markup.bcf".format(testBCFName,
        topicDir)
    project.debug("Executing: {}".format(cmd))
    os.system(cmd)

    return os.path.join(testFileDir, testBCFName)


