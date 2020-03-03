import os
import sys
from PyQt5.QtWidgets import QMainWindow, QComboBox, QSpinBox, QLineEdit, QPushButton, QMessageBox, QApplication
from PyQt5.uic import loadUi
from os.path import dirname, join
import subprocess


class SetupWindow(QMainWindow):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        loadUi(os.path.join(os.path.dirname(__file__), 'client_setup.ui'), self)
        self.setWindowTitle("Chat setup")
        self.fontComboBox: QComboBox = self.fontComboBox
        self.fontSpinBox: QSpinBox = self.fontSpinBox
        self.ageSpinBox: QSpinBox = self.ageSpinBox
        self.genderComboBox: QComboBox = self.genderComboBox
        self.nameLineEdit: QLineEdit = self.nameLineEdit
        self.nicknameLineEdit: QLineEdit = self.nicknameLineEdit
        self.startButton: QPushButton = self.startButton
        self.addressLineEdit: QLineEdit = self.addressLineEdit
        self.portSpinBox: QSpinBox = self.portSpinBox

        self.startButton.clicked.connect(self.run)
        self.show()

    def run(self):
        nickname = self.nicknameLineEdit.text()
        name = self.nameLineEdit.text()
        if nickname == "" or name == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Wrong Values")
            msg.setText("Both name and nickname must be filled")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        self.hide()
        if os.name == "nt":
            status = subprocess.run(f'{join(dirname(sys.executable), "pythonw.exe")} -m chat.client.qt_client "{nickname}" "{name}" {self.ageSpinBox.text()} {self.genderComboBox.currentText()} -a {self.addressLineEdit.text()} -p {self.portSpinBox.text()} -s {self.fontSpinBox.text()} -f "{self.fontComboBox.currentText()}"')
        elif os.name == "posix":
            status = os.system(f'{sys.executable} -m chat.client.qt_client "{nickname}" "{name}" {self.ageSpinBox.text()} {self.genderComboBox.currentText()} -a {self.addressLineEdit.text()} -p {self.portSpinBox.text()} -s {self.fontSpinBox.text()} -f "{self.fontComboBox.currentText()}"')
        else:
            raise NotImplementedError("Unknown system type, please contact developer with details about your operating system.")
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = SetupWindow()
    app.exec_()