# BCF-Plugin-FreeCAD
It is a standalone plugin aimed at the BIM Workbench of
[FreeCAD](https://github.com/FreeCAD). The aim is it to integrate
collaboration through the [BCF (BIM Collaboration Format)](https://en.wikipedia.org/wiki/BIM_Collaboration_Format). 

# Download
To use the plugin, in its current state in FreeCAD, clone it to some directory of your liking. To be able to import the modules/packages of the plugin we need to symlink the source folder (`bcfplugin`) to your FreeCAD Mod directory.
```bash
$> git clone git@github.com:podestplatz/BCF-Plugin-FreeCAD.git /path/to/repo/dir
$> ln -s /path/to/repo/dir/bcfplugin "$HOME"/.FreeCAD/Mod/BCFPlugin
```

# Dependencies
Following you will find a list of non standard python modules that might have to be installed 
manually:

- [python-dateutil](https://pypi.org/project/python-dateutil/)
- [xmlschema](https://pypi.org/project/xmlschema/)
- [pytz](https://pypi.org/project/pytz/)

I reccommend installing these packages inside a [python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). To 
create one in the current directory, and subsequently activate it, execute:

```bash
$> python3 -m venv <NAME>
$> source ./<NAME>/bin/activate
```


# Usage
All source code is contained in the directory [./bcfplugin/](https://github.com/podestplatz/BCF-Plugin-FreeCAD/tree/feature/PI_retrieval/bcfplugin). 
To import it in FreeCAD run the following command in the `Python Console`:

```python
>>> import bcfplugin
```

`bcfpluin/` contains a `__init__.py` which, upon import, checks whether the dependencies are satisfied. 

## Making FreeCAD aware of Virtual Environment

If you have installed the dependencies in a python virtual environment, FreeCAD is likely to not be aware of it. Thus you probably also got some error messages in the `Report View`. To make FreeCAD aware of the packages installed in the python virtual environment you have to execute the following steps: 

  1. Get a path to the directory in which you installed the virtual environment.
  2. Find out which python version FreeCAD is using, in my case it is `python3.6`.
  3. Check that the following path exists, relative to the root directory of you virtual environment. If it does not exist, maybe you have installed the packages for a different version of python than FreeCAD is using.
    
```
/path/to/venv/lib/python[VERSION]/site-packages
```  
  4. In the `Python console` you have to append to `sys.path` the above mentioned path like this:
    ```python
    import sys
    sys.path.append("VENV/lib/python[VERSION]/site-packages
    ```
    
## Using the nonGui frontend
To get access to the nonGui-frontend (also called programmatic interface or PI for short) the import of `bcfplugin` suffices. 
```python
>>> import bcfplugin as plugin
```
This imports all necessary functions into the plugin global namespace from `programmaticInterface.py`, thereby making them easily accessible.

Without a BCF file, however, the plugin is of little value, thus let's open a BCF file: 
```python
>>> plugin.openProject("/path/to/bcf/file.bcf")
```
If you use a file that does not comply with the standard, then you will see many error prints in the `Report view`. These notify you about what xml node exactly is not compliant. If it is a bigger BCF file, it may be that there are quite many nodes. 

But that doesn't have to concern you right now. Every node that does not comply with the standard is simply not read into the internal data model. That means you can't modify it, but still can add/update/delete to/from the model. 

To read all available topics, ordered by index run:

```python
>>> plugin.getTopics()
```

This function returns you a list of tuples. Each tuple does contain the title of the topic as first element, the second element is a reference to the topic object itself. These references are important, so save them in a variable like: 

```python 
>>> topics = [ topic[1] for topic in plugin.getTopics() ]
```

You might also want to view all comments in chronological order, related with one topic, say the first one in the list: 

```python
>>> plugin.getComments(topics[0])
```

As it was the case with the topics, `getComments()` also returns a list of tuples, here the first element is the comment itself with the name of the creator, the date of creation and the date of last modification.

But comments alone would be pretty boring, so you can retrieve a list of viewpoints associated with a given topic with

```python
>>> plugin.getViewpoints(topics[0])
```

Again, you receive a list of tuples. Apart from the reference to the viewpoint object, you get the file name of the viewpoint as first element of the tuple. 
There might be cases where you just want to view comments that are linked to certain viewpoints in a topic. To generate a list like this run:

```python
>>> viewpoints = [ vp[1] for fp in plugin.getViewpoints(topic[0]) ]
>>> plugin.getComments(topic[0], viewpoints[0])
```

In a topic might also be some IFC project files listed that the topic is associated to. You can review a list of these with: 
```python
>>> plugin.getRelevantIfcFiles(topics[0])
```

And to get a list of related documents run the function `getAdditionalDocumentReferences()` is the one for you: 

```python
>>> plugin.getAdditionalDocumentReferences(topics[0])
```

You might have noticed by now that the topic is a rather important object, so treat it with care!
If you stumble upon a member `id` in any object gotten from the plugin, please don't modify it. The BCFPlugin relies upon it!

## Debugging

If you want to show all debug messages (be warned they are a lot) then you can
enable debugging by setting the value of `util.verbosity` to `Verbosity.EVERYTHING` (to get every message the plugin wants to print or `Verbosity.INFODEBUG` to just get info and debug messages, but no error messages.
