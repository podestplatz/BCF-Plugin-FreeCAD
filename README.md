# BCF-Plugin-FreeCAD
It is a standalone plugin aimed at the BIM Workbench of
[FreeCAD](https://github.com/FreeCAD). The aim is it to integrate
collaboration through the [BCF (BIM Collaboration Format)](https://en.wikipedia.org/wiki/BIM_Collaboration_Format). 

# Download
Currently this plugin in development, and atm cannot be integrated into FreeCAD. If 
you want to git it a try you might have to clone it (or download it as archive):
```bash
$> git clone git@github.com:podestplatz/BCF-Plugin-FreeCAD.git
```

# Dependencies
Following a list of non standard python modules that might have to be installed 
manually:

- [python-dateutil](https://pypi.org/project/python-dateutil/)
- [xmlschema](https://pypi.org/project/xmlschema/)

I reccommend installing these packages inside a [python virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/). To 
create one in the current directory, and subsequently activate it, execute:

```bash
$> python3 -m venv <NAME>
$> source ./<NAME>/bin/activate
```


# Usage
All source code is contained in the directory [./src/](https://github.com/podestplatz/BCF-Plugin-FreeCAD/tree/master/src). There also the main file `bcf-plugin.py` resides. To use the plugin in the terminal 
just run from inside the src directory: 

```bash
$> python3 -i bcf-plugin.py
```

This will drop you in the interactive mode with the plugin, as it is, loaded. 
Now, to read in a BCF file (I am using here teh example BCF file I have stored under `./src/bcf/test_data/Issues_BIMcollab_Example.bcf`):
```python
>>> project = reader.readBcfFile("./bcf/test_data/Issues_BIMcollab_Example.bcf")
```
With `project` you have the complete data model (i.e.: contents of the BCF file at your fingertips). 
Note: currently the contents of a BCF file have to comply with the XSD files provided by [buildingSMART](https://github.com/buildingSMART/BCF-XML/tree/release_2_1/Schemas).
Unfortunately some BCF files ship with an empty header node, which is prohibited by `markup.xsd`. So at 
the moment these files have to be modified manually. 

`project` has a member `topicList` which is a list of all topics that were found inside the BCF file. 
Each element of `topicList` is of type `Markup` which contains the contents of a `markup.bcf` file. In such
a file a node `Topic` is defined with its properties. 
So in order to access the properties of any given topic run:
```python
>>> # replace N with the index of the topic and PROPERTY with the name of the property you want to access
>>> project.topicList[N].topic.PROPERTY 
>>> # for example print the title of every topic contained
>>> for markup in project.topicList:
...     print(markup.topic.title)
...
>>>
```

The following commands update the `title` property of the first topic, and write it to file using `writer`: 
```python
>>> topic = project.topicList[0].topic
>>> curTitle = topic.title
>>> topic.title = "Hello World"
>>> writer.modifyElement(topic._title, curTitle)
```
Note how in the last line the member `_title` was passed to `modifyElement()` instead of `title`. 
`modifyElement()` expects an object of type `SimpleElement`, `Attribute` or of one defined in `./src/bcf`. 
Every member prefixed with '\_' accesses a member of type `SimpleElement` or `Attribute`, whereas the same
member without the prefix accesses directly the value. For more information on this please see the 
[wiki page](https://github.com/podestplatz/BCF-Plugin-FreeCAD/wiki/BCF-Package#representation-of-simple-slements-and-attributes)
