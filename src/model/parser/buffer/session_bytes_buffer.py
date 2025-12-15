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


import codecs
from collections import namedtuple
from typing import Optional

from src.common.msg_code import InnerMsgCode
from src.model.parser.xterm_ctrl_sequences.xterm_code import INCOMPLETE_ANSI_RE, XTERM_PARSER_RE, XTERM_ASCII_CODE_BS, \
    XTERM_ASCII_CODE_VT, XTERM_ASCII_CODE_FF, XTERM_CTRL_SEQ_RESTORE_CURSOR, XTERM_CTRL_SEQ_SAVE_CURSOR, \
    XTERM_CTRL_SEQ_APPLICATION_KEYPAD, XTERM_CTRL_SEQ_NORMAL_KEYPAD, XTERM_CTRL_SEQ_SCROLL_REVERSE_INDEX, \
    XTERM_CTRL_SEQ_SCROLL_INDEX, XTERM_CTRL_SEQ_NEXT_LINE

FuncParams = namedtuple('FuncParams', ['inner_msg_code', 'params'])


class SessionBytesBuffer:
    SES_FUNC_MAP = {
        XTERM_CTRL_SEQ_SAVE_CURSOR: FuncParams(InnerMsgCode.STORE_CURSOR_CODE, None),  # b'7':
        XTERM_CTRL_SEQ_RESTORE_CURSOR: FuncParams(InnerMsgCode.RESTORE_CURSOR_CODE, None),  # b'8':
        XTERM_CTRL_SEQ_APPLICATION_KEYPAD: FuncParams(InnerMsgCode.KEYBOARD_APP_MODE_ON_CODE, None),  # b'=':
        XTERM_CTRL_SEQ_NORMAL_KEYPAD: FuncParams(InnerMsgCode.KEYBOARD_APP_MODE_OFF_CODE, None),  # b'>':
        XTERM_CTRL_SEQ_SCROLL_REVERSE_INDEX: FuncParams(InnerMsgCode.REVERSE_INDEX_CODE, None),  # b'M':
        XTERM_CTRL_SEQ_SCROLL_INDEX: FuncParams(InnerMsgCode.INDEX_CODE, None),  # b'D':
        XTERM_CTRL_SEQ_NEXT_LINE: FuncParams(InnerMsgCode.MOVE_TO_START_OF_NEXT_LINE_CODE, None)  # b'E':
    }

    CSI_FUNC_MAP = {
        b'A': InnerMsgCode.MOVE_CURSOR_UP_CODE,
        b'B': InnerMsgCode.MOVE_CURSOR_DOWN_CODE,
        b'C': InnerMsgCode.MOVE_CURSOR_RIGHT_CODE,
        b'D': InnerMsgCode.MOVE_CURSOR_LEFT_CODE,
        b'H': InnerMsgCode.CURSOR_MOVE_TO_CODE,
        b'f': InnerMsgCode.CURSOR_MOVE_TO_CODE,
        b'K': InnerMsgCode.CLEAR_LINE_CODE,
        b'J': InnerMsgCode.CLEAR_SCREEN_CODE,
        b'm': InnerMsgCode.FONT_STYLE_CODE,
        b'r': InnerMsgCode.FUNC_R_CODE,
        b'P': InnerMsgCode.DEL_CHARS_CODE,
        b'L': InnerMsgCode.INSERT_LINES_CODE,
        b'@': InnerMsgCode.INSERT_BLANKS_CODE,
        b'l': InnerMsgCode.DEC_RST_CODE,
        b'h': InnerMsgCode.DEC_SET_CODE,
    }

    def __init__(self):
        self.buffer = b''
        self.keyboard_app_mode_on = False
        self.decoder = codecs.getincrementaldecoder("utf-8")(errors='replace')

    def parse(self, income_bytes: bytes, last_send_bytes: bytes):
        self.buffer += income_bytes

        if last_send_bytes == income_bytes or not INCOMPLETE_ANSI_RE.search(self.buffer[-30:]):
            yield from self.__parse_iter()

    def __parse_iter(self):
        begin_index = 0
        plain_text_bytes = b''

        for xterm_control in XTERM_PARSER_RE.finditer(self.buffer):
            xterm_ctrl_begin, xterm_ctrl_end = xterm_control.span()

            plain_text_bytes += self.buffer[begin_index:xterm_ctrl_begin]
            begin_index = xterm_ctrl_end

            if plain_text_bytes:
                yield {
                    'inner_msg_code': InnerMsgCode.INSERT_PLAIN_STRING_CODE,
                    'inner_payload': self.decoder.decode(plain_text_bytes, final=False)
                }
                plain_text_bytes = b''

            if func_params := self.__parse_xterm(xterm_control):
                yield {
                    'inner_msg_code': func_params.inner_msg_code,
                    'inner_payload': func_params.params.decode('utf-8') if func_params.params else None
                }

        if rest_bytes := plain_text_bytes + self.buffer[begin_index:]:
            yield {
                'inner_msg_code': InnerMsgCode.INSERT_PLAIN_STRING_CODE,
                'inner_payload': self.decoder.decode(rest_bytes, final=False)
            }

        self.buffer = b''

    def __parse_xterm(self, xterm_control_info):
        last_group = xterm_control_info.lastgroup
        group_dict = xterm_control_info.groupdict()

        if last_group == 'TERM_CAP_DELAY':
            return None

        if last_group == 'ASCII_1':
            ascii_code = group_dict.get(last_group)
            if ascii_code == XTERM_ASCII_CODE_BS:
                return FuncParams(InnerMsgCode.MOVE_CURSOR_LEFT_CODE, None)
            if ascii_code in [XTERM_ASCII_CODE_VT, XTERM_ASCII_CODE_FF]:
                return FuncParams(InnerMsgCode.MOVE_TO_START_OF_NEXT_LINE_CODE, None)
            return None

        if last_group == 'ASCII_LF':
            return FuncParams(InnerMsgCode.MOVE_TO_START_OF_NEXT_LINE_CODE, None)

        if last_group == 'ASCII_CR':
            return FuncParams(InnerMsgCode.CARRIAGE_RETURN_CODE, None)

        if last_group == 'ANSI':
            return self.__parse_ansi(group_dict)

        return None

    def __parse_ansi(self, group_dict):
        if group_dict.get('CSI'):
            return SessionBytesBuffer.__get_csi_func_params(group_dict['CSI_F'], group_dict['CSI_P'])

        if simple_escape_sequences := group_dict.get('SUPPORT_SES'):
            func_params = SessionBytesBuffer.SES_FUNC_MAP.get(simple_escape_sequences)
            if func_params is None:
                return None
            if func_params.inner_msg_code == InnerMsgCode.KEYBOARD_APP_MODE_ON_CODE:
                self.keyboard_app_mode_on = True
            elif func_params.inner_msg_code == InnerMsgCode.KEYBOARD_APP_MODE_OFF_CODE:
                self.keyboard_app_mode_on = False
            return func_params

        return None

    @staticmethod
    def __get_csi_func_params(csi_func: bytes, csi_params: bytes) -> Optional[FuncParams]:
        if inner_msg_code := SessionBytesBuffer.CSI_FUNC_MAP.get(csi_func):
            return FuncParams(inner_msg_code, csi_params)
        return None
