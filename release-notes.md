v0.3:
General:
  - No error is reported when parsing camera nodes with field of view values >
    60
  - python's logging library replaces the custom logging solution

GUI:
  - Notifications are displayed in the topicMetrics window informing the user
    about the behavior of the additional documents table
  - Topics can be added
  - Projects can be created
  - Fix issues with a dark theme. 
  - The topic drop down list was replaced by an always present ordinary list 
  - The mainLayout got replaced by a QSplitter, dividing the ui now in three
    sections. 
  - Margins on the outside were removed to use more of the screen real estate. 


v0.2:
General:
  - E-Mails are now optional
  - modAuthor is cleared if no E-Mail is set and a modification is done
  - files are now used to store session information these include:
    - author's E-Mail
    - path of the temporary working directory
    - path of the extracted bcf file in the working directory
  - xml validation errors are written to a file instead of stderr
  - all created temporary files/directories are prefixed with 'bcfplugin_'

GUI:
  - BCFPlugin.FCMacro opens UI in taskpanel
  - camera settings of the object view are stored.
  - camera settings can be reset to previous state
  - a dialog was added showing information stored in a topic node
  - strings are enveloped into tr() to support translation
  - a "close without saving" dialog was added. 
  - Additional Documents in the topicMetrics window:
    - additional Documents can be opened by double clicking on the description. 
    - the path of additional documents can be copied to clipboard by double
      clicking on the path.

nonGUI:
  - closeProject() was added to the programmaticInterface
  - interactive "exit-without-saving" mode was added.



v0.1: 
UI:
  - the projects contents can be explored and changed. 
  - comments can be added
  - the current state of the project can be saved. 

nonUI:
  - everyting that can be done through the UI can also be done by using just the
    programmaticInterface.py file. 
  - viewpoints can be applied (mostly)
