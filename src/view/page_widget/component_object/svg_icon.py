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


from PySide6.QtGui import QIcon, QPixmap, Qt, QPainter
from PySide6.QtSvg import QSvgRenderer


def get_icon_from_svg(svg_str: str) -> QIcon:
    svg_renderer = QSvgRenderer()
    svg_renderer.load(svg_str.encode('utf-8'))
    pixmap = QPixmap(100, 100)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    svg_renderer.render(painter)
    painter.end()
    return QIcon(pixmap)