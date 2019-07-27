import sys

from PySide2.QtWidgets import QApplication, QListView
from PySide2.QtGui import QStandardItem, QStandardItemModel


app = QApplication(sys.argv)

list = QListView()
list.setWindowTitle("Honey-Do-List")
#list.setMinimalSize(600, 400)

model = QStandardItemModel(list)

foods = [
        "Cookie dough",
        "Spaghetti",
        "Salad",
        "Linsen Dal",
        "Chocolate whiped cream"
]

for food in foods:
    item = QStandardItem(food)
    item.setCheckable(True)
    model.appendRow(item)

def on_item_changed(item):
    if not item.checkState():
        return
    i = 0
    while model.item(i):
        if not model.item(i).checkState():
            return
        i += 1

    app.quit()

model.itemChanged.connect(on_item_changed)
list.setModel(model)
list.show()
app.exec_()
