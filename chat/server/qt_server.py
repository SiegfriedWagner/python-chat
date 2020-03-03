import os
import sys
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextBrowser, QLabel, QWidget, QLineEdit, QApplication, \
    QFileDialog
from PyQt5.uic import loadUi


class MainView(QMainWindow):

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        loadUi(os.path.join(os.path.dirname(__file__), "server.ui"), self)
        self.output_path = os.path.join(os.path.dirname(__file__), "log")
        self._buffer = ""
        self._server_process: QProcess = None

        self.startStopButton: QPushButton = self.startStopButton
        self.logTextBrowser: QTextBrowser = self.logTextBrowser
        self.formWidget: QWidget = self.formWidget
        self.portLabel: QLabel = self.portLabel
        self.portLineEdit: QLineEdit = self.portLineEdit
        self.addressLabel: QLabel = self.addressLabel
        self.addressLineEdit: QLineEdit = self.addressLineEdit
        self.outputDirectoryButton: QPushButton = self.outputDirectoryButton

        self.outputDirectoryButton.setText(self.output_path)
        self.logTextBrowser.verticalScrollBar().rangeChanged.connect(
            lambda x: self.logTextBrowser.verticalScrollBar().setValue(
                self.logTextBrowser.verticalScrollBar().maximum()))
        self.outputDirectoryButton.clicked.connect(self.set_output_path)
        self.startStopButton.clicked.connect(self.start_server)
        self.show()

    def start_server(self):
        if not self._server_process:
            self._server_process = QProcess(self)
            self._server_process.readyRead.connect(self.data_ready)
            addr = self.addressLineEdit.text()
            port = self.portLineEdit.text()
            self._server_process.start(sys.executable,
                                       ["-m",
                                        "chat.server.chat_server",
                                        "--addr", addr,
                                        "--port", port,
                                        "--output", self.output_path])
            self.startStopButton.setText("Stop server")
        else:
            self._server_process.kill()
            self._server_process = None
            self.startStopButton.setText("Start server")

    def set_output_path(self):
        diag = QFileDialog()
        diag.setFileMode(QFileDialog.Directory)
        self.output_path = diag.getExistingDirectory(self, "Folder do zapisu wyników",
                                             self.output_path)
        self.outputDirectoryButton.setText(self.output_path)

    def data_ready(self):
        prev = self.logTextBrowser.toPlainText()
        try:
            new = bytes(self._server_process.readAll()).decode("UTF-8")
            self.logTextBrowser.setText(prev + new)
        except UnicodeDecodeError:
            pass

    def closeEvent(self, QCloseEvent):
        if self._server_process:
            self._server_process.kill()
            self._server_process = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = MainView()
    app.exec_()
