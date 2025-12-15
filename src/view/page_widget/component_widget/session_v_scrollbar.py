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
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QScrollBar


class SessionVScrollbar(QScrollBar):
    SESSION_START_LINE_NUM = Signal(int)

    def __init__(self):
        super(SessionVScrollbar, self).__init__(Qt.Orientation.Vertical)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            """
            QScrollBar:vertical {
                border: none;
                background: white;
                width: 3px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #3B85D5;
                min-height: 100px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
                border: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            """
        )

    def update_scrollbar(self, total_lines: int, visible_lines: int, first_visible_line: int, hide_scrollbar: bool):
        if hide_scrollbar:
            self.hide()
            return

        self.show()
        if total_lines <= 0 or visible_lines <= 0:
            self.setEnabled(False)
            return

        self.setEnabled(True)
        max_val = max(total_lines - visible_lines + 1, 1)
        self.setRange(1, max_val)

        self.setValue(first_visible_line)
        self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        self.SESSION_START_LINE_NUM.emit(self.value())
        super().mouseMoveEvent(event)
