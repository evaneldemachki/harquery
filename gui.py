from PyQt5 import QtCore, QtGui, QtWidgets
from harquery import *
from harquery.query import execute
import pprint

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(801, 593)

        self.active = None

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.profilesList = QtWidgets.QListWidget(self.centralwidget)
        self.profilesList.setGeometry(QtCore.QRect(10, 40, 256, 231))
        self.profilesList.setObjectName("profilesList")
        self.profilesList.itemPressed.connect(self.load_profile)

        # ADDING PROFILES:
        self.profiles = []
        for profile in profiles:
            item = QtWidgets.QListWidgetItem()
            self.profiles.append(item)
            self.profilesList.addItem(item)

        self.profilesHeader = QtWidgets.QLabel(self.centralwidget)
        self.profilesHeader.setGeometry(QtCore.QRect(10, 0, 181, 31))
        self.profilesHeader.setAlignment(QtCore.Qt.AlignCenter)
        self.profilesHeader.setObjectName("profilesHeader")

        self.addProfileButton = QtWidgets.QPushButton(self.centralwidget)
        self.addProfileButton.setGeometry(QtCore.QRect(220, 0, 41, 31))
        self.addProfileButton.setObjectName("addProfileButton")

        self.filtersHeader = QtWidgets.QLabel(self.centralwidget)
        self.filtersHeader.setGeometry(QtCore.QRect(50, 280, 181, 31))
        self.filtersHeader.setAlignment(QtCore.Qt.AlignCenter)
        self.filtersHeader.setObjectName("filtersHeader")

        self.addFilterButton = QtWidgets.QPushButton(self.centralwidget)
        self.addFilterButton.setGeometry(QtCore.QRect(220, 520, 41, 31))
        self.addFilterButton.setObjectName("addFilterButton")
        self.addFilterButton.clicked.connect(self.add_filter)

        self.filtersList = QtWidgets.QListWidget(self.centralwidget)
        self.filtersList.setGeometry(QtCore.QRect(10, 320, 251, 191))
        self.filtersList.setObjectName("filtersList")

        self.profileBrowser = QtWidgets.QListWidget(self.centralwidget)
        self.profileBrowser.setGeometry(QtCore.QRect(280, 40, 501, 511))

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.profileBrowser.sizePolicy().hasHeightForWidth())

        self.profileBrowser.setSizePolicy(sizePolicy)
        self.profileBrowser.setMaximumSize(QtCore.QSize(981, 16777215))
        self.profileBrowser.setObjectName("profileBrowser")

        self.profileTitle = QtWidgets.QLabel(self.centralwidget)
        self.profileTitle.setGeometry(QtCore.QRect(280, 0, 151, 31))
        self.profileTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.profileTitle.setObjectName("profileTitle")
        self.profileViewLabel = QtWidgets.QLabel(self.centralwidget)
        self.profileViewLabel.setGeometry(QtCore.QRect(440, 0, 341, 31))
        self.profileViewLabel.setObjectName("profileViewLabel")

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(10, 519, 201, 31))
        self.lineEdit.setObjectName("lineEdit")

        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 801, 21))
        self.menubar.setObjectName("menubar")

        self.menuProfiles = QtWidgets.QMenu(self.menubar)
        self.menuProfiles.setObjectName("menuProfiles")

        self.menuEndpoints = QtWidgets.QMenu(self.menubar)
        self.menuEndpoints.setObjectName("menuEndpoints")

        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")

        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuProfiles.menuAction())
        self.menubar.addAction(self.menuEndpoints.menuAction())

        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Harquery GUI"))

        __sortingEnabled = self.profilesList.isSortingEnabled()

        self.profilesList.setSortingEnabled(False)

        # Add profile text on window load:
        profile_names = list(profiles)
        for i in range(len(self.profiles)):
            profile = self.profiles[i]
            profile.setText(_translate("MainWindow", profile_names[i]))

        self.profilesList.setSortingEnabled(__sortingEnabled)

        self.profilesHeader.setText(_translate("MainWindow", "PROFILES"))
        self.addProfileButton.setText(_translate("MainWindow", "+"))

        self.filtersHeader.setText(_translate("MainWindow", "FILTERS"))
        self.addFilterButton.setText(_translate("MainWindow", "+"))

        __sortingEnabled = self.filtersList.isSortingEnabled()

        self.filtersList.setSortingEnabled(False)

        self.filtersList.setSortingEnabled(__sortingEnabled)
        self.profileTitle.setText(_translate("MainWindow", ""))
        self.profileViewLabel.setText(_translate("MainWindow", ""))
        self.menuProfiles.setTitle(_translate("MainWindow", "Profiles"))
        self.menuEndpoints.setTitle(_translate("MainWindow", "Endpoints"))
    
    def show_profile(self):
        _translate = QtCore.QCoreApplication.translate
        profile = self.active

        if profile._is_empty("SHOW"):
            self.profileBrowser.setText("<EMPTY>")
            return

        title = ">".join(profile._cursor)
        
        self.profileTitle.setText(_translate("MainWindow", title))
        self.profileViewLabel.setText(_translate("MainWindow", profile._focus["string"]))

        data = execute(profile._obj, profile._focus["object"], "focus")
        for i in range(len(data)):
            item = QtWidgets.QListWidgetItem()

            if type(data[i]) not in [str, int, float]:
                item_repr = type(data[i])
            else:
                item_repr = data[i]

            item.setText(_translate("MainWindow", item_repr))

            self.profileBrowser.addItem(item)
        
        for filt in profile.filters:
            filt_string = filt["string"]
            item = QtWidgets.QListWidgetItem()
            item.setText(_translate("MainWindow", filt_string))
            self.filtersList.addItem(item)
    
    def load_profile(self):
        self.profileBrowser.clear()
        self.filtersList.clear()

        index = self.centralwidget.sender().currentRow()
        profile = profiles[self.profiles[index].text()]
        self.active = profile

        self.show_profile()

    def add_filter(self):
        if self.active is None:
            return

        filt = self.lineEdit.text()
        profile = self.active

        try:
            profile.filters.add(filt)
            self.profileBrowser.clear()
            self.show_profile()
            profile.save()
        except:
            print("idk man fix this shit")

        self.lineEdit.clear()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
