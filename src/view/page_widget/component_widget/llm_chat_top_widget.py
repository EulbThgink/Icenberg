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


from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QMenu

from src.view.page_widget.component_object.svg_icon import get_icon_from_svg


class LlmChatTopWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("llmChatTopWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
        #llmChatTopWidget{
            border-bottom: 1px solid #F0F0F0;
            background: transparent;
            padding: 5px 10px;
        }
        """)
        self.main_layout = QHBoxLayout()
        self.chat_label = QLabel('Chat:')
        self.chat_label.setStyleSheet("font-size: 13px; color: #3f3f3f;")
        self.chat_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        history_svg = '''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <!-- 外部深灰色圆圈 -->
            <circle cx="12" cy="12" r="10" fill="none" stroke="#4CAF50" stroke-width="1"/>
            
            <!-- 时针指向5点 (150度角) - 改细 -->
            <line x1="12" y1="12" x2="15.4" y2="16" stroke="#4CAF50" stroke-width="1" stroke-linecap="round"/>
            
            <!-- 分针指向12点 (0度角) - 改细 -->
            <line x1="12" y1="12" x2="12" y2="7" stroke="#4CAF50" stroke-width="1" stroke-linecap="round"/>
        </svg>'''
        self.history_chat_button = QPushButton()
        self.history_chat_button.setIcon(get_icon_from_svg(history_svg))
        self.history_chat_button.setIconSize(QSize(20, 20))
        self.history_chat_button.setFixedSize(20, 20)
        self.history_chat_button.setStyleSheet("""
            QPushButton{
                border: none;
                width: 20px;
                height: 20px;
                border-radius: 5px;
            }
            QPushButton:hover{
                background: #BDE8BF;
            }""")

        add_svg = '''<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
  <path d="M12 5v14M5 12h14"
        stroke="#4CAF50" stroke-width="1" stroke-linecap="round"/>
</svg>'''
        self.new_chat_button = QPushButton()
        self.new_chat_button.setIcon(get_icon_from_svg(add_svg))
        self.new_chat_button.setIconSize(QSize(20, 20))
        self.new_chat_button.setFixedSize(20, 20)
        self.new_chat_button.setStyleSheet("""
            QPushButton{
                border: none;
                width: 20px;
                height: 20px;
                border-radius: 5px;
            }
            QPushButton:hover{
                background: #BDE8BF;
            }""")

        self.main_layout.addWidget(self.chat_label, 0, Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.history_chat_button, 0, Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.addWidget(self.new_chat_button, 0, Qt.AlignmentFlag.AlignVCenter)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.setLayout(self.main_layout)
        self.setFixedHeight(25)

        self.history_menu = QMenu()
        self.history_menu.setObjectName("historyMenu")
        self.history_menu.setStyleSheet("""
                    QMenu { font-size: 13px; font-family: Arial; background: white; }
                    QMenu::item { font-size: 13px; padding: 5px 20px; }
                    QMenu::item:selected { font-size: 13px; background: #3B85D5; color: white; padding: 5px 20px; }
                """)

    def show_chat_history(self, chat_history: list):
        if not chat_history:
            return

        self.history_menu.clear()

        for item in chat_history:
            history_info_str = item.get('start_time', '') + ' - ' + item.get('first_message', '')[: 20]
            action = QAction(history_info_str, self.history_menu)
            action.setData(item.get('history_idx'))
            self.history_menu.addAction(action)

        btn = self.history_chat_button
        global_pos = btn.mapToGlobal(btn.rect().bottomLeft())
        self.history_menu.popup(global_pos)
        self.history_menu.show()
