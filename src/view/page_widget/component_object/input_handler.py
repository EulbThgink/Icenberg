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
from PySide6.QtGui import QKeyEvent

from src.common.common_definition import OS_TYPE


class InputHandler:
    ENTER = '\n'
    BACKSPACE = '\x7f'
    ESCAPE = '\x1b'
    TAB = '\t'
    UP = '\x1b[A'
    DOWN = '\x1b[B'
    LEFT = '\x1b[D'
    RIGHT = '\x1b[C'

    def __init__(self):
        self.CTRL_MODIFIER = Qt.KeyboardModifier.ControlModifier \
            if OS_TYPE != 'darwin' else Qt.KeyboardModifier.MetaModifier

    def handle_key_event(self, event: QKeyEvent) -> str | None:
        key = event.key()
        modifiers = event.modifiers()

        if modifiers == self.CTRL_MODIFIER and Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            return chr(key - Qt.Key.Key_A + 1)

        if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
            return InputHandler.ENTER

        if key == Qt.Key.Key_Backspace:
            return InputHandler.BACKSPACE

        if key == Qt.Key.Key_Tab:
            return InputHandler.TAB

        if key == Qt.Key.Key_Escape:
            return InputHandler.ESCAPE

        # 上下键就是\x1b[A, \x1b[B, 之前有\x10 和 \x0e的处理是因为vt100在不同的linux版本上不兼容导致的，现在改为xterm问题解决
        if key == Qt.Key.Key_Up:
            return InputHandler.UP

        if key == Qt.Key.Key_Down:
            return InputHandler.DOWN

        if key == Qt.Key.Key_Left:
            return InputHandler.LEFT

        if key == Qt.Key.Key_Right:
            return InputHandler.RIGHT

        event_text = event.text()
        if event_text and not (modifiers & ~Qt.KeyboardModifier.ShiftModifier):
            return event_text

        return None
