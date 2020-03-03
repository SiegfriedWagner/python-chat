from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
import os
from .message import ChatMessage


class MessageWidget(QWidget):

    def __init__(self, message: ChatMessage, font_size, font_family, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        loadUi(os.path.join(os.path.dirname(__file__), "message.ui"), self)
        self.messageLabel.setFont(QFont(font_family, font_size))
        self.senderLabel.setFont(QFont(font_family, font_size))
        self.messageLabel.setText(message.text)
        self.senderLabel.setText(message.sender)
