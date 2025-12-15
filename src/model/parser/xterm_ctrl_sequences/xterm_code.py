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


import re

# ascii control character for xterm
XTERM_ASCII_CODE_BEL = b'\x07'  # BEL
XTERM_ASCII_CODE_BS = b'\x08'  # BS backspace
XTERM_ASCII_CODE_HT = b'\x09'  # HT horizontal tab, \t
XTERM_ASCII_CODE_LF = b'\x0a'  # LF new line, \n
XTERM_ASCII_CODE_VT = b'\x0b'  # VT vertical tab, same as \n
XTERM_ASCII_CODE_FF = b'\x0c'  # FF form feed, same as \n
XTERM_ASCII_CODE_CR = b'\x0d'  # CR carriage return, \r
XTERM_ASCII_CODE_SO = b'\x0e'  # SO shift out, switch to alternate character set: invokes the G1 character set
XTERM_ASCII_CODE_SI = b'\x0f'  # SI shift in, switch to standard character set: invokes the G0 character set
XTERM_ASCII_CODE_ANSI_CS = b'\x1b'  # ESC, start of control sequence

# ansi control sequences for xterm
'''SUPPORT!!!
save cursor position'''
XTERM_CTRL_SEQ_SAVE_CURSOR = b'7'

'''SUPPORT!!!
restore cursor position'''
XTERM_CTRL_SEQ_RESTORE_CURSOR = b'8'

'''SUPPORT!!!
turn on application keypad mode, in this mode, the keypad keys send application-specific codes'''
XTERM_CTRL_SEQ_APPLICATION_KEYPAD = b'='

'''SUPPORT!!!
turn off application keypad mode, in this mode, the keypad keys send normal codes'''
XTERM_CTRL_SEQ_NORMAL_KEYPAD = b'>'

'''SUPPORT!!!
if scroll region is full->remove 1 top line and insert 1 bottom line'''
XTERM_CTRL_SEQ_SCROLL_INDEX = b'D'

'''SUPPORT!!!
if scroll region is full->remove 1 bottom line and insert 1 top line'''
XTERM_CTRL_SEQ_SCROLL_REVERSE_INDEX = b'M'

'''SUPPORT!!!
move cursor to begin of next line, same as \r\n'''
XTERM_CTRL_SEQ_NEXT_LINE = b'E'

'''NOT SUPPORT!!!
move cursor to lower left corner of screen, NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_HP_LOWER_LEFT = b'F'

'''NOT SUPPORT!!!
set tab stop at current cursor position'''
XTERM_CTRL_SEQ_TAB_SET = b'H'

'''NOT SUPPORT!!!
single shift select G2 character set'''
XTERM_CTRL_SEQ_SINGLE_SHIFT_SELECT_G2 = b'N'

'''NOT SUPPORT!!!
single shift select G3 character set'''
XTERM_CTRL_SEQ_SINGLE_SHIFT_SELECT_G3 = b'O'

'''NOT SUPPORT!!!
return terminal ID, this is an obsolete form of ESC[c, NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_RETURN_TERMINAL_ID = b'Z'

'''NOT SUPPORT!!!
full reset, reset terminal to initial state, NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_FULL_RESET = b'c'

'''NOT SUPPORT!!!
memory lock, HP terminal, NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_MEMORY_LOCK = b'l'  # memory lock,HP terminal, NOT SUPPORT!!!

'''NOT SUPPORT!!!
memory unlock, HP terminal, NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_MEMORY_UNLOCK = b'm'

'''NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_LS2 = b'n'  # invoke the G2 character set, NOT SUPPORT!!!
XTERM_CTRL_SEQ_LS3 = b'o'  # invoke the G3 character set, NOT SUPPORT!!!
XTERM_CTRL_SEQ_LS3R = b'|'  # invoke the G3 character set as GR, has no visible effect in xterm, NOT SUPPORT!!!
XTERM_CTRL_SEQ_LS2R = b'}'  # invoke the G2 character set as GR, has no visible effect in xterm, NOT SUPPORT!!!
XTERM_CTRL_SEQ_LS1R = b'~'  # invoke the G1 character set as GR, has no visible effect in xterm, NOT SUPPORT!!!

'''NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_SPA = b'V'  # start of guarded area, SPA, NOT SUPPORT!!!
XTERM_CTRL_SEQ_EPA = b'W'  # end of guarded area, EPA, NOT SUPPORT!!!
XTERM_CTRL_SEQ_SOS = b'X'  # start of string, SOS, NOT SUPPORT!!!

# ---------------------------------- Parameter, no function ----------------------------------
'''NOT SUPPORT!!!
ESC # 3:DEC double-height line, top half (DECDHL)
ESC # 4:DEC double-height line, bottom half (DECDHL)
ESC # 5:DEC single-width line (DECSWL)
ESC # 6:DEC double-width line (DECDWL)
ESC # 8:DEC Screen Alignment Test (DECALN)'''
XTERM_CTRL_SEQ_DEC_SCREEM_BEGIN = b'#'

'''NOT SUPPORT!!!
ESC % @:Select default character set, ISO 8859-1 (ISO 2022)
ESC % G:Select UTF-8 character set (ISO 2022)'''
XTERM_CTRL_SEQ_SELECT_CHARACTER = b'%'  # (ESC%@,ESC%G) NOT SUPPORT

'''NOT SUPPORT!!!
ESC ( C , Designate G0 Character Set (ISO 2022)
ESC ) C , Designate G1 Character Set (ISO 2022)
ESC * C , Designate G2 Character Set (ISO 2022)
ESC + C , Designate G3 Character Set (ISO 2022)
C = 0 → DEC Special Character and Line Drawing Set
C = A → United Kingdom (UK)
C = B → United States (USASCII)
C = 4 → Dutch
C = C or 5 → Finnish
C = R → French
C = Q → French Canadian
C = K → German
C = Y → Italian
C = E or 6 → Norwegian/Danish
C = Z → Spanish
C = H or 7 → Swedish
C = = → Swiss
'''
XTERM_CTRL_SEQ_DESIGNATE_G0 = b'('
XTERM_CTRL_SEQ_DESIGNATE_G1 = b')'
XTERM_CTRL_SEQ_DESIGNATE_G2 = b'*'
XTERM_CTRL_SEQ_DESIGNATE_G3 = b'+'

'''SUPPORT!!!
begin of control sequence introducer, CSI, used to send control sequences with parameters'''
XTERM_CTRL_SEQ_CSI = b'['

'''NOT SUPPORT!!!
ESC SP F, 7-bit controls (S7C1T).
ESC SP G, 8-bit controls (S8C1T).
ESC SP L, Set ANSI conformance level 1 (dpANS X3.134.1).
ESC SP M, Set ANSI conformance level 2 (dpANS X3.134.1).'''
XTERM_CTRL_SEQ_SP = b' '  # space, used to separate parameters in control sequences, NOT SUPPORT!!!
# ---------------------------------- control sequence pair ----------------------------------
'''ESC P Pt ESC \\ , Device Control String, DCS, xterm implements no DCS sequences, Pt is ignored,'''
'''NOT SUPPORT!!!
begin of device control string, DCS, used to send device-specific control sequences'''
XTERM_CTRL_SEQ_DCS = b'P'

'''ESC _ Pt ESC \\ , Application Program Command (APC), xterm implements no APC functions; Pt is ignored.'''
'''NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_APC = b'_'  # APC, application program command

'''ESC ^ Pt ESC \\ , Privacy Message (PM), xterm implements no PM functions; Pt is ignored.'''
'''NOT SUPPORT!!!'''
XTERM_CTRL_SEQ_PM = b'^'  # PM, privacy message

'''ESC ] Ps ; Pt BEL 
   ESC ] Ps ; Pt Esc \\
   Operating System Command, OSC, used to send commands to the operating system, e.g., setting terminal title'''
'''NOT SUPPORT!!!
Ps=0: set terminal icon name and window title
Ps=1: set terminal icon name
Ps=2: set terminal window title
Ps=46: set Log File to Pt
Ps=50: set font to Pt'''
XTERM_CTRL_SEQ_OSC_RAW = rb'\]'
XTERM_CTRL_SEQ_OSC = b']'

'''NOT SUPPORT!!!
String Terminal, ST, used to end a control sequence that was started with DCS'''
XTERM_CTRL_SEQ_ST_RAW = rb'\\'
XTERM_CTRL_SEQ_ST = b'\\'

# ---------------------------------- old control sequences ----------------------------------
TERM_CAP_DELAY_RE_STR = b'\\$<\\d+>'  # termcap delay, used to delay the terminal output, e.g., $<1000> for 1 second

INCOMPLETE_ANSI_RE = re.compile(
    b'('
    b'(\\$(<(\\d+)?)?)'
    b'|'
    b'(\x1b((\\[([0-9;?>!"$\']*)?)|([#%()*+ \\]]?)|([P^_\\]]([^\x07\x1b\\\\]*?)?))?)'
    b')'
    b'$'
)

XTERM_PARSER_RE = re.compile(
    b'(?P<TERM_CAP_DELAY>\\$<\\d+>)'
    b'|(?P<ASCII_1>[\x07\x08\x0b\x0c\x0e\x0f])'  # ASCII control characters, excluding LF and CR
    b'|(?P<ASCII_LF>\r*\n)'  # \x0d*\x0a LF
    b'|(?P<ASCII_CR>\r+(?!\n))'  # \x0d CR
    b'|(?P<ANSI>\x1b'
    b'('
    b'(?P<CSI>\\[(?P<CSI_P>[0-9;?>!$"\']*?)(?P<CSI_F>[@ABCDEFGHIJKLMPSTXZ`bcdfghilmnpqrstuvwxz{|]))'  # CSI control sequences
    b'|(?P<SUPPORT_SES>[78=>DME])'  # Support Simple Escape Sequences
    b'|(?P<SES>[HNOVWXZFclmno|}~])'  # Unsupport Simple Escape Sequences
    b'|(?P<ESFC>[ #%()*+].)'  # Escape sequences with intermediate and final characters
    b'|(?P<OSC>].*?(\x1b\\\\|\x07))'  # Operating System Command, OSC, used to send commands to the operating system, e.g., setting terminal title
    b'|(?P<DCS_APC_PM>[P^_].*?\x1b\\\\)'  # DCS APC PM
    b')'
    b')'
)
