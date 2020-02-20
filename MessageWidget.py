from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLabel, QSpacerItem, QFrame, QVBoxLayout
from PyQt5.uic import loadUi
import os
from message import ChatMessage


class MessageWidget(QFrame):

    def __init__(self, message: ChatMessage, font_size, font_family, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        widget = QWidget(None)
        loadUi(os.path.join(os.path.dirname(__file__), "message.ui"), widget)
        widget.messageLabel.setFont(QFont(font_family, font_size))
        widget.senderLabel.setFont(QFont(font_family, font_size))
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(widget)
        widget.messageLabel: QLabel = widget.messageLabel
        widget.senderLabel: QLabel = widget.senderLabel
        widget.setAutoFillBackground(True)
        # self.senderAndMessengerSpacer: QSpacerItem = self.senderAndMessengerSpacer
        widget.messageLabel.setText(message.text)
        widget.senderLabel.setText(message.sender)
        self.setLineWidth(10)
        self.setFrameStyle(QFrame.StyledPanel + QFrame.Raised)
        self.setLayout(layout)

