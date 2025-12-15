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


from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.view.page_widget.component_widget.llm_chat_buttom_widget import LlmChatBottomWidget
from src.view.page_widget.component_widget.llm_chat_main_widget import LlmChatMainWidget
from src.view.page_widget.component_widget.llm_chat_top_widget import LlmChatTopWidget


class LlmChat(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Layout for the chat widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)

        # top widget
        self.top_widget = LlmChatTopWidget()

        # main widget
        self.main_widget = LlmChatMainWidget()

        # button widget
        self.buttom_widget = LlmChatBottomWidget()

        main_layout.addWidget(self.top_widget)
        main_layout.addWidget(self.main_widget, stretch=1)
        main_layout.addWidget(self.buttom_widget)
        self.setLayout(main_layout)

    def update_model_list(self, llm_models: list):
        # print('llm models: ', llm_models)
        self.buttom_widget.pill_llm_widget.combo.clear()
        self.buttom_widget.pill_llm_widget.combo.addItems(
            [x['name'] for x in llm_models] if llm_models else ["No LLM Model"])

    def add_ai_message(self, llm_msg_payload: dict):
        self.main_widget.add_llm_message(llm_msg_payload)
        if llm_msg_payload.get('is_done', True):
            self.buttom_widget.pill_llm_widget.send_btn.setEnabled(True)

    def clear_chat_widget(self):
        self.main_widget.clear()
        self.buttom_widget.input_line.clear()

    def list_chat_history(self, chat_history: list):
        self.top_widget.show_chat_history(chat_history)

    def load_chat(self, payload: dict):
        content = payload.get('content', {})
        message_list = content.get('message_list')
        self.main_widget.reload_chat_message_list(message_list)
