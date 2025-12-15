# Copyright 2025 Xu Yan (EulbThgink), https://github.com/EulbThgink/Icenberg
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import re

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PySide6.QtWidgets import QTextBrowser

THINK_RE = re.compile('(<think>.*?</think>)(.*)', re.DOTALL)


class LlmChatMainWidget(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: white;
                width: 3px;
            }
            QScrollBar::handle:vertical {
                background: #3B85D5;
                min-height: 100px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: white;
                height: 3px;
            }
            QScrollBar::handle:horizontal {
                background: #3B85D5;
                min-width: 100px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.original_format = self.currentCharFormat()
        self.user_title_format = QTextCharFormat()
        self.user_title_format.setFontWeight(QFont.Weight.Bold)
        self.user_title_format.setForeground(QColor("#3f7BF1"))

        self.llm_title_format = QTextCharFormat()
        self.llm_title_format.setFontWeight(QFont.Weight.Bold)
        self.llm_title_format.setForeground(QColor("#7821A3"))

        self.llm_think_format = QTextCharFormat()
        self.llm_think_format.setForeground(QColor("#7f7f7f"))

        self.insert_cursor = QTextCursor(self.document())
        self.insert_cursor.movePosition(QTextCursor.MoveOperation.End)

        self.__is_think = False

    def paint_user_message(self, message: str, llm_model_name: str = None):
        self.insert_cursor.setCharFormat(self.user_title_format)
        self.insert_cursor.insertText("You:\n")
        self.insert_cursor.setCharFormat(self.original_format)
        self.insert_cursor.insertText(message + "\n")

        self.insert_cursor.setCharFormat(self.llm_title_format)
        self.insert_cursor.insertText(f"\nAI ({llm_model_name}):\n")
        self.insert_cursor.setCharFormat(self.original_format)

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def add_llm_message(self, llm_msg_payload: dict):
        if self.__is_think == False and llm_msg_payload.get('is_think') == True:
            self.__is_think = True
            self.insert_cursor.setCharFormat(self.llm_think_format)
        if self.__is_think == True and llm_msg_payload.get('is_think') == False:
            self.insert_cursor.setCharFormat(self.original_format)
            self.__is_think = False

        message = llm_msg_payload.get('content')
        self.insert_cursor.insertText(message)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def reload_chat_message_list(self, message_list):
        self.clear()
        for msg in message_list:
            role = msg.get('role')
            if role == 'user':
                org_user_msg = msg.get('org_user_msg')
                self.insert_cursor.setCharFormat(self.user_title_format)
                self.insert_cursor.insertText("You:\n")
                self.insert_cursor.setCharFormat(self.original_format)
                self.insert_cursor.insertText(org_user_msg + "\n")
                continue

            if role == 'assistant':
                assistant_msg = msg.get('content')
                self.insert_cursor.setCharFormat(self.llm_title_format)
                self.insert_cursor.insertText(f"\nAI:\n")
                self.insert_cursor.setCharFormat(self.original_format)
                g = THINK_RE.match(assistant_msg)
                if not g:
                    continue
                think_text = g.group(1)
                content_text = g.group(2)
                if think_text:
                    self.insert_cursor.setCharFormat(self.llm_think_format)
                    self.insert_cursor.insertText(think_text)
                self.insert_cursor.setCharFormat(self.original_format)
                self.insert_cursor.insertText(content_text)
                continue

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
