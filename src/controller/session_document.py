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


import threading
from typing import List, Dict, Callable, Tuple, Final

from src.common.msg_code import InnerMsgCode
from src.controller.mark_pen import MarkPen
from src.controller.text_line import SessionTextLine


class SessionDocument:
    EXPIRED_MILLISECOND: Final[int] = 50

    def __init__(self, max_row: int):
        self.__MAX_ROW = max_row
        self.__row_pos: int = 1  # 1-based
        self.__lines: List[SessionTextLine] = [SessionTextLine()]
        self.__backup_cursor_position = None
        self.__scrolling_region = None
        self.__history_lines = []
        self.__is_alternate_screen_buffer_on = False

        self.__push_lines_to_history_before_2J = False

        self.__pen = MarkPen()

        self.__content_changed = False

        self.stick_to_bottom = True
        self.stick_to_bottom_lock = threading.Lock()
        self.window_bottom_line_number = 1  # effect when stick_to_bottom is False

        self.__ui_scroll_reqs = []
        self.__ui_scroll_reqs_lock = threading.Lock()

        self.func_handlers: Dict[int, Callable] = {
            InnerMsgCode.CARRIAGE_RETURN_CODE: self.handle_carriage_return,
            InnerMsgCode.STORE_CURSOR_CODE: self.store_cursor,
            InnerMsgCode.RESTORE_CURSOR_CODE: self.restore_cursor,
            InnerMsgCode.CLEAR_LINE_CODE: self.handle_clear_line,
            InnerMsgCode.CLEAR_SCREEN_CODE: self.handle_clear_screen,
            InnerMsgCode.INSERT_PLAIN_STRING_CODE: self.insert_plain_string,
            InnerMsgCode.FUNC_R_CODE: self.handle_func_r,
            InnerMsgCode.CURSOR_MOVE_TO_CODE: self.handle_cursor_move_to,
            InnerMsgCode.FONT_STYLE_CODE: self.handle_font_style,
            InnerMsgCode.MOVE_CURSOR_UP_CODE: self.move_cursor_up,
            InnerMsgCode.MOVE_CURSOR_DOWN_CODE: self.move_cursor_down,
            InnerMsgCode.MOVE_TO_START_OF_NEXT_LINE_CODE: self.move_to_start_of_next_line,
            InnerMsgCode.MOVE_CURSOR_LEFT_CODE: self.move_cursor_left,
            InnerMsgCode.MOVE_CURSOR_RIGHT_CODE: self.move_cursor_right,
            InnerMsgCode.KEYBOARD_APP_MODE_ON_CODE: self.app_mode_on,
            InnerMsgCode.KEYBOARD_APP_MODE_OFF_CODE: self.app_mode_off,
            InnerMsgCode.DEL_CHARS_CODE: self.del_chars,
            InnerMsgCode.REVERSE_INDEX_CODE: self.reverse_index,
            InnerMsgCode.INSERT_LINES_CODE: self.insert_lines,
            InnerMsgCode.INSERT_BLANKS_CODE: self.insert_blanks,
            InnerMsgCode.DEC_RST_CODE: self.handle_dec_rst,
            InnerMsgCode.DEC_SET_CODE: self.handle_dec_set
        }

    def get_max_row(self) -> int:
        return self.__MAX_ROW

    def set_stick_to_bottom(self, stick_to_bottom: bool):
        with self.stick_to_bottom_lock:
            self.stick_to_bottom = stick_to_bottom

    def is_stick_to_bottom(self) -> bool:
        with self.stick_to_bottom_lock:
            return self.stick_to_bottom

    def add_ui_scroll_req(self, req: dict) -> None:
        with self.__ui_scroll_reqs_lock:
            self.__ui_scroll_reqs.append(req)

    def get_and_clear_ui_scroll_reqs(self):
        with self.__ui_scroll_reqs_lock:
            self.__ui_scroll_reqs, snapshot = [], self.__ui_scroll_reqs
            return snapshot

    def handle_msgs(self, inner_msgs: list):
        for inner_msg in inner_msgs:
            inner_msg_code = inner_msg.get('inner_msg_code')
            inner_payload = inner_msg.get('inner_payload')
            if handle_func := self.func_handlers.get(inner_msg_code):
                handle_func() if inner_payload is None else handle_func(inner_payload)

        if inner_msgs:
            self.__content_changed = True

    def insert_session_fail_msg(self, msg: str):
        self.move_to_start_of_next_line()
        self.handle_font_style('0')
        self.handle_font_style('31;1')
        self.insert_plain_string(msg)
        self.handle_font_style('0')
        self.move_to_start_of_next_line()
        self.__content_changed = True

    @property
    def cursor_pos(self) -> Tuple[int, int]:
        return self.__row_pos, self.__lines[self.__row_pos - 1].col_pos

    @cursor_pos.setter
    def cursor_pos(self, pos: Tuple[int, int]):
        if pos is None:
            return

        row_pos, col_pos = pos
        # 不要限制新行在1到MAX_ROW之间，因为它可能超出当前视图区域
        while not (new_row_line := self.__get_line(row_pos)):
            self.__lines.append(SessionTextLine())
        self.__row_pos = row_pos
        new_row_line.set_pos(col_pos)

    @property
    def view_area_content(self) -> List:
        ui_scroll_reqs = self.get_and_clear_ui_scroll_reqs()
        if ui_scroll_reqs or self.__content_changed:
            return self.current_view_area_content(ui_scroll_reqs)

        return []

    @property
    def total_lines(self) -> int:
        return len(self.__history_lines) + len(self.__lines)

    def handle_ui_sroll_reqs(self, ui_scroll_reqs: list, total_line_count: int):
        if total_line_count <= self.__MAX_ROW:
            self.set_stick_to_bottom(True)
            self.window_bottom_line_number = total_line_count
            return

        moved_window_bottom_line_number = self.window_bottom_line_number
        for req in ui_scroll_reqs:
            if 'move' in req:
                moved_window_bottom_line_number += req.get('move', 0)
                continue

            if 'start_line_num' in req:
                start_line_num = req.get('start_line_num', 0)
                moved_window_bottom_line_number = min(start_line_num + self.__MAX_ROW - 1, total_line_count)
                continue

        self.update_window_bottom_line_number_by_scroll_bar(moved_window_bottom_line_number, total_line_count)

    def update_window_bottom_line_number_by_scroll_bar(self, new_window_bottom_line_number: int, total_line_count: int):
        if new_window_bottom_line_number >= total_line_count:
            self.window_bottom_line_number = total_line_count
            self.set_stick_to_bottom(True)
            return

        self.set_stick_to_bottom(False)
        self.window_bottom_line_number = max(new_window_bottom_line_number, self.__MAX_ROW)

    def current_view_area_content(self, ui_scroll_reqs: list) -> List:
        self.__content_changed = False

        line_count = len(self.__lines)
        history_line_count = len(self.__history_lines)
        total_line_count = history_line_count + line_count

        if ui_scroll_reqs:
            self.handle_ui_sroll_reqs(ui_scroll_reqs, total_line_count)

        if self.is_stick_to_bottom():
            self.window_bottom_line_number = total_line_count
            if not self.__is_alternate_screen_buffer_on and (history_line_count := (self.__MAX_ROW - line_count)) > 0:
                return [line.line for line in self.__history_lines[-history_line_count:]] \
                    + [line.line for line in self.__lines]
            return [line.line for line in self.__lines]

        if self.window_bottom_line_number <= history_line_count:
            return [line.line for line in self.__history_lines[
                self.window_bottom_line_number - self.__MAX_ROW:self.window_bottom_line_number]]

        line_count = self.window_bottom_line_number - history_line_count
        history_line_count = self.__MAX_ROW - line_count
        return [line.line for line in self.__history_lines[-history_line_count:]] \
            + [line.line for line in self.__lines[:line_count]]

    def handle_carriage_return(self):
        self.cursor_pos = (self.__row_pos, 1)

    def store_cursor(self):
        self.__backup_cursor_position = self.cursor_pos

    def restore_cursor(self):
        self.cursor_pos = self.__backup_cursor_position

    def handle_clear_line(self, inner_payload: str = ''):
        if not (current_line := self.__get_current_line()):
            return

        if inner_payload == '' or inner_payload == '0':
            current_line.erase_to_right()
        elif inner_payload == '1':
            current_line.erase_to_left()
        elif inner_payload == '2':
            current_line.erase_all()

        # 注意：这里不需要更新光标列位置，因为它在行擦除方法中已经改变了

    def handle_clear_screen(self, inner_payload: str = ''):
        # CAUTION:
        # 清理屏幕，不要改变光标位置！！！后续ansi会改变光标位置的
        current_line = self.__get_current_line()

        if not current_line:
            return

        if inner_payload == '0' or inner_payload == '':
            # \x1b[0J: 从当前光标位置删除到屏幕末尾
            # 当前行从光标位置到行尾的内容被删除，包括当前光标位置
            # 光标下面的所有行完全删除（包括空行）
            current_line.erase_to_right()
            self.__lines[self.__row_pos:] = []
            return

        if inner_payload == '1':
            # \x1b[1J: 从屏幕开始删除到当前光标位置,包括当前光标位置
            self.__lines[: self.__row_pos - 1] = []
            current_line.erase_to_left()
            return

        if inner_payload == '2':
            # \x1b[2J: 清除整个屏幕
            if self.__push_lines_to_history_before_2J:
                self.__history_lines.extend(self.__lines[:-1])
                self.__push_lines_to_history_before_2J = False
            self.__lines = [SessionTextLine()]
            return

        if inner_payload == '3':
            # \x1b[3J: 清除整个屏幕和滚动缓冲区
            self.__history_lines = []
            self.__lines = [SessionTextLine()]
            return

    def insert_plain_string(self, inner_payload: str):
        if current_line := self.__get_current_line():
            current_line.write(
                self.__pen.render(inner_payload.expandtabs(8) if '\t' in inner_payload else inner_payload)
            )

        # inner_payload will not contain LF, so do not need flush view here. KEEP THIS COMMENT!!!
        # self.__flush_view()

    def handle_func_r(self, inner_payload: str = ''):
        self.__scrolling_region = (1, self.__MAX_ROW) if inner_payload == '' \
            else tuple(map(int, inner_payload.split(';')))

    def handle_cursor_move_to(self, inner_payload: str = ''):
        row_column_params = '1;1' if inner_payload in ['', '0', '1', '0;1', '1;0'] else inner_payload
        new_row_pos, new_col_pos = map(int, row_column_params.split(';'))

        # 不要限制新行在1到MAX_ROW之间，它可能超出视图区
        self.cursor_pos = (new_row_pos, new_col_pos)

        self.__flush_view()

    def handle_font_style(self, inner_payload: str = ''):
        # 重置鼠标形状 (\x1b[>4;m),这个不是字体格式控制
        if '>' in inner_payload:
            return

        self.__pen.update_style(inner_payload)

    def move_cursor_up(self, inner_payload: str = ''):
        n = 1 if inner_payload == '' else int(inner_payload)
        org_row, org_col = self.cursor_pos
        self.cursor_pos = (max(1, org_row - n), org_col)

    def move_cursor_down(self, inner_payload: str = ''):
        n = 1 if inner_payload == '' else int(inner_payload)
        org_row, org_col = self.cursor_pos
        self.cursor_pos = (min(self.__MAX_ROW, org_row + n), org_col)

    def move_to_start_of_next_line(self, *args):
        if self.__scrolling_region and self.__scrolling_region[1] == self.__row_pos:
            self.__lines.pop(self.__scrolling_region[0] - 1)
            self.__lines.insert(self.__row_pos - 1, SessionTextLine())
            self.cursor_pos = (self.__row_pos, 1)
            return

        self.cursor_pos = (self.__row_pos + 1, 1)
        self.__flush_view()

    def move_cursor_left(self, inner_payload: str = ''):
        if current_line := self.__get_current_line():
            current_line.move_pos(-(1 if inner_payload == '' else int(inner_payload)))

    def move_cursor_right(self, inner_payload: str = ''):
        if current_line := self.__get_current_line():
            current_line.move_pos(1 if inner_payload == '' else int(inner_payload))

    def app_mode_on(self):
        pass

    def app_mode_off(self):
        self.__scrolling_region = None
        pass

    def del_chars(self, inner_payload: str = ''):
        # 删去包含当前光标位置在内的n个字符，光标位置不变，后续会有ansi控制光标移动
        if current_line := self.__get_current_line():
            current_line.erase_to_right(1 if inner_payload == '' else int(inner_payload))

    def reverse_index(self):
        if not self.__scrolling_region:
            top_row_pos, bottom_row_pos = 1, self.__MAX_ROW
        else:
            top_row_pos, bottom_row_pos = self.__scrolling_region

        # 删除滚动区域的底部行，仅当该行存在时
        if 1 <= bottom_row_pos <= len(self.__lines):
            self.__lines.pop(bottom_row_pos - 1)

        # 在顶部插入一个新空白行
        self.__lines.insert(top_row_pos - 1, SessionTextLine())

    def insert_lines(self, inner_payload: str = ''):
        if not self.__scrolling_region:
            top_row_pos, bottom_row_pos = 1, self.__MAX_ROW
        else:
            top_row_pos, bottom_row_pos = self.__scrolling_region

        # 只有当光标在滚动区域内时，才能插入行
        if not (top_row_pos <= self.__row_pos <= bottom_row_pos):
            return

        n = 1 if inner_payload == '' else int(inner_payload)
        for i in range(n):
            if self.__get_line(bottom_row_pos):
                self.__lines.pop(bottom_row_pos - 1)
            self.__lines.insert(self.__row_pos - 1, SessionTextLine())

    def insert_blanks(self, inner_payload: str = ''):
        if current_line := self.__get_current_line():
            current_line.insert_blanks(1 if inner_payload == '' else int(inner_payload), is_append=False)

    def handle_dec_set(self, inner_payload: str = ''):
        if inner_payload in ['?1049', '?47', '?1047']:
            self.__is_alternate_screen_buffer_on = True
            self.__history_lines.extend(self.__lines)
            self.__lines = [SessionTextLine()]
            self.__row_pos = 1

    def handle_dec_rst(self, inner_payload: str = ''):
        if inner_payload in ['?1049', '?47', '?1047'] and self.__is_alternate_screen_buffer_on:
            self.__is_alternate_screen_buffer_on = False
            self.__lines = self.__history_lines[-self.__MAX_ROW:]
            self.__history_lines[-self.__MAX_ROW:] = []
            self.__row_pos = len(self.__lines)

        if inner_payload == '?2004':
            self.__push_lines_to_history_before_2J = True

    def __flush_view(self):
        while len(self.__lines) > self.__MAX_ROW:
            row_pos, col_pos = self.cursor_pos
            if not self.__is_alternate_screen_buffer_on:
                self.__history_lines.append(self.__lines.pop(0))
            else:
                self.__lines.pop(0)
            self.cursor_pos = (max(1, row_pos - 1), col_pos)
            if self.__backup_cursor_position:
                backup_row, backup_col = self.__backup_cursor_position
                self.__backup_cursor_position = (max(1, backup_row - 1), backup_col)

    def __get_line(self, row: int | str) -> SessionTextLine | None:
        row_pos = row if row != 'current' else self.__row_pos
        return self.__lines[row_pos - 1] if (1 <= row_pos <= len(self.__lines)) else None

    def __get_current_line(self) -> SessionTextLine | None:
        return self.__get_line('current')
