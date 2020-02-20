import string
import time
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QApplication, QTextEdit, QLabel, QPushButton, QScrollArea, QSizePolicy
from PyQt5.uic import loadUi
import os
import sys
import socket
import argparse
from MessageWidget import MessageWidget
from message import ChatMessage, LogMessage, Serializable, IntroductionMessage
from configuration import  MSG_TERMINATOR


class ChatClient(QObject):

    class Reader(QObject):

        onReceive = pyqtSignal(bytes)

        def __init__(self, connection):
            super().__init__()
            self.connection = connection
            self.is_open = True

        def read(self):
            buffer = b""
            print("started reading")
            while self.is_open:
                try:
                    buffer += self.connection.recv(4096)
                    if buffer.endswith(MSG_TERMINATOR):
                        buffer.strip(MSG_TERMINATOR)
                        self.onReceive.emit(buffer)
                        buffer = b""
                        print("read emited")
                except socket.timeout as e:
                    buffer = b""
                    print("timeout occuread")


    def __init__(self, intro_msg):
        """
        Socket client that support async communication.
        :param sock: socket to ther other end of communication
        :param incoming_queue: deque that retrieves incoming messages
        :param outcoming_queue: deque that contains message to send to other end of communication
        """
        super().__init__()
        self.connection = None
        self.reader = None
        self._read_thread = None
        self.intro_msg : IntroductionMessage = intro_msg

    @property
    def is_open(self):
        return True if self.connection else False

    @property
    def onReceive(self):
        if self.reader:
            return self.reader.onReceive
        else:
            raise Exception("Establish connection before geting access to signal")

    def connect(self, address, port):
        self.connection = socket.create_connection((address, port), 10)
        self._read_thread = QThread(self)
        self.reader = self.Reader(self.connection)
        self.reader.moveToThread(self._read_thread)
        self._read_thread.started.connect(self.reader.read)
        self._read_thread.start()
        self.connection.send(bytes(self.intro_msg) + MSG_TERMINATOR)

    @pyqtSlot(bytes)
    def write(self, message: bytes):
        print("write called")

        if self.is_open:
            obj_to_send = Serializable.from_bytes(message)
            if type(obj_to_send) is ChatMessage:
                obj_to_send.sender = self.intro_msg.nickname
            self.connection.send(bytes(obj_to_send) + MSG_TERMINATOR)
        else:
            raise Exception("Cannot write to closed connection")

    def close(self):
        if self.is_open:
            self._read_thread.terminate()
            self.connection.close()
            self.connection = None


class MainView(QMainWindow):

    onSend = pyqtSignal(bytes)

    def __init__(self, font_size, font_family, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        loadUi(os.path.join(os.path.dirname(__file__), "client.ui"), self)
        self.font_size = int(font_size)
        self.font_family = font_family
        self.inputTextEdit: QTextEdit = self.inputTextEdit
        self.scrollArea: QScrollArea = self.scrollArea
        self.sendButton: QPushButton = self.sendButton
        self.sendButton.clicked.connect(self.on_send)
        self.inputTextEdit.textChanged.connect(self.on_text_change)
        self.inputTextEdit.keyPressEvent = self.keyPressEvent
        self.inputTextEdit.setFont(QFont(self.font_family, self.font_size))
        self.scrollArea.verticalScrollBar().rangeChanged.connect(
            lambda x: self.scrollArea.verticalScrollBar().setValue(
                self.scrollArea.verticalScrollBar().maximum()))
        self.prevetext = ""
        self.show()

    def on_send(self):
        text = self.inputTextEdit.toPlainText()
        chat_message = ChatMessage(timestamp=time.time(), sender="Ty", text=text)
        self.addMessage(chat_message)
        self.inputTextEdit.setText("")
        self.onSend.emit(bytes(chat_message))

    @pyqtSlot(bytes)
    def on_receive(self, message: bytes):
        cmessage = ChatMessage.from_bytes(message)
        self.addMessage(cmessage)
        self.onSend.emit(bytes(LogMessage(cmessage.sender, "RECEIVED", cmessage.text, time.time())))

    def on_text_change(self):
        text = self.inputTextEdit.toPlainText()
        if len(self.prevetext) < len(text):
            if text.strip() != text and len(text) > 1 and text[-2] not in string.whitespace:
                splited = text.split()
                if len(splited) > 1 or len(splited) == 1 and text[-2] == text.strip()[-1]:
                    print(splited[-1])
                    self.onSend.emit(bytes(LogMessage("", "WORD", splited[-1], time.time())))
        self.prevetext = text

    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key_Return and not QApplication.queryKeyboardModifiers() == Qt.ShiftModifier:
            self.on_send()
        else:
            QTextEdit.keyPressEvent(self.inputTextEdit, a0)

    def addMessage(self, message: ChatMessage):
        widget = self.scrollArea.widget()
        label = MessageWidget(message=message,
                              font_size=self.font_size,
                              font_family=self.font_family)
        widget.layout().addWidget(label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("nickname", help="Nickname in chat")
    parser.add_argument("name", help="Name of subject")
    parser.add_argument("age", help="Subject age")
    parser.add_argument("gender", help="Subject gender")
    parser.add_argument("-a", "--addr", default='127.0.0.1', help="Ip address of chat server")
    parser.add_argument("-p", "--port", default=5000, help="Port number of chat server")
    parser.add_argument('-s', '--font-size', default=13, help="Chat font size")
    parser.add_argument('-f', '--font-family', default='Helvetica', help='Chat font family')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    client = ChatClient(IntroductionMessage(nickname=args.nickname, name=args.name, gender=args.gender, age=args.age))
    view = MainView(font_size=args.font_size, font_family=args.font_family)
    view.setWindowTitle(args.nickname)
    client.connect(args.addr, args.port)
    view.onSend.connect(client.write)
    client.onReceive.connect(view.on_receive)
    app.exec_()
    sys.exit(0)

