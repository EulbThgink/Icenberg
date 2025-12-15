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
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox, QListView, QFrame, QToolButton, \
    QCheckBox, QLabel


class PillLlmWidget(QFrame):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.setObjectName("PillLlmWidget")
        self.setFrameShape(QFrame.Shape.NoFrame)

        self.enable_check = QCheckBox(self)
        self.enable_check.setChecked(False)
        self.enable_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.enable_check.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.enable_check.clicked.connect(self.set_label_color)

        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.setFrame(False)
        self.combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.combo.setView(QListView())

        if items:
            self.combo.addItems(items)
        else:
            self.combo.addItems([])

        self.send_btn = QToolButton(self)
        self.send_btn.setText("▶")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.setObjectName("GoButton")
        self.send_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.link_screen_label = QLabel("ScrCtx")
        self.link_screen_label.setObjectName("ScrCtx")
        self.link_screen_label.setToolTip("设置大模型回答时是否结合当前屏幕内容")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 3, 10, 3)
        lay.setSpacing(5)
        lay.addWidget(self.enable_check, 0, Qt.AlignmentFlag.AlignVCenter)
        lay.addWidget(self.link_screen_label, 0, Qt.AlignmentFlag.AlignVCenter)

        lay.addStretch(1)

        lay.addWidget(self.combo, 0)
        lay.addWidget(self.send_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet("""
        /* 胶囊容器 */
        #PillLlmWidget {
            border: 1px solid #B5C7FF;
            border-radius: 5px;
        }
        #PillLlmWidget:hover {
            border-color: #8EA6FF;
        }
        #PillLlmWidget:focus-within { /* 子控件获得焦点时高亮 */
            border: 2px solid #5B8CFF;
            background: #F2F6FF;
        }
        QCheckBox {
            spacing: 0px;
            margin-left: 0px;
            margin-right: 0px;
        }
        #ScrCtx {
            color: #999999;
            font-size: 13px;
            margin-left: 0px;
            margin-right: 10px;
        }
        /* 下拉框本体去掉自带边框/背景，保持胶囊统一外观 */
        QComboBox {
            border: none;
            border-left: 1px solid #CCCCCC;
            padding: 5px 10px 5px 10px;
            background: transparent;
            font-size: 13px;
        }
        QListView {
            border: none;
            background: transparent;
            font-size: 13px;
        }
        #GoButton {
            border: none;
            color: rgba(19,185,13,1);
            background: transparent;
            font-size: 13px;
        }
        #GoButton:hover {
            background: rgba(19,185,13,0.06);
            border-radius: 6px;
        }
        #GoButton:disabled {
            color: #AAAAAA;
            background: transparent;
        }
        QToolTip {
            font-size: 13px;
        }""")

    def set_label_color(self):
        if self.enable_check.isChecked():
            self.link_screen_label.setStyleSheet("color: #378CE6; font-weight: bold;")
        else:
            self.link_screen_label.setStyleSheet("color: #999999; font-weight: normal;")


class LlmChatBottomWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        self.input_line = QTextEdit()
        self.input_line.setViewportMargins(0, 0, 0, 0)
        self.input_line.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        font = QFont("Arial", 13)
        self.input_line.setFont(font)

        font_metrics = self.input_line.fontMetrics()
        line_height = font_metrics.height()
        fixed_height = line_height * 8 + 10
        self.input_line.setFixedHeight(fixed_height)

        main_layout.addWidget(self.input_line, stretch=1)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        self.pill_llm_widget = PillLlmWidget([], self)

        bottom_layout.addWidget(self.pill_llm_widget)

        main_layout.addLayout(bottom_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: none;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
            QTextEdit:hover {
                border: 1px solid #888888;
            }
            QTextEdit:focus {
                border: 1px solid #5B8CFF;
            }
        """)

    def get_current_model_name(self):
        return self.pill_llm_widget.combo.currentText()
