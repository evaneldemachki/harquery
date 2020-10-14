from PyQt5 import QtCore, QtGui, QtWidgets
from harquery import *
from harquery.query import execute
from harquery.tree import index_profile
import pprint

def fill_model(obj, entry):
    for key, item in entry.items():
        if key != "{hash}":
            child = QtGui.QStandardItem(key)
            obj.appendRow(child)
            print(child)
            fill_model(child, item)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1038, 705)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setStyleSheet("background-color: #36393F;\n"
"color: rgb(255, 255, 255)")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.active = None
        self.focus = None

        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 361, 661))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.profilesLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight")
        font.setPointSize(12)
        self.profilesLabel.setFont(font)
        self.profilesLabel.setObjectName("profilesLabel")
        self.verticalLayout.addWidget(self.profilesLabel)

        self.profilesTree = QtWidgets.QTreeView(self.centralwidget)
        self.profilesTree.setHeaderHidden(True)
        self.profilesTree.setObjectName("profilesTree")
        self.profilesTree.clicked.connect(self.load_profile)

        self.verticalLayout.addWidget(self.profilesTree)

        model = QtGui.QStandardItemModel()
        data = {}
        for key in profiles: 
            data[key] = index_profile(profiles[key]._cursor)

        fill_model(model, data)
        self.profilesTree.setModel(model)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.profilesEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.profilesEdit.setFont(font)
        self.profilesEdit.setText("")
        self.profilesEdit.setObjectName("profilesEdit")
        self.horizontalLayout.addWidget(self.profilesEdit)

        self.addProfileButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.addProfileButton.setObjectName("addProfileButton")
        self.addProfileButton.clicked.connect(self.add_profile)
        self.horizontalLayout.addWidget(self.addProfileButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.filtersLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiLight")
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.filtersLabel.setFont(font)
        self.filtersLabel.setObjectName("filtersLabel")
        self.verticalLayout.addWidget(self.filtersLabel)

        self.filtersList = QtWidgets.QListWidget(self.verticalLayoutWidget)
        self.filtersList.setObjectName("filtersList")
        self.verticalLayout.addWidget(self.filtersList)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.filtersEdit = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.filtersEdit.setFont(font)
        self.filtersEdit.setObjectName("filtersEdit")

        self.horizontalLayout_2.addWidget(self.filtersEdit)

        self.addFilterButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.addFilterButton.setObjectName("addFilterButton")
        self.addFilterButton.clicked.connect(self.add_filter)

        self.horizontalLayout_2.addWidget(self.addFilterButton)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.profilesBrowser = QtWidgets.QListWidget(self.centralwidget)
        self.profilesBrowser.setGeometry(QtCore.QRect(370, 30, 661, 631))
        self.profilesBrowser.setObjectName("profilesList")
        self.profilesBrowser.itemDoubleClicked.connect(self.load_entry)

        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(370, 0, 661, 27))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.browserLabel = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.browserLabel.setMinimumSize(QtCore.QSize(150, 0))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.browserLabel.setFont(font)
        self.browserLabel.setObjectName("browserLabel")
        self.horizontalLayout_3.addWidget(self.browserLabel)

        self.focusEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.focusEdit.setFont(font)
        self.focusEdit.setText("")
        self.focusEdit.setObjectName("focusEdit")
        self.horizontalLayout_3.addWidget(self.focusEdit)

        self.setFocusButton = QtWidgets.QPushButton(self.horizontalLayoutWidget_3)
        self.setFocusButton.setObjectName("setFocusButton")
        self.setFocusButton.clicked.connect(self.set_focus)

        self.horizontalLayout_3.addWidget(self.setFocusButton)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1038, 21))
        self.menubar.setObjectName("menubar")
        self.menuPresets = QtWidgets.QMenu(self.menubar)
        self.menuPresets.setObjectName("menuPresets")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionFilters = QtWidgets.QAction(MainWindow)
        self.actionFilters.setObjectName("actionFilters")

        self.actionHeaders = QtWidgets.QAction(MainWindow)
        self.actionHeaders.setObjectName("actionHeaders")

        self.menuPresets.addAction(self.actionFilters)
        self.menuPresets.addAction(self.actionHeaders)
        self.menubar.addAction(self.menuPresets.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Harquery GUI"))

        __sortingEnabled = self.profilesBrowser.isSortingEnabled()

        self.profilesLabel.setText(_translate("MainWindow", "Profiles"))
        self.addProfileButton.setText(_translate("MainWindow", "Add Profile"))
        self.filtersLabel.setText(_translate("MainWindow", "Filters"))
        self.addFilterButton.setText(_translate("MainWindow", "Add Filter"))
        self.browserLabel.setText(_translate("MainWindow", ""))
        self.setFocusButton.setText(_translate("MainWindow", "Set Focus"))
        self.menuPresets.setTitle(_translate("MainWindow", "Presets"))
        self.actionFilters.setText(_translate("MainWindow", "Filters"))
        self.actionHeaders.setText(_translate("MainWindow", "Headers"))

        self.active = profiles[self.profilesTree.model().item(0).text()]
        self.focus = self.active._focus["string"]
        self.show_profile()
    
    def add_profile(self):
        prof = self.profilesEdit.text()
        if prof == "":
            return

        profile = profiles.add(prof)
        self.profilesEdit.clear()
        index = {prof: index_profile(profile._cursor)}
        fill_model(self.profilesTree.model(), index)

    def show_profile(self):
        _translate = QtCore.QCoreApplication.translate

        self.profilesBrowser.clear()

        if self.active._is_empty("SHOW"):
            return

        title = ">".join(self.active._cursor)
        self.browserLabel.setText(_translate("MainWindow", title))

        self.focusEdit.setText(_translate("MainWindow", self.focus))
        self.active.focus(self.focus)

        print(self.focus)
        data = execute(self.active._obj, self.active._focus["object"], "focus")
        for i in range(len(data)):
            item = QtWidgets.QListWidgetItem()

            if len(str(data[i])) < 200:
                item_repr = str(data[i])
            else:
                item_repr = "[exceeds max size]"

            item.setText(_translate("MainWindow", str(item_repr)))
            self.profilesBrowser.addItem(item)
        
        self.filtersList.clear()
        for filt in self.active.filters:
            filt_string = filt["string"]
            item = QtWidgets.QListWidgetItem()
            item.setText(_translate("MainWindow", filt_string))
            self.filtersList.addItem(item)
        
    def load_entry(self):
        self.popup = QtWidgets.QWidget()

        item = QtWidgets.QTextBrowser(self.popup)
        item.setGeometry(QtCore.QRect(0, 0, 1000, 1000))

        index = self.centralwidget.sender().currentRow()
        item.setText(pprint.pformat(self.active.get(index)))
        self.popup.show()
    
    def load_profile(self, index):
        self.profilesBrowser.clear()
        self.filtersList.clear()

        cursor = []
        entry = index.model().itemFromIndex(index)
        cursor.append(entry.text())

        while entry.parent() is not None:
            entry = entry.parent()
            cursor.append(entry.text())
        
        cursor = list(reversed(cursor))

        profile = profiles[cursor[0]]
        for c in cursor[1:]:
            profile.cd(c)

        self.active = profile
        self.show_profile()

    def add_filter(self):
        if self.active is None:
            return

        filt = self.filtersEdit.text()
        profile = self.active

        try:
            profile.filters.add(filt)
            self.show_profile()
            profile.save()
        except Exception as error:
            print(str(error))

        self.filtersEdit.clear()
    
    def set_focus(self):
        if self.active is None:
            return
        
        focus = self.focusEdit.text()
        profile = self.active

        try:
            profile.focus(focus)
            self.focus = focus
            self.show_profile()
            profile.save()
        except Exception as error:
            print(str(error))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
