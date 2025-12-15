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


import json
import random
import uuid

from PySide6.QtCore import Qt, SignalInstance, QSize
from PySide6.QtWidgets import QTabWidget, QPushButton, QWidget, QHBoxLayout, QMessageBox, QDialog, QDialogButtonBox, \
    QLineEdit, QLabel, QVBoxLayout, QComboBox

from src.common.common_definition import RESPONSE_LOGIN_SUCCESS, FONT_SIZE_RANGE, set_session_widget_height, FONT_LIST, \
    BASE_DIR
from src.common.msg_code import LOGIN_CODE, REMOVE_SESSION_CODE, LLM_SERVER_URL_UPDATE_CODE
from src.view.page_widget.component_object.svg_icon import get_icon_from_svg
from src.view.page_widget.session_page_stack import SessionPageStack


class SettingDialog(QDialog):
    def __init__(self, to_backend_sig, parent=None):
        super().__init__(parent)
        self.to_backend_sig = to_backend_sig
        self.setWindowTitle("Settings")
        self.setModal(True)

        self.settings = SettingDialog.load_settings()
        # print('loaded settings: ', self.settings)

        self.llm_server_label = QLabel(self)
        self.llm_server_label.setText("LLM Server Address:")
        self.llm_server_address_input = QLineEdit(self)
        self.llm_server_address_input.setText(self.settings.get('llm_server', ''))
        self.llm_server_address_input.textChanged.connect(self.setting_changed)

        self.llm_server_port_label = QLabel(self)
        self.llm_server_port_label.setText("LLM Server Port:")
        self.llm_server_port_input = QLineEdit(self)
        self.llm_server_port_input.setText(str(self.settings.get('llm_port', '')))
        self.llm_server_port_input.textChanged.connect(self.setting_changed)

        self.shell_font_label = QLabel(self)
        self.shell_font_label.setText("Shell Font(effect after restart):")
        self.shell_font_combobox = QComboBox(self)
        current_font = self.settings.get('font', '')
        self.shell_font_combobox.addItems(FONT_LIST)
        self.shell_font_combobox.setCurrentText(current_font)
        self.shell_font_combobox.currentTextChanged.connect(self.setting_changed)

        self.shell_font_size_label = QLabel(self)
        self.shell_font_size_label.setText("Shell Font Size(effect after restart):")
        self.shell_font_size_combobox = QComboBox(self)
        self.shell_font_size_combobox.addItems([str(x) for x in FONT_SIZE_RANGE])
        self.shell_font_size_combobox.setCurrentText(str(self.settings.get('font_size', '')))
        self.shell_font_size_combobox.currentTextChanged.connect(self.setting_changed)

        # Dialog buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)

        layout = QVBoxLayout()
        layout.addWidget(self.shell_font_label)
        layout.addWidget(self.shell_font_combobox)
        layout.addWidget(self.shell_font_size_label)
        layout.addWidget(self.shell_font_size_combobox)
        layout.addSpacing(20)
        layout.addWidget(self.llm_server_label)
        layout.addWidget(self.llm_server_address_input)
        layout.addWidget(self.llm_server_port_label)
        layout.addWidget(self.llm_server_port_input)

        layout.addStretch()
        layout.addWidget(self.button_box)

        self.setStyleSheet('''
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                font-size: 13px;
            }
            QLineEdit {
                border: none;
                height: 30px;
                border-radius: 15px;
                background-color: #EAEAEA;
                font-family: Arial;
                font-size: 13px;
                padding-left: 10px;
            }
            QDialogButtonBox QPushButton {
                color: #105315;
                background: #EAEAEA;
                border: none;
                width: 60px;
                height: 30px;
                border-radius: 15px;
            }
            QDialogButtonBox QPushButton:hover {
                background: #96E858;
            }
        ''')

        self.setLayout(layout)

    def accept(self) -> None:
        try:
            int(self.llm_server_port_input.text().strip())
        except ValueError as e:
            QMessageBox.warning(self, "error", str(e))
            return

        self.save_settings()
        super().accept()

    def reject(self) -> None:
        super().reject()

    @staticmethod
    def load_settings() -> dict:
        with open(BASE_DIR / "settings.json", "r") as settings_file:
            settings = json.load(settings_file)
        return settings

    def save_settings(self):
        settings = {
            "llm_server": self.llm_server_address_input.text().strip(),
            "llm_port": int(self.llm_server_port_input.text().strip()),
            "font": self.shell_font_combobox.currentText().strip(),
            "font_size": int(self.shell_font_size_combobox.currentText().strip()),
        }
        self.to_backend_sig.emit(
            {
                'msg_code': LLM_SERVER_URL_UPDATE_CODE,
                'payload': {'llm_server': settings['llm_server'], 'llm_port': settings['llm_port']}
            }
        )
        with open(BASE_DIR / "settings.json", "w") as settings_file:
            json.dump(settings, settings_file, indent=4)

    def setting_changed(self):
        llm_server = self.llm_server_address_input.text().strip()
        llm_port = int(self.llm_server_port_input.text().strip())
        font = self.shell_font_combobox.currentText().strip()
        font_size = int(self.shell_font_size_combobox.currentText().strip())

        is_setting_changed = True
        if llm_server == self.settings.get('llm_server', '') and \
                llm_port == self.settings.get('llm_port', '') and \
                font == self.settings.get('font', '') and \
                font_size == self.settings.get('font_size', ''):
            is_setting_changed = False

        if is_setting_changed:
            self.ok_button.setStyleSheet("""
                 QPushButton{
                     color: #105315;
                     background: #96E858;
                     border: none;
                     width: 60px;
                     height: 30px;
                     border-radius: 15px;
                 }
                 QPushButton:hover{
                     background: #7ad63c;
                 }
             """)
            return

        self.ok_button.setStyleSheet("""
            QDialogButtonBox QPushButton {
                color: #105315;
                background: #EAEAEA;
                border: none;
                width: 60px;
                height: 30px;
                border-radius: 15px;
            }
            QDialogButtonBox QPushButton:hover {
                background: #96E858;
            }""")


class SessionTabWidget(QTabWidget):
    HOME_TAB_TITLE = '*new session*'
    TAB_ICONS = [
        0x1f603,  # 😃
        0x1f609,  # 😉
        0x1f60b,  # 😋
        0x1f300,  # 🌀
        0x1f302,  # 🌂
        0x1f30f,  # 🌏
        0x1f32d,  # 🌭
        0x1f32e,  # 🌮
        0x1f32f,  # 🌯
        0x1f332,  # 🌲
        0x1f333,  # 🌳
        0x1f334,  # 🌴
        0x1f335,  # 🌵
        0x1f33d,  # 🌽
        0x1f345,  # 🍅
        0x1f346,  # 🍆
        0x1f349,  # 🍉
        0x1f34a,  # 🍊
        0x1f34b,  # 🍋
        0x1f34d,  # 🍍
        0x1f34e,  # 🍎
        0x1f34f,  # 🍏
        0x1f350,  # 🍐
        0x1f351,  # 🍑
        0x1f352,  # 🍒
        0x1f353,  # 🍓
        0x1f354,  # 🍔
        0x1f355,  # 🍕
        0x1f357,  # 🍗
        0x1f35b,  # 🍛
        0x1f35c,  # 🍜
        0x1f35d,  # 🍝
        0x1f35e,  # 🍞
        0x1f35f,  # 🍟
        0x1f363,  # 🍣
        0x1f36d,  # 🍭
        0x1f383,  # 🎃
        0x1f384,  # 🎄
        0x1f3c8,  # 🏈
        0x1f3c0,  # 🏀
        0x1f3d0,  # 🏐
        0x1f3d3,  # 🏓
        0x1f4a1,  # 💡
        0x1f3af,  # 🎯
        0x1f9a2,  # 🦢
        0x1f996,  # 🦖
        0x1f98b,  # 🦋
        0x1f373,  # 🍳
        0x1f9ed,  # 🧭
        0x1f9e2,  # 🧢
        0x1f9c0,  # 🧀
        0x1f955,  # 🥕
        0x1f9f2,  # 🧲
        0x1f99a,  # 🦚
    ]

    def __init__(self, to_backend_signal: SignalInstance):
        super().__init__()
        self.to_backend_signal = to_backend_signal

        self.setTabsClosable(True)
        self.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                border: none;
                padding: 5px 10px;
                margin: 0;
                min-height: 30px;
                min-width: 100px;
                max-width: 200px;
                background: white;
                color: #3e3e3e;
                border-bottom: 3px solid #bebebe;
                font-size: 15px;
                font-family: Arial;
            }
            QTabBar::tab:selected {
                border-bottom: 3px solid #3B85D5;
                background: #C3E5FF;
                color: #0A56A7;
            }
            QTabBar::tab:hover:!selected {
                border-bottom: 3px solid #6e6e6e;
                background: white;
                color: #3e3e3e;
            }
            QTabBar::scroller {
                width: 25px;
                height: 10px;
            }
            QTabBar::close-button {
                subcontrol-position: right;
            }""")
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        self.setElideMode(Qt.TextElideMode.ElideRight)
        self.tabCloseRequested.connect(self.on_tab_close_requested)
        self.currentChanged.connect(self.on_tab_changed)

        corner_widget = QWidget()
        corner_layout = QHBoxLayout()
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.setSpacing(0)

        setting_svg_icon = '''<svg width="64" height="64" viewBox="0 0 64 64"
     xmlns="http://www.w3.org/2000/svg">
  <!-- 6 个规则矩形齿 -->
  <!-- 齿根半径约 17，齿高约 6，齿宽 4 -->
  <!-- 矩形中心放在 x = 30, y = 9，之后绕 (32,32) 旋转 -->
  <g fill="#4CAF50" stroke="#4CAF50" stroke-width="2">
    <!-- 齿 0 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(0 32 32)"/>
    <!-- 齿 1 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(60 32 32)"/>
    <!-- 齿 2 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(120 32 32)"/>
    <!-- 齿 3 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(180 32 32)"/>
    <!-- 齿 4 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(240 32 32)"/>
    <!-- 齿 5 -->
    <path d="M 27 8 L 37 8 L 39 18 L 25 18 Z"
          transform="rotate(300 32 32)"/>
  </g>
  <!-- 齿轮外圆轮廓 -->
  <circle cx="32" cy="32" r="18"
          fill="#4CAF50"
          stroke="#4CAF50"
          stroke-width="2"/>
  <!-- 内孔 -->
  <circle cx="32" cy="32" r="8"
          fill="#ffffff"
          stroke="#4CAF50"
          stroke-width="2"/>
</svg>'''

        self.setting_button = QPushButton()
        self.setting_button.setIcon(get_icon_from_svg(setting_svg_icon))
        self.setting_button.setStyleSheet("""
            QPushButton{
                font-size: 16px;
                border: none;
                width: 30px;
                height: 30px;
                border-radius: 5px;
                margin-right: 1px;
                margin-left: 1px;
                margin-top: 6px;
                margin-bottom: 2px;
            }
            QPushButton:hover{
                background: #d0d0d0;
            }""")
        self.setting_button.setIconSize(QSize(23, 23))
        self.setting_button.clicked.connect(self.open_settings_dialog)

        add_svg_icon = '''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
          <!-- Tab 背景 -->
          <rect x="4" y="20" width="56" height="35" rx="4" ry="4"
                fill="#ffffff" stroke="#6c6f73" stroke-width="1.5"/>
          <!-- Tab 顶部突出部分（整体偏左一些） -->
          <path d="M4 20 L10 12 L38 12 L45 20 Z"
                fill="#C8E8FF" stroke="#6c6f73" stroke-width="1.5"/>

          <!-- 中间加号 -->
          <!-- 竖线 -->
          <rect x="31" y="30" width="2" height="18" fill="#6c6f73" />
          <!-- 横线 -->
          <rect x="22" y="38" width="20" height="2" fill="#6c6f73" />
        </svg>'''
        self.add_button = QPushButton()
        self.add_button.setIcon(get_icon_from_svg(add_svg_icon))
        self.add_button.setStyleSheet("""
            QPushButton{
                font-size: 16px;
                border: none;
                width: 30px;
                height: 30px;
                border-radius: 5px;
                margin-right: 1px;
                margin-left: 1px;
                margin-top: 6px;
                margin-bottom: 2px;
            }
            QPushButton:hover{
                background: #d0d0d0;
            }""")
        self.add_button.setIconSize(QSize(23, 23))
        self.add_button.clicked.connect(self.add_new_tab)

        llm_chat_svg_icon = """<?xml version="1.0" encoding="UTF-8"?>
        <svg width="64" height="64" viewBox="0 0 64 64"
             xmlns="http://www.w3.org/2000/svg">

          <defs>
            <!-- 主渐变：蓝 -> 青 -> 紫 -->
            <linearGradient id="starGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%"   stop-color="#4C7DFF"/>
              <stop offset="50%"  stop-color="#17C4FF"/>
              <stop offset="100%" stop-color="#9B6BFF"/>
            </linearGradient>

            <!-- 环形发光渐变，用于主星背景光晕 -->
            <radialGradient id="glowGradient" cx="50%" cy="40%" r="50%">
              <stop offset="0%"   stop-color="#17C4FF" stop-opacity="0.45"/>
              <stop offset="60%"  stop-color="#4C7DFF" stop-opacity="0.0"/>
              <stop offset="100%" stop-color="#4C7DFF" stop-opacity="0.0"/>
            </radialGradient>

            <!-- 轻微阴影 -->
            <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="1.2" result="blur"/>
              <feOffset in="blur" dx="0" dy="1.2" result="offsetBlur"/>
              <feMerge>
                <feMergeNode in="offsetBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          <!-- 背景透明，如需白底可用 rect 填充 -->
          <!-- 主星光背景光晕 -->
          <circle cx="38" cy="26" r="16" fill="url(#glowGradient)" />

          <!-- 主星：稍大的四角星（菱形十字） -->
          <g filter="url(#softShadow)">
            <!-- 外层星形轮廓 -->
            <path d="
              M 38 12
              L 41.5 21.5
              L 52 24
              L 41.5 26.5
              L 38 36
              L 34.5 26.5
              L 24 24
              L 34.5 21.5
              Z
            " fill="none"
               stroke="url(#starGradient)"
               stroke-width="2.4"
               stroke-linejoin="round"
            />

            <!-- 内层小菱形，增强层次 -->
            <path d="
              M 38 17
              L 42.5 24
              L 38 31
              L 33.5 24
              Z
            " fill="none"
               stroke="url(#starGradient)"
               stroke-width="1.6"
               stroke-linejoin="round"
            />
          </g>

          <!-- 左侧小星 -->
          <g filter="url(#softShadow)">
            <path d="
              M 18 30
              L 20 35
              L 25 37
              L 20 39
              L 18 44
              L 16 39
              L 11 37
              L 16 35
              Z
            " fill="none"
               stroke="url(#starGradient)"
               stroke-width="1.5"
               stroke-linejoin="round"
            />
          </g>

          <!-- 右下小星 -->
          <g filter="url(#softShadow)">
            <path d="
              M 44 40
              L 45.8 44
              L 50 45.5
              L 45.8 47
              L 44 51
              L 42.2 47
              L 38 45.5
              L 42.2 44
              Z
            " fill="none"
               stroke="url(#starGradient)"
               stroke-width="1.4"
               stroke-linejoin="round"
            />
          </g>
        </svg>
        """

        self.llm_chat_button = QPushButton()
        self.llm_chat_button.setIcon(get_icon_from_svg(llm_chat_svg_icon))
        self.llm_chat_button.setStyleSheet("""
            QPushButton{
                border: none;
                width: 32px;
                height: 32px;
                border-radius: 5px;
                margin-right: 1px;
                margin-left: 1px;
                margin-top: 6px;
                margin-bottom: 2px;
            }
            QPushButton:hover{
                background: #d0d0d0;
            }""")
        self.llm_chat_button.setIconSize(QSize(23, 23))
        self.llm_chat_button.clicked.connect(self.toggle_current_tab_chat)

        corner_layout.addWidget(self.setting_button)
        corner_layout.addWidget(self.add_button)
        corner_layout.addWidget(self.llm_chat_button)

        corner_widget.setLayout(corner_layout)
        self.setCornerWidget(corner_widget)

        self.session_page_map = {}
        self.add_new_tab()

    def init_session_widget_height(self):
        # total height
        total_height = self.height()
        tab_bar_height = self.tabBar().height() if self.tabBar() is not None else 0
        available_h = max(0, total_height - tab_bar_height)

        set_session_widget_height(available_h)

    def open_settings_dialog(self):
        dialog = SettingDialog(self.to_backend_signal, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.",
                                    QMessageBox.StandardButton.Ok)

    def add_new_tab(self):
        session_id = str(uuid.uuid4())
        page_stack = SessionPageStack(session_id)
        page_stack.SIG_COMMAND.connect(self.transmit_page_stack_sig, type=Qt.ConnectionType.DirectConnection)

        self.session_page_map.update({session_id: page_stack})
        self.add_tab(SessionTabWidget.HOME_TAB_TITLE, page_stack)

    def add_tab(self, title, widget):
        index = self.addTab(widget, title)
        self.setCurrentIndex(index)

    def on_tab_close_requested(self, index):
        page_stack = self.widget(index)
        if isinstance(page_stack, SessionPageStack):
            session_id = page_stack.session_id
            if session_id in self.session_page_map:
                del self.session_page_map[session_id]
            page_stack.deleteLater()
            remove_msg = {
                'msg_code': REMOVE_SESSION_CODE,
                'payload': {
                    'session_id': session_id,
                }
            }
            self.to_backend_signal.emit(remove_msg)
        self.removeTab(index)
        if self.count() == 0:
            self.add_new_tab()

    def on_tab_changed(self, index):
        # print(f'on_tab_changed: index={index}')
        if index == -1:
            return

        widget = self.widget(index)
        if isinstance(widget, SessionPageStack):
            widget.set_focus()
            # title = self.tabText(index)
            # print(title, widget.session_id)

    def handle_login_rsp_msg(self, msg_payload: dict):
        session_id = msg_payload.get('session_id')
        page_stack: SessionPageStack = self.session_page_map.get(session_id)
        if page_stack is None:
            return

        content = msg_payload.get('content', {})
        login_result = content.get('result')
        if login_result != RESPONSE_LOGIN_SUCCESS:
            QMessageBox.warning(self, "Login Failed", f"login result: {login_result}")
            page_stack.login_page.reset_login_state()
            return
        page_stack.turn_2_session_page()

    def update_current_tab_title(self, title: str):
        tab_index = self.currentIndex()
        if tab_index != -1:
            self.setTabText(tab_index, title)

    def transmit_page_stack_sig(self, msg: dict):
        msg_code = msg.get('msg_code')
        if msg_code == LOGIN_CODE:
            host_name = msg.get('payload', {}).get('content', {}).get('hostname')
            icon_str = chr(random.choice(SessionTabWidget.TAB_ICONS))
            self.update_current_tab_title(icon_str + ' ' * 3 + host_name + ' ' * 3)
        self.to_backend_signal.emit(msg)

    def update_session_text_browser(self, msg_list: list):
        for msg in msg_list:
            if session_id := msg.get('session_id'):
                page_stack: SessionPageStack = self.session_page_map.get(session_id)
                if page_stack is None:
                    continue
                page_stack.update_text_browser(msg)

    def update_session_llm_chat_widget(self, msg_code, msg_payload: dict):
        if session_id := msg_payload.get('session_id'):
            page_stack: SessionPageStack = self.session_page_map.get(session_id)
            if page_stack is None:
                return
            page_stack.update_session_llm_widget(msg_code, msg_payload)

    def toggle_current_tab_chat(self):
        current_index = self.currentIndex()
        if current_index >= 0:
            page_stack = self.widget(current_index)
            if isinstance(page_stack, SessionPageStack) and page_stack.session_page:
                page_stack.session_page.toggle_chat_widget()
                return
