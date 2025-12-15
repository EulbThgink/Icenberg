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
import os
import platform
from pathlib import Path

INLINE_CHAT_ID = 'inline_chat_id'
SIDE_CHAT_ID = 'side_chat_id'
RESPONSE_LOGIN_SUCCESS = 'success'


def get_os_type():
    return platform.system().lower()


OS_TYPE = get_os_type()
VIEW_WIDTH = 210
SESSION_WIDGET_HEIGHT = 0

BASE_DIR = Path(__file__).resolve().parent.parent


def set_session_widget_height(height: int):
    global SESSION_WIDGET_HEIGHT
    SESSION_WIDGET_HEIGHT = height


def get_session_widget_height():
    return SESSION_WIDGET_HEIGHT


def get_shell_font_setting():
    with open(BASE_DIR / 'settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
        font_family = settings.get('font', 'Courier New')
        font_size = settings.get('font_size', 13)
        return font_family, font_size


def get_llm_url():
    with open(BASE_DIR / 'settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)
        llm_server = settings.get('llm_server', 'localhost')
        llm_port = settings.get('llm_port', 11434)
        return f'http://{llm_server}:{llm_port}'


FONT_SIZE_RANGE = [8, 9, 10, 11, 12, 13]
FONT_LIST = ['Courier New', 'Monaco', 'Andale Mono', 'PT Mono', 'Menlo'] if OS_TYPE == 'darwin' else ['Courier New']
