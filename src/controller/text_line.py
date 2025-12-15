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


from typing import List, Union

from src.common.font_style import FontStyle
from src.controller.mark_pen import CharCell


class SessionTextLine:
    # special marker for the end of the line, not a real character
    END_MARK = None
    END_POS = -1

    def __init__(self):
        self.__write_pos = 1
        self.__cells: List[Union[str, CharCell] | SessionTextLine.END_MARK] = [SessionTextLine.END_MARK]

    @property
    def line(self) -> list:
        result = []

        for cell in self.__cells[: SessionTextLine.END_POS]:
            current_char, current_style = cell.char, cell.style

            if result and result[-1]['style'] == current_style:
                result[-1]['chars'].append(current_char)
            else:
                result.append({'style': current_style, 'chars': [current_char]})

        return [{'style': x['style'], 'text': ''.join(x['chars'])} for x in result]

    def write(self, chars: List[Union[str, CharCell]], pos_move=True):
        write_len = len(chars)
        write_index = self.__write_pos - 1
        replace_len = min(self.__rest_len(), write_len)

        self.__cells[write_index: write_index + replace_len] = chars
        if pos_move:
            self.__write_pos += write_len

    def set_pos(self, pos: int):
        if pos and (over_move := pos - len(self.__cells)) > 0:
            self.insert_blanks(over_move)

        self.__write_pos = pos

    def move_pos(self, offset: int, force=True):
        new_pos = self.__write_pos + offset
        if force and new_pos > (line_len := len(self.__cells)):
            self.insert_blanks(new_pos - line_len)
        self.__write_pos = max(1, min(new_pos, len(self.__cells)))

    def erase_to_right(self, n: int | None = None):
        if n is None:
            # erase from current position to the end None mark, include current position
            self.__cells[self.__write_pos - 1: SessionTextLine.END_POS] = []
            return
        erase_len = min(self.__rest_len(), n)
        self.__cells[self.__write_pos - 1: self.__write_pos - 1 + erase_len] = []

    def erase_to_left(self):
        self.__cells[: self.__write_pos] = []
        self.__write_pos = 1

    def erase_all(self):
        self.__cells[: SessionTextLine.END_POS] = []
        self.__write_pos = 1

    def insert_blanks(self, num: int, is_append=True):
        if num <= 0:
            return

        if is_append:
            self.__cells[SessionTextLine.END_POS: SessionTextLine.END_POS] = \
                [CharCell(char=' ', style=FontStyle.DEFAULT_STYLE_TUPLE) for _ in range(num)]
            return

        # push text move n blanks right from current position
        self.__cells[self.__write_pos - 1: self.__write_pos - 1] = \
            [CharCell(char=' ', style=FontStyle.DEFAULT_STYLE_TUPLE) for _ in range(num)]

    @property
    def col_pos(self):
        return self.__write_pos

    def __rest_len(self):
        # include current position
        return len(self.__cells[: SessionTextLine.END_POS]) - self.__write_pos + 1
