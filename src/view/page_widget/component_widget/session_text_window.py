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


from datetime import datetime

from PySide6.QtCore import Signal, QEvent, QTimer, Qt, QPoint
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QKeyEvent, QPainter, QTextCursor, QWheelEvent, QMouseEvent, \
    QGuiApplication, QCursor, QFontMetrics, QTextBlockFormat
from PySide6.QtWidgets import QTextBrowser, QToolButton

from src.common.common_definition import INLINE_CHAT_ID, get_shell_font_setting, OS_TYPE
from src.common.font_style import StyleTuple, FontStyle
from src.common.msg_code import LLM_INLINE_MODEL_CHECK, LLM_INLINE_ASK_CODE
from src.view.page_widget.component_object.input_handler import InputHandler
from src.view.page_widget.component_widget.llm_inline_chat import LlmInlineChat


class SessionTextWindow(QTextBrowser):
    SIG_SESSION_TEXT_BROWSER_COMMAND = Signal(str)
    SIG_LLM_INLINE = Signal(dict)
    SIG_WINDOW_SCROLL = Signal(dict)

    def __init__(self):
        super(SessionTextWindow, self).__init__()
        self.setStyleSheet("""
                    QTextBrowser {
                        background-color: white;
                        border: none;
                    }
                    QScrollBar:horizontal {
                        border: none;
                        background: white;
                        height: 3px;
                    }
                    QScrollBar::handle:horizontal {
                        background: #3B85D5;
                        min-width: 100px;
                    }
                    QScrollBar::handle:horizontal:hover {
                        background: #a0a0a0;
                    }
                    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                        border: none;
                        background: none;
                    }
                    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                        background: none;
                    }
                """)
        font_family, font_size = get_shell_font_setting()
        self.display_font = QFont(font_family, font_size)
        self.setFont(self.display_font)

        self.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.verticalScrollBar().hide()

        self.__view_cursor = (1, 1)  # (row, col)
        self.input_handler = InputHandler()
        self.clipboard_text_pasted = False
        self.insert_cursor = self.textCursor()

        fm = QFontMetrics(self.display_font)
        line_height_px = fm.lineSpacing()
        self.block_format = QTextBlockFormat()
        self.block_format.setLineHeight(line_height_px, QTextBlockFormat.LineHeightTypes.FixedHeight.value)

        self.cursor_flash = True
        self.cursor_flash_timer = QTimer(self)
        self.cursor_flash_timer.setInterval(600)
        self.cursor_flash_timer.timeout.connect(self.toggle_cursor_flashing)
        self.cursor_flash_timer.start()

        self._scroll_line_accum = 0.0
        self.setTabChangesFocus(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.float_btn = QToolButton(self.viewport())
        self.float_btn.setText("Q?")
        self.float_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.float_btn.setVisible(False)
        self.float_btn.setAutoRaise(True)
        self.float_btn.setStyleSheet(
            "QToolButton {"
            "  background-color: rgba(0,0,0,160);"
            "  color: white;"
            "  border: none;"
            "  border-radius: 6px;"
            "  padding: 0px 0px;"
            "  font-size: 15px;"
            "}"
            "QToolButton:hover {"
            "  background-color: rgba(0,0,0,200);"
            "}"
        )
        self.float_btn.clicked.connect(self.on_float_btn_clicked)
        self.inline_chat = LlmInlineChat(self.viewport())
        self.inline_chat.input_edit.send_btn.clicked.connect(self.inline_chat_query)
        self.update_datetime = None
        self.inline_shell_content_time_mark = None
        self.llm_shell_content_time_mark = None

    def show_input_edit_center(self):
        self.inline_chat.ensurePolished()
        self.inline_chat.show()

        hint = self.inline_chat.sizeHint()
        if hint.isValid():
            self.inline_chat.resize(hint)

        vp_rect = self.viewport().rect().adjusted(8, 8, -8, -8)
        size = self.inline_chat.size()
        tx = vp_rect.center().x() - size.width() // 2
        ty = vp_rect.center().y() - size.height() // 2
        x = max(vp_rect.left(), min(tx, vp_rect.right() - size.width()))
        y = max(vp_rect.top(), min(ty, vp_rect.bottom() - size.height()))
        self.inline_chat.move(int(x), int(y))
        self.inline_chat.raise_()
        self.inline_chat.setFocus()

    def on_float_btn_clicked(self):
        self.float_btn.hide()

        QGuiApplication.clipboard().clear()
        self.show_input_edit_center()
        self.SIG_LLM_INLINE.emit(
            {
                'msg_code': LLM_INLINE_MODEL_CHECK,
                'payload': {}
            }
        )

    def inline_chat_query(self):
        inline_ask_text = self.inline_chat.input_text()
        self.inline_chat.input_clear()
        self.inline_chat.insert_user_msg(inline_ask_text)

        if self.inline_shell_content_time_mark != self.update_datetime:
            self.inline_shell_content_time_mark = self.update_datetime
            shell_content = self.toPlainText()
        else:
            shell_content = ''

        if self.inline_chat.is_first_question_asked:
            shell_focus_text = ''
        else:
            shell_focus_text = self.textCursor().selectedText()

        self.SIG_LLM_INLINE.emit(
            {
                'msg_code': LLM_INLINE_ASK_CODE,
                'payload': {
                    'content': {
                        'chat_session_id': INLINE_CHAT_ID,
                        'llm_model_name': self.inline_chat.current_model_name(),
                        'shell_content_text': shell_content,
                        'shell_focus_text': shell_focus_text or None,
                        'inline_ask': inline_ask_text
                    }
                }
            }
        )
        self.inline_chat.is_first_question_asked = True
        self.inline_chat.input_edit.send_btn.setEnabled(False)

    def focusNextPrevChild(self, next, /):
        return False

    def wheelEvent(self, event: QWheelEvent):
        dy_px = event.pixelDelta().y()
        delta_lines = 0

        if dy_px:
            line_px = max(1, self.fontMetrics().lineSpacing())
            self._scroll_line_accum += (dy_px / line_px) * 0.2
            whole = int(self._scroll_line_accum)
            if whole != 0:
                delta_lines = whole * 3
                self._scroll_line_accum -= whole
        else:
            steps = event.angleDelta().y()

            if OS_TYPE == 'darwin':
                delta_lines = int(3 * steps)
            else:
                delta_lines = int(0.06 * steps)

        if delta_lines != 0:
            self.SIG_WINDOW_SCROLL.emit({'move': delta_lines if OS_TYPE == 'darwin' else -delta_lines})
            event.accept()
            return

        super().wheelEvent(event)

    def toggle_cursor_flashing(self):
        if self.isVisible() and self.hasFocus():
            self.cursor_flash = not self.cursor_flash
        else:
            self.cursor_flash = False
        self.viewport().update()

    def update_window(self, update_view_area_msg: dict):
        self.update_datetime = datetime.now()
        self.viewport().setUpdatesEnabled(False)

        self.update_view(update_view_area_msg)

        self.cursor_flash = True
        self.viewport().setUpdatesEnabled(True)
        self.viewport().update()

    def viewportEvent(self, event):
        if event.type() == QEvent.Type.Paint:
            ok = super().viewportEvent(event)
            self.paint_cursor()
            return ok
        return super().viewportEvent(event)

    def update_view(self, update_view_area_msg: dict):
        self.clear()
        self.insert_cursor.setBlockFormat(self.block_format)

        view_area_content = update_view_area_msg.get('view_area_content', [])
        last_idx = len(view_area_content) - 1
        for idx, line in enumerate(view_area_content):
            self.paint_line(line, is_last_line=(idx == last_idx))
        self.__view_cursor = update_view_area_msg.get('cursor_pos', (1, 1))

    def get_test_lines_height(self, line_count: int):
        self.clear()
        self.insert_cursor.setBlockFormat(self.block_format)

        for i in range(line_count):
            line = [{'text': f'Test line {i + 1}', 'style': None}]
            self.paint_line(line, is_last_line=(i == line_count - 1))
        return self.document().documentLayout().documentSize().height()

    def paint_line(self, line: list, is_last_line: bool = False):
        for segment in line:
            style: StyleTuple | None = segment.get('style')
            text = segment.get('text', '')

            qformat = QTextCharFormat()
            qformat.setForeground(QColor(FontStyle.DEFAULT_FOREGROUND_COLOR))
            qformat.setBackground(QColor(FontStyle.DEFAULT_BACKGROUND_COLOR))

            if style:
                qformat.setForeground(QColor(style.foreground_color))
                qformat.setBackground(QColor(style.background_color))
                if style.bold:
                    qformat.setFontWeight(QFont.Weight.Bold)
                if style.italic:
                    qformat.setFontItalic(True)
                if style.opacity != 1.0:
                    color = qformat.foreground().color()
                    color.setAlpha(128)
                    qformat.setForeground(color)
                if style.visible is False:
                    color = qformat.foreground().color()
                    color.setAlpha(0)
                    qformat.setForeground(color)

            self.insert_cursor.setCharFormat(qformat)
            self.insert_cursor.insertText(text)

        if is_last_line:
            return

        self.insert_cursor.insertBlock()

    def paint_cursor(self):
        if not self.__view_cursor:
            return

        if not self.cursor_flash:
            rect_color = QColor("#A6D0FF")
            text_color = QColor("black")
        else:
            rect_color = QColor("#5893D3")
            text_color = QColor("white")

        row, col = self.__view_cursor
        cursor = self.cursor_at_row_col(row, col)
        cursor_rect = self.cursorRect(cursor)

        painter = QPainter(self.viewport())
        cursor2 = QTextCursor(cursor)
        cursor2.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 1)
        char_at_cursor = cursor2.selectedText()

        painter.fillRect(
            cursor_rect.x(),
            cursor_rect.y(),
            self.fontMetrics().averageCharWidth(),
            cursor_rect.height(),
            rect_color
        )

        if char_at_cursor:
            painter.setPen(text_color)
            painter.setFont(self.font())
            painter.drawText(
                cursor_rect.x(),
                cursor_rect.y() + self.fontMetrics().ascent(),
                char_at_cursor
            )

    def cursor_at_row_col(self, row: int, col: int) -> QTextCursor:
        temp_cursor = QTextCursor(self.document())
        temp_cursor.movePosition(QTextCursor.MoveOperation.Start)
        temp_cursor.movePosition(QTextCursor.MoveOperation.NextBlock, n=row - 1)
        temp_cursor.movePosition(QTextCursor.MoveOperation.Right, n=col - 1)
        return temp_cursor

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus()

        if not self.cursor_flash_timer.isActive():
            self.cursor_flash_timer.start()
        self.cursor_flash = True

    def set_latin_input_hints(self):
        hints = Qt.InputMethodHint.ImhNoPredictiveText
        if hasattr(Qt.InputMethodHint, "ImhLatinOnly"):
            hints |= Qt.InputMethodHint.ImhLatinOnly
        self.setInputMethodHints(hints)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.cursor_flash = True
        if not self.cursor_flash_timer.isActive():
            self.cursor_flash_timer.start()

        self.set_latin_input_hints()
        QGuiApplication.inputMethod().reset()

        self.viewport().update()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)

        self.cursor_flash_timer.stop()
        self.cursor_flash = False
        self.viewport().update()

    def keyPressEvent(self, event: QKeyEvent):
        if emit_key := self.input_handler.handle_key_event(event):
            self.SIG_SESSION_TEXT_BROWSER_COMMAND.emit(emit_key)

        self.cursor_flash = True

        if not self.cursor_flash_timer.isActive():
            self.cursor_flash_timer.start()
        self.viewport().update()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.float_btn.setVisible(False)
            event.accept()
            return

        if event.button() == Qt.MouseButton.RightButton:
            clipboard = QGuiApplication.clipboard()
            if text := clipboard.text():
                self.SIG_SESSION_TEXT_BROWSER_COMMAND.emit(text)
                self.clipboard_text_pasted = True
                clipboard.clear()
            event.accept()

    def show_floating_btn_near_mouse(self):
        global_pos = QCursor.pos()
        vp_pos = self.viewport().mapFromGlobal(global_pos)

        pos = vp_pos + QPoint(10, 14)

        self.float_btn.adjustSize()
        btn_size = self.float_btn.size()
        vp_rect = self.viewport().rect()

        x = max(vp_rect.left(), min(pos.x(), vp_rect.right() - btn_size.width()))
        y = max(vp_rect.top(), min(pos.y(), vp_rect.bottom() - btn_size.height()))
        self.float_btn.move(QPoint(x, y))

        self.float_btn.setVisible(True)
        self.float_btn.raise_()

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not self.inline_chat.isVisible():
            if text := self.textCursor().selectedText():
                self.show_floating_btn_near_mouse()

                text = text.replace('\u2029', '\n')
                QGuiApplication.clipboard().setText(text)

    def contextMenuEvent(self, event):
        event.accept()
