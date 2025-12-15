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


from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QLabel, QPushButton


class LoginLineEdit(QLineEdit):
    def __init__(self, is_password=False):
        super(LoginLineEdit, self).__init__()
        self.setFixedWidth(220)
        self.setStyleSheet("""
            QLineEdit{
                border: none;
                height: 30px;
                border-radius: 15px;
                background-color: #EAEAEA;
                font-family: Arial;
                font-size: 15px;
                padding-left: 10px;
                }""")
        if is_password:
            self.setEchoMode(QLineEdit.EchoMode.Password)

        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

class LoginLabel(QLabel):
    def __init__(self, text):
        super(LoginLabel, self).__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

class LoginButton(QPushButton):
    def __init__(self, text):
        super(LoginButton, self).__init__(text)
        self.setStyleSheet("""
            QPushButton{
                color: #105315;
                background: #B0F173;
                border: none;
                width: 60px;
                height: 30px;
                border-radius: 15px;
                }
            QPushButton:hover{
                background: #96E858;
            }""")