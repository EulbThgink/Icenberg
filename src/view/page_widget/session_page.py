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


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSplitter

from src.common.common_definition import INLINE_CHAT_ID, OS_TYPE, get_session_widget_height, SIDE_CHAT_ID
from src.common.msg_code import LLM_ANSWER_CODE, LLM_MODEL_LIST_CODE, LLM_CHAT_HISTORY_RSP_CODE, \
    USER_COMMAND_CODE, SCROLL_WINDOW_CODE, LLM_ASK_CODE, LLM_CHAT_HISTORY_REQ_CODE, LLM_MODEL_CHECK, \
    LLM_INLINE_MODEL_LIST_CODE, LLM_LOAD_CHAT_BY_HISTORY_IDX, LLM_RSP_CHAT_BY_CHAT_ID, LLM_NEW_CHAT_CODE
from src.view.page_widget.component_widget.llm_chat import LlmChat
from src.view.page_widget.component_widget.session_browser import SessionBrowser


class SessionPage(QWidget):
    SIG_SESSION_PAGE = Signal(dict)

    CTRL_MODIFIER = Qt.KeyboardModifier.ControlModifier if OS_TYPE != 'darwin' else Qt.KeyboardModifier.MetaModifier

    def __init__(self, session_id: str):
        super(SessionPage, self).__init__()
        self.__session_id = session_id
        self.setStyleSheet("""
            background-color: white;
        """)

        page_layout = QHBoxLayout()
        page_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(page_layout)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        page_layout.addWidget(self.splitter)

        self.text_browser = SessionBrowser()
        self.splitter.addWidget(self.text_browser)

        self.llm_chat_widget = LlmChat()
        self.llm_chat_widget.setVisible(False)
        self.llm_chat_widget.setMaximumWidth(500)
        self.splitter.addWidget(self.llm_chat_widget)

        self.splitter.setStretchFactor(0, 9)
        self.splitter.setStretchFactor(1, 3)

        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: lightgray;
                width: 2px;
            }
        """)

        self.text_browser.session_text_window.SIG_SESSION_TEXT_BROWSER_COMMAND.connect(self.emit_session_command)
        self.text_browser.session_text_window.SIG_LLM_INLINE.connect(self.llm_inline_chat)
        self.text_browser.session_text_window.SIG_WINDOW_SCROLL.connect(self.emit_session_scroll)
        self.text_browser.v_scrollbar.SESSION_START_LINE_NUM.connect(self.emit_value_changed)
        self.llm_chat_widget.top_widget.history_chat_button.clicked.connect(self.emit_llm_chat_history_req)
        self.llm_chat_widget.top_widget.new_chat_button.clicked.connect(self.emit_llm_new_chat_req)
        self.llm_chat_widget.top_widget.history_menu.triggered.connect(self.emit_llm_load_chat_by_chat_id)
        self.llm_chat_widget.buttom_widget.pill_llm_widget.send_btn.clicked.connect(self.emit_user_question)

    def calc_line_count(self) -> int:
        view_height = get_session_widget_height()
        # print(f'calc_line_count view_height: {view_height}')

        max_lines = 200

        low, high = 1, max_lines
        line_count = 0

        while low <= high:
            mid = (low + high) // 2
            doc_height = self.text_browser.session_text_window.get_test_lines_height(mid)

            if doc_height <= view_height:
                line_count = mid
                low = mid + 1
            else:
                high = mid - 1

        self.text_browser.session_text_window.clear()
        return line_count

    def llm_inline_chat(self, req: dict):
        payload = req.get('payload', {})
        payload['session_id'] = self.__session_id
        self.SIG_SESSION_PAGE.emit(req)

    def emit_user_question(self):
        question = self.llm_chat_widget.buttom_widget.input_line.toPlainText().strip()
        self.llm_chat_widget.buttom_widget.input_line.clear()

        if not question:
            return

        self.llm_chat_widget.buttom_widget.pill_llm_widget.send_btn.setEnabled(False)
        current_llm_model = self.llm_chat_widget.buttom_widget.get_current_model_name()
        shell_content = ''
        if self.llm_chat_widget.buttom_widget.pill_llm_widget.enable_check.isChecked():
            if self.text_browser.session_text_window.llm_shell_content_time_mark != \
                    self.text_browser.session_text_window.update_datetime:
                self.text_browser.session_text_window.llm_shell_content_time_mark = \
                    self.text_browser.session_text_window.update_datetime
                shell_content = self.text_browser.session_text_window.toPlainText()

        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': LLM_ASK_CODE,
                'payload': {
                    'session_id': self.__session_id,
                    'content': {
                        'chat_session_id': SIDE_CHAT_ID,
                        'llm_ask': question,
                        'llm_model_name': current_llm_model,
                        'shell_content_text': shell_content,
                    }
                }
            }
        )
        self.llm_chat_widget.main_widget.paint_user_message(question, current_llm_model)

    def emit_session_command(self, command: str):
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': USER_COMMAND_CODE,
                'payload': {
                    'session_id': self.__session_id,
                    'content': {'command': command}
                }
            }
        )

    def emit_session_scroll(self, scroll_info: dict):
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': SCROLL_WINDOW_CODE,
                'payload': {
                    'session_id': self.__session_id,
                    'content': scroll_info
                }
            }
        )

    def emit_value_changed(self, value: int):
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': SCROLL_WINDOW_CODE,
                'payload': {
                    'session_id': self.__session_id,
                    'content': {
                        'start_line_num': value
                    }
                }
            }
        )

    def emit_llm_chat_history_req(self):
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': LLM_CHAT_HISTORY_REQ_CODE,
                'payload': {
                    'session_id': self.__session_id,
                }
            }
        )

    def emit_llm_new_chat_req(self):
        self.llm_chat_widget.clear_chat_widget()
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': LLM_NEW_CHAT_CODE,
                'payload': {
                    'session_id': self.__session_id,
                }
            }
        )

    def emit_llm_load_chat_by_chat_id(self, action: QAction):
        history_idx = action.data()
        # print('history_idx', history_idx)
        self.SIG_SESSION_PAGE.emit(
            {
                'msg_code': LLM_LOAD_CHAT_BY_HISTORY_IDX,
                'payload': {
                    'session_id': self.__session_id,
                    'content': {'history_idx': history_idx}
                }
            }
        )

    def toggle_chat_widget(self):
        is_visible = self.llm_chat_widget.isVisible()
        self.llm_chat_widget.setVisible(not is_visible)

        if not is_visible:
            self.llm_chat_widget.setFocus()
            self.SIG_SESSION_PAGE.emit(
                {
                    'msg_code': LLM_MODEL_CHECK,
                    'payload': {
                        'session_id': self.__session_id,
                    }
                }
            )
        else:
            self.text_browser.session_text_window.setFocus()

    def update_page(self, update_view_area_msg: dict):
        if not update_view_area_msg:
            return

        self.__text_browser_update(update_view_area_msg)

    def update_llm_widget(self, msg_code, payload: dict):
        if not payload:
            return

        if msg_code == LLM_ANSWER_CODE:
            chat_session_id = payload.get('chat_session_id')
            if chat_session_id == INLINE_CHAT_ID:
                self.text_browser.session_text_window.inline_chat.insert_llm_msg(payload)
                return
            self.llm_chat_widget.add_ai_message(payload)
            return

        if msg_code == LLM_MODEL_LIST_CODE:
            self.llm_chat_widget.update_model_list(payload.get('content', {}).get('models', []))
            return

        if msg_code == LLM_CHAT_HISTORY_RSP_CODE:
            self.llm_chat_widget.list_chat_history(payload.get('content', []))
            return

        if msg_code == LLM_INLINE_MODEL_LIST_CODE:
            self.text_browser.session_text_window.inline_chat.update_llm_inline_model_list(
                payload.get('content', {}).get('models', [])
            )

        if msg_code == LLM_RSP_CHAT_BY_CHAT_ID:
            self.llm_chat_widget.load_chat(payload)

    def __text_browser_update(self, update_view_area_msg: dict):
        self.text_browser.session_text_window.update_window(update_view_area_msg.get('view_area', {}))
        self.text_browser.v_scrollbar.update_scrollbar(**update_view_area_msg.get('scroll_info', {}))

    def setFocus(self):
        super().setFocus()
        self.text_browser.session_text_window.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.text_browser.session_text_window.setFocus()
