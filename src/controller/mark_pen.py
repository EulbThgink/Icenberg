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


from collections import namedtuple
from typing import List
from src.common.font_style import FontStyle

CharCell = namedtuple('CharCell', ['style', 'char'])


class MarkPen:
    def __init__(self):
        self.__font_style = FontStyle()

    def render(self, text: str) -> List[CharCell | str]:
        return [CharCell(style=self.__font_style.style, char=char) for char in text]

    def update_style(self, csi_params: str):
        self.__font_style.update(csi_params)
