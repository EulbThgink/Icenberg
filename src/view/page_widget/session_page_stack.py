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


from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QStackedWidget

from src.common.msg_code import LOGIN_CODE
from src.view.page_widget.login_page import LoginPage
from src.view.page_widget.session_page import SessionPage


class SessionPageStack(QStackedWidget):
    SIG_COMMAND = Signal(dict)

    def __init__(self, session_id: str):
        super(SessionPageStack, self).__init__()
        self.session_id = session_id
        self.login_page = LoginPage()
        self.session_page = SessionPage(self.session_id)
        self.addWidget(self.login_page)
        self.addWidget(self.session_page)
        self.setCurrentWidget(self.login_page)

        self.login_page.login_btn.clicked.connect(self.on_login)
        self.login_page.password_input.returnPressed.connect(self.on_login)
        self.session_page.SIG_SESSION_PAGE.connect(self.SIG_COMMAND, type=Qt.ConnectionType.DirectConnection)

    def on_login(self):
        self.login_page.loading_label.show()
        self.login_page.loading_timer.start()
        login_params = self.login_page.get_input_params()

        self.login_page.ip_input.clear()
        self.login_page.port_input.clear()
        self.login_page.user_input.clear()
        self.login_page.password_input.clear()
        self.login_page.ip_input.setFocus()

        self.login_page.login_btn.setEnabled(False)
        self.session_page.calc_line_count()
        login_params['page_line_count'] = self.session_page.calc_line_count()
        self.SIG_COMMAND.emit(
            {
                'msg_code': LOGIN_CODE,
                'payload': {
                    'session_id': self.session_id,
                    'content': login_params
                }
            }
        )

    def set_focus(self):
        if self.currentWidget() is not None:
            self.currentWidget().setFocus()

    def turn_2_session_page(self):
        self.setCurrentWidget(self.session_page)

    def update_text_browser(self, content: dict):
        if self.session_page is None:
            return

        if (current_widget := self.currentWidget()) and isinstance(current_widget, SessionPage):
            current_widget.update_page(content)

    def update_session_llm_widget(self, msg_code, content: dict):
        if self.session_page is None:
            return

        if (current_widget := self.currentWidget()) and isinstance(current_widget, SessionPage):
            current_widget.update_llm_widget(msg_code, content)
