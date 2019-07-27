.PHONY: all clean run

all: plugin.ui resources.qrc
	pyside2-uic -o ui_plugin.py plugin.ui
	pyside2-rcc -o rc_resources.py resources.qrc

clean: 
	rm rc_resources.py ui_plugin.py

run: plugin.py ui_plugin.py
	python3 plugin.py

