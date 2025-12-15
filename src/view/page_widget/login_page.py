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


from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QGuiApplication
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget, QGridLayout

from src.view.page_widget.component_widget.login_page_widget import LoginLineEdit, LoginLabel, LoginButton


class LogoLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel{
                margin-top: 60px;
                margin-bottom: 40px;
            }""")
        img_path = Path(__file__).parent / "icenberg.png"
        self._logo_pixmap = QPixmap(str(img_path)) if img_path.is_file() else QPixmap()

        screen = QGuiApplication.primaryScreen()
        screen_geo = screen.geometry()
        screen_height = screen_geo.height()

        scaled = self._logo_pixmap.scaledToHeight(int(screen_height * 0.15), Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)


class LoginPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), Qt.GlobalColor.white)
        self.setPalette(palette)

        page_layout = QVBoxLayout(self)

        self.logo_label = LogoLabel()
        page_layout.addWidget(self.logo_label)

        form_layout = QGridLayout()
        form_container = QWidget()
        form_container.setLayout(form_layout)

        self.ip_label = LoginLabel("IP:")
        self.ip_input = LoginLineEdit()
        form_layout.addWidget(self.ip_label, 0, 0)
        form_layout.addWidget(self.ip_input, 0, 1)

        self.port_label = LoginLabel("Port:")
        self.port_input = LoginLineEdit()
        self.port_input.setPlaceholderText("22")
        form_layout.addWidget(self.port_label, 1, 0)
        form_layout.addWidget(self.port_input, 1, 1)

        self.user_label = LoginLabel("User:")
        self.user_input = LoginLineEdit()
        form_layout.addWidget(self.user_label, 2, 0)
        form_layout.addWidget(self.user_input, 2, 1)

        self.password_label = LoginLabel("Password:")
        self.password_input = LoginLineEdit(is_password=True)
        form_layout.addWidget(self.password_label, 3, 0)
        form_layout.addWidget(self.password_input, 3, 1)

        self.login_btn = LoginButton("Login")
        form_layout.addWidget(self.login_btn, 4, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.loading_label = QLabel("")
        self.loading_label.setStyleSheet("color: #3B85D5; font-size: 18px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.loading_label.hide()

        self.dot_count = 0
        self.loading_timer = QTimer(self)
        self.loading_timer.setInterval(150)
        self.loading_timer.timeout.connect(self.on_loading_timeout)
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        form_layout.addWidget(self.loading_label, 5, 1, 1, 2)

        page_layout.addWidget(form_container, 0, Qt.AlignmentFlag.AlignCenter)
        page_layout.addStretch()

    def setFocus(self):
        super().setFocus()
        self.ip_input.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.ip_input.setFocus()

    def get_input_params(self) -> dict:
        return {
            "hostname": self.ip_input.text(),
            "port": self.port_input.text(),
            "username": self.user_input.text(),
            "password": self.password_input.text()
        }

    def reset_login_state(self):
        self.ip_input.clear()
        self.port_input.clear()
        self.user_input.clear()
        self.password_input.clear()
        self.ip_input.setFocus()

        self.loading_timer.stop()
        self.loading_label.hide()
        self.login_btn.setEnabled(True)

    def on_loading_timeout(self):
        test = self.spinner_frames[self.dot_count % len(self.spinner_frames)]
        self.loading_label.setText(test)
        self.dot_count += 1
