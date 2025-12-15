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


class StyleTuple:
    def __init__(self, bold: bool, italic: bool, opacity: float, visible: bool,
                 underline: bool, background_color: str, foreground_color: str):
        self.bold = bold
        self.italic = italic
        self.opacity = opacity
        self.visible = visible
        self.underline = underline
        self.background_color = background_color
        self.foreground_color = foreground_color

    def to_dict(self):
        return {
            'bold': self.bold,
            'italic': self.italic,
            'opacity': self.opacity,
            'visible': self.visible,
            'underline': self.underline,
            'background_color': self.background_color,
            'foreground_color': self.foreground_color
        }

    def tuple_key(self) -> tuple:
        return self.bold, self.italic, self.opacity, self.visible, self.underline, \
            self.background_color, self.foreground_color

    def is_equal(self, other):
        return self.bold == other.bold \
            and self.italic == other.italic \
            and self.opacity == other.opacity \
            and self.visible == other.visible \
            and self.underline == other.underline \
            and self.background_color == other.background_color \
            and self.foreground_color == other.foreground_color


class FontStyle:
    DEFAULT_BACKGROUND_COLOR = "#FFFFFF"
    DEFAULT_FOREGROUND_COLOR = "#000000"

    DEFAULT_STYLE_TUPLE = StyleTuple(
        bold=False,
        italic=False,
        opacity=1.0,
        visible=True,
        underline=False,
        background_color=DEFAULT_BACKGROUND_COLOR,
        foreground_color=DEFAULT_FOREGROUND_COLOR
    )

    STYLE_SET = dict()
    STYLE_MAP = {
        '': DEFAULT_STYLE_TUPLE.to_dict(),
        '0': DEFAULT_STYLE_TUPLE.to_dict(),
        '1': {'bold': True},
        '01': {'bold': True},
        '2': {'opacity': 0.5},
        '02': {'opacity': 0.5},
        '3': {'italic': True},
        '03': {'italic': True},
        '4': {'underline': True},
        '04': {'underline': True},
        '7': {
            'background_color': DEFAULT_FOREGROUND_COLOR,
            'foreground_color': DEFAULT_BACKGROUND_COLOR
        },
        '07': {
            'background_color': DEFAULT_FOREGROUND_COLOR,
            'foreground_color': DEFAULT_BACKGROUND_COLOR
        },
        '8': {'visible': False},
        '08': {'visible': False},
        '22': {'bold': False},
        '24': {'underline': False},
        '27': {
            'background_color': DEFAULT_BACKGROUND_COLOR,
            'foreground_color': DEFAULT_FOREGROUND_COLOR
        },
        '28': {'visible': True},

        '30': {'foreground_color': "#000000"},
        '31': {'foreground_color': "#800000"},
        '32': {'foreground_color': "#008000"},
        '33': {'foreground_color': "#808000"},
        '34': {'foreground_color': "#000080"},
        '35': {'foreground_color': "#800080"},
        '36': {'foreground_color': "#008080"},
        '37': {'foreground_color': "#C0C0C0"},
        '39': {'foreground_color': DEFAULT_FOREGROUND_COLOR},
        '90': {'foreground_color': "#808080"},
        '91': {'foreground_color': "#FF0000"},
        '92': {'foreground_color': "#00FF00"},
        '93': {'foreground_color': "#FFFF00"},
        '94': {'foreground_color': "#0000FF"},
        '95': {'foreground_color': "#FF00FF"},
        '96': {'foreground_color': "#00FFFF"},
        '97': {'foreground_color': "#FFFFFF"},

        '40': {'background_color': "#000000"},
        '41': {'background_color': "#800000"},
        '42': {'background_color': "#008000"},
        '43': {'background_color': "#808000"},
        '44': {'background_color': "#000080"},
        '45': {'background_color': "#800080"},
        '46': {'background_color': "#008080"},
        '47': {'background_color': "#C0C0C0"},
        '49': {'background_color': DEFAULT_BACKGROUND_COLOR},
        '100': {'background_color': "#808080"},
        '101': {'background_color': "#FF0000"},
        '102': {'background_color': "#00FF00"},
        '103': {'background_color': "#FFFF00"},
        '104': {'background_color': "#0000FF"},
        '105': {'background_color': "#FF00FF"},
        '106': {'background_color': "#00FFFF"},
        '107': {'background_color': "#FFFFFF"}
    }

    def __init__(self):
        self.__style = FontStyle.DEFAULT_STYLE_TUPLE
        self.__style_dict: dict = FontStyle.DEFAULT_STYLE_TUPLE.to_dict()

    @property
    def style(self) -> StyleTuple:
        return self.__style

    def update(self, csi_params: str):
        for csi_param in csi_params.split(';'):
            if style_param := FontStyle.STYLE_MAP.get(csi_param):
                self.__style_dict.update(style_param)

        self.__update_style()

    def __update_style(self):
        style_tuple = (
            self.__style_dict.get('bold', False),
            self.__style_dict.get('italic', False),
            self.__style_dict.get('opacity', 1.0),
            self.__style_dict.get('visible', True),
            self.__style_dict.get('underline', False),
            self.__style_dict.get('background_color', FontStyle.DEFAULT_BACKGROUND_COLOR),
            self.__style_dict.get('foreground_color', FontStyle.DEFAULT_FOREGROUND_COLOR)
        )

        new_style = FontStyle.STYLE_SET.get(style_tuple)
        if not new_style:
            new_style = StyleTuple(**self.__style_dict)
            FontStyle.STYLE_SET[style_tuple] = new_style
        self.__style = new_style
