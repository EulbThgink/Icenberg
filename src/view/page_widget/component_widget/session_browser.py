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


from PySide6.QtWidgets import QWidget, QHBoxLayout

from src.view.page_widget.component_widget.session_text_window import SessionTextWindow
from src.view.page_widget.component_widget.session_v_scrollbar import SessionVScrollbar


class SessionBrowser(QWidget):
    def __init__(self):
        super(SessionBrowser, self).__init__()
        self.session_text_window = SessionTextWindow()
        self.v_scrollbar = SessionVScrollbar()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.session_text_window)
        layout.addWidget(self.v_scrollbar)
        self.setLayout(layout)
