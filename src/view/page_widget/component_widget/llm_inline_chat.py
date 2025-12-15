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


import uuid
from typing import Optional

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PySide6.QtWidgets import QWidget, QToolButton, QHBoxLayout, QSizePolicy, QLineEdit, QTextBrowser, QVBoxLayout, \
    QComboBox, QFrame, QListView


class PillLlmInput(QFrame):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.setObjectName("PillLlmInput")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.input = QLineEdit(self)
        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.setFrame(False)
        self.combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.combo.setView(QListView())

        if items:
            self.combo.addItems(items)

        self.send_btn = QToolButton(self)
        self.send_btn.setText("▶")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setObjectName("GoButton")

        self.send_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 4, 4, 4)
        lay.addWidget(self.input, 1)
        lay.addWidget(self.combo, 0)
        lay.addWidget(self.send_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet("""
        /* 胶囊容器 */
        #PillLlmInput {
            border: 1px solid #B5C7FF;
            border-radius: 8px;
            background: #FFFFFF;
        }
        #PillLlmInput:hover {
            border-color: #8EA6FF;
        }
        #PillLlmInput:focus-within { /* 子控件获得焦点时高亮 */
            border: 2px solid #5B8CFF;
            background: #F2F6FF;
        }

        QLineEdit {
            border: none;
            padding: 5px;
            background: transparent;
            font-size: 14px;
        }
        /* 下拉框本体去掉自带边框/背景，保持胶囊统一外观 */
        QComboBox {
            border: none;
            border-left: 1px solid #D0D0D0;
            padding: 5px;
            background: transparent;
            font-size: 14px;
        }
        QListView {
            border: none;
            background: transparent;
            font-size: 14px;
        }
        #GoButton {
            border: none;
            color: rgba(19,185,13,1);
            background: transparent;
            font-size: 14px;
        }
        #GoButton:hover {
            background: rgba(19,185,13,0.06);
            border-radius: 6px;
        }
        #GoButton:disabled {
            color: #AAAAAA;
            background: transparent;
        }""")


class LlmInlineChat(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.input_edit = PillLlmInput(items=[], parent=self)
        self.dialog_show = QTextBrowser(parent=self)

        self.dialog_show.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.dialog_show.horizontalScrollBar().hide()

        self.original_format = self.dialog_show.currentCharFormat()
        self.user_title_format = QTextCharFormat()
        self.user_title_format.setFontWeight(QFont.Weight.Bold)
        self.user_title_format.setForeground(QColor("#3f7BF1"))

        self.llm_title_format = QTextCharFormat()
        self.llm_title_format.setFontWeight(QFont.Weight.Bold)
        self.llm_title_format.setForeground(QColor("#7821A3"))

        self.llm_think_format = QTextCharFormat()
        self.llm_think_format.setForeground(QColor("#7f7f7f"))

        self.insert_cursor = QTextCursor(self.dialog_show.document())
        self.insert_cursor.movePosition(QTextCursor.MoveOperation.End)

        # Target width: SessionTextWindow clamps position by this width
        self.input_edit.setFixedWidth(700)
        self.dialog_show.setFixedWidth(700)

        self.close_btn = QToolButton(self)
        self.close_btn.setText("✕")
        self.close_btn.setObjectName("closeBtn")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.on_close_clicked)

        up_layout = QHBoxLayout()
        up_layout.setSpacing(6)
        up_layout.addWidget(self.input_edit, 1)
        up_layout.addWidget(self.close_btn, 0)

        main_layout = QVBoxLayout()
        main_layout.addLayout(up_layout)
        main_layout.addWidget(self.dialog_show, 1)
        self.setLayout(main_layout)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.input_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.setStyleSheet(
            """
            LlmInlineChat {
                background: rgba(255,255,255,230);
                border: 1px solid #eeeeee;
                border-radius: 8px;
            }
            LlmInlineChat QLineEdit {
                background: #FFFFFF;
                color: #222222;
                border: 1px solid #3B85D5;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            LlmInlineChat QToolButton {
                background: rgba(0,0,0,0);
                color: #0969DA;
                border: none;
                border-radius: 6px;
                padding: 3px 3px;
                font-size: 13px;
            }
            LlmInlineChat QToolButton:hover {
                background: rgba(9,105,218,0.10);
            }
            LlmInlineChat QToolButton#closeBtn {
                color: #D1242F;
            }
            LlmInlineChat QToolButton#closeBtn:hover {
                background: rgba(209,36,47,0.10);
            }
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
            """
        )

        self._dragging = False
        self._drag_offset_global = QPoint(0, 0)

        self.set_children_visible(False)
        self.hide()
        self.inline_chat_uuid = None
        self.is_first_question_asked = False

        self.__is_think = False

    def input_text(self) -> str:
        return self.input_edit.input.text()

    def current_model_name(self) -> str:
        return self.input_edit.combo.currentText()

    def input_clear(self):
        self.input_edit.input.clear()

    def show(self):
        self.set_children_visible(True)
        self.inline_chat_uuid = str(uuid.uuid4())
        super().show()

    def hide(self):
        self.set_children_visible(False)
        super().hide()

    def setFocus(self):
        super().setFocus()
        self.input_edit.setFocus()

    def insert_user_msg(self, message: str):
        self.insert_cursor.setCharFormat(self.user_title_format)
        self.insert_cursor.insertText("You:\n")
        self.insert_cursor.setCharFormat(self.original_format)
        self.insert_cursor.insertText(message + "\n")

        self.insert_cursor.setCharFormat(self.llm_title_format)
        self.insert_cursor.insertText(f"\nAI ({self.current_model_name()}):\n")
        self.insert_cursor.setCharFormat(self.original_format)

        self.dialog_show.verticalScrollBar().setValue(self.dialog_show.verticalScrollBar().maximum())

    def insert_llm_msg(self, llm_msg_payload: dict):
        if self.__is_think == False and llm_msg_payload.get('is_think') == True:
            self.__is_think = True
            self.insert_cursor.setCharFormat(self.llm_think_format)
        if self.__is_think == True and llm_msg_payload.get('is_think') == False:
            self.insert_cursor.setCharFormat(self.original_format)
            self.__is_think = False

        message = llm_msg_payload.get('content')

        self.insert_cursor.insertText(message)
        if llm_msg_payload.get('is_done', True):
            self.input_edit.send_btn.setEnabled(True)
        self.dialog_show.verticalScrollBar().setValue(self.dialog_show.verticalScrollBar().maximum())

    def is_blank_area(self, pos: QPoint) -> bool:
        return self.childAt(pos) is None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_blank_area(event.pos()):
            self._dragging = True
            self._drag_offset_global = event.globalPosition().toPoint() - self.mapToGlobal(QPoint(0, 0))
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            target_top_left_global = event.globalPosition().toPoint() - self._drag_offset_global
            parent = self.parentWidget()
            if parent:
                target = parent.mapFromGlobal(target_top_left_global)
                max_x = max(0, parent.width() - self.width())
                max_y = max(0, parent.height() - self.height())
                target.setX(min(max(target.x(), 0), max_x))
                target.setY(min(max(target.y(), 0), max_y))
                self.move(target)
            else:
                self.move(target_top_left_global)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_children_visible(self, visible: bool):
        self.input_edit.setVisible(visible)
        self.dialog_show.setVisible(visible)
        self.close_btn.setVisible(visible)

    def on_close_clicked(self):
        self.input_clear()
        self.dialog_show.clear()
        self.is_first_question_asked = False
        self.hide()

    def update_llm_inline_model_list(self, llm_models: list):
        self.input_edit.combo.clear()
        self.input_edit.combo.addItems([x['name'] for x in llm_models] if llm_models else ["None"])
