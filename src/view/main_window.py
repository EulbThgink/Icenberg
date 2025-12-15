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


from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication

from src.common.msg_code import LOGIN_RSP_CODE, LLM_ANSWER_CODE, LLM_MODEL_LIST_CODE, \
    SESSION_VIEW_CONTENT_CODE, LLM_CHAT_HISTORY_RSP_CODE, LLM_INLINE_MODEL_LIST_CODE, LLM_RSP_CHAT_BY_CHAT_ID
from src.view.tab_wdget.session_tab_widget import SessionTabWidget


class MainWindow(QMainWindow):
    SIG_2_BACKEND = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('MainWindow')
        self.setWindowState(Qt.WindowState.WindowMaximized)

        self.tab_widget = SessionTabWidget(self.SIG_2_BACKEND)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.addWidget(self.tab_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        QApplication.processEvents()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

        QTimer.singleShot(2000, self.tab_widget.init_session_widget_height)

    def update_view(self, msg: dict):
        msg_code = msg.get('msg_code')
        msg_payload = msg.get('payload')

        if msg_code == LOGIN_RSP_CODE:
            self.tab_widget.handle_login_rsp_msg(msg_payload)
            return

        self.setUpdatesEnabled(False)
        if msg_code == SESSION_VIEW_CONTENT_CODE:
            self.tab_widget.update_session_text_browser(msg_payload)

        if msg_code in [LLM_ANSWER_CODE, LLM_MODEL_LIST_CODE, LLM_CHAT_HISTORY_RSP_CODE,
                        LLM_INLINE_MODEL_LIST_CODE, LLM_RSP_CHAT_BY_CHAT_ID]:
            self.tab_widget.update_session_llm_chat_widget(msg_code, msg_payload)

        self.setUpdatesEnabled(True)
