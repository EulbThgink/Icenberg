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
from datetime import datetime
from queue import Queue, Empty
from threading import Thread
from typing import Dict

import requests

from src.common.common_definition import INLINE_CHAT_ID, SIDE_CHAT_ID, BASE_DIR
from src.common.msg_code import LLM_ANSWER_CODE, LLM_ASK_CODE, LLM_MODEL_CHECK, LLM_MODEL_LIST_CODE, \
    LLM_CHAT_HISTORY_RSP_CODE, LLM_CHAT_HISTORY_REQ_CODE, LLM_THREAD_STOP, LLM_INLINE_MODEL_CHECK, \
    LLM_INLINE_MODEL_LIST_CODE, LLM_INLINE_ASK_CODE, LLM_LOAD_CHAT_BY_HISTORY_IDX, LLM_RSP_CHAT_BY_CHAT_ID, \
    LLM_SERVER_URL_UPDATE_CODE, LLM_NEW_CHAT_CODE


class LlmClient(Thread):
    LLM_QUEUE_GET_TIMEOUT = 0.1
    INLINE_CHAT_SYSTEM_ROLE = {
        'role': 'system',
        'content': '''
你是一个集成在交互式shell中的AI专家，能够帮助用户理解和操作shell环境。
要求:
- 当用户提出问题时，结合shell的当前状态和内容进行回答。
- 你会收到用户的问题(inline_ask), 当前屏幕的完整内容文本(shell_content_text), 用户关注的特定区域文本(shell_focus_text)
- 如果shell_focus_text内容不是空，优先使用shell_focus_text中的信息来回答用户的问题。
- 如果需要并且shell_content_text内容不是空，则尝试从shell_content_text中寻找答案。
- 如果原始信息不足以回答用户的问题，礼貌地提示用户提供更多细节。
- 使用中文回答用户的问题。'''
    }
    CHAT_SYSTEM_ROLE = {
        'role': 'system',
        'content': '''
你是一个集成在交互式shell中的AI专家，能够帮助用户理解和操作shell环境。
要求:
- 当用户提出问题时，结合shell的当前状态和内容进行回答。
- 你会收到用户的问题(llm_ask), 当前屏幕的完整内容文本(shell_content_text)
- 如果需要并且shell_content_text内容不是空，则尝试从shell_content_text中寻找答案。
- 如果原始信息不足以回答用户的问题，礼貌地提示用户提供更多细节。
- 使用中文回答用户的问题。'''
    }

    def __init__(self, llm_service_url: str, query_queue: Queue, response_queue: Queue):
        super().__init__()
        self.__query_queue = query_queue
        self.__response_queue = response_queue
        self.__llm_service_url = llm_service_url
        self.__session_chat_record_map: Dict[str, dict] = {}
        self.__history_chat_records: list[dict] = []
        self.__llm_api_map = {
            'chat': {
                'ollama': '/api/chat',
            },
            'generate': {
                'ollama': '/api/generate'
            },
            'model_check': {
                'ollama': '/api/ps'
            }
        }
        self.load_chat_record()

    def clear_chat_record(self, session_id, chat_id):
        session_chat_record_map = self.__session_chat_record_map.setdefault(session_id, {})
        session_chat_record_map[chat_id] = {
            'message_list': [],
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'chat_id': chat_id
        }

    def get_chat_record(self, session_id, chat_id):
        record = self.__session_chat_record_map.setdefault(session_id, {}).setdefault(chat_id, {})
        if not record:
            record['message_list'] = []
            record['start_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            record['chat_id'] = chat_id

        return record

    def pop_history_chat_record_by_idx(self, history_idx):
        if history_idx < 0 or history_idx >= len(self.__history_chat_records):
            return None
        return self.__history_chat_records.pop(history_idx)

    def move_current_chat_record_to_history(self, session_id):
        session_records = self.__session_chat_record_map.get(session_id, {})
        old_chat_record = session_records.get(SIDE_CHAT_ID)
        if not old_chat_record:
            return

        self.__history_chat_records.append(old_chat_record)
        self.clear_chat_record(session_id, SIDE_CHAT_ID)

    def generate_new_message_list(self, session_id, chat_id, message, org_user_msg, system_role: dict):
        record = self.get_chat_record(session_id, chat_id)
        message_list = record.setdefault('message_list', [system_role])
        message_list.append({'role': 'user', 'content': message, 'org_user_msg': org_user_msg})
        return message_list

    def run(self):
        while True:
            try:
                user_query_msg = self.__query_queue.get()
            except Empty:
                continue

            msg_code = user_query_msg.get('msg_code')
            # print(f'LLM Client received message code: {msg_code}, query: {user_query_msg}')
            payload = user_query_msg.get('payload', {})
            session_id = payload.get('session_id')

            if msg_code == LLM_THREAD_STOP:
                self.store_chat_record()
                print('LLM Client stopped...')
                break

            if msg_code == LLM_ASK_CODE:
                content = user_query_msg.get('payload', {}).get('content', {})
                chat_session_id = content.get('chat_session_id')
                llm_ask = content.get('llm_ask')
                llm_model_name = content.get('llm_model_name')
                shell_content_text = content.get('shell_content_text')

                message = f"[llm_ask 用户的问题]\n{llm_ask}\n"
                if shell_content_text:
                    message += f"\n\n[shell_content_text 当前屏幕的完整内容]\n{shell_content_text}\n"

                message_list = self.generate_new_message_list(
                    session_id, SIDE_CHAT_ID, message, llm_ask, system_role=LlmClient.CHAT_SYSTEM_ROLE)
                self.send_user_chat_message_to_llm(session_id, chat_session_id, message_list, llm_model_name)
                continue

            if msg_code == LLM_MODEL_CHECK or msg_code == LLM_INLINE_MODEL_CHECK:
                # print(f'LLM model check for session {session_id}')
                self.send_model_check_request(session_id, msg_code)

                # LLM INLINE MODEL CHECK 是临时对话的起点，所以在这条消息做初始化
                if msg_code == LLM_INLINE_MODEL_CHECK:
                    self.clear_chat_record(session_id, INLINE_CHAT_ID)
                continue

            if msg_code == LLM_INLINE_ASK_CODE:
                content = user_query_msg.get('payload', {}).get('content', {})
                llm_model_name = content.get('llm_model_name')
                inline_ask_text = content.get('inline_ask')
                shell_focus_text = content.get('shell_focus_text', '')
                shell_content_text = content.get('shell_content_text', '')

                message = f"[inline_ask 用户的问题]\n{inline_ask_text}\n"
                if shell_content_text:
                    message += f"\n\n[shell_content_text 当前屏幕的完整内容]\n{shell_content_text}\n"
                if shell_focus_text:
                    message += f"\n\n[shell_focus_text 用户关注的特定区域文本]\n{shell_focus_text}\n"

                message_list = self.generate_new_message_list(
                    session_id, INLINE_CHAT_ID, message, inline_ask_text, system_role=LlmClient.INLINE_CHAT_SYSTEM_ROLE)
                self.send_user_chat_message_to_llm(session_id, INLINE_CHAT_ID, message_list, llm_model_name)
                continue

            if msg_code == LLM_CHAT_HISTORY_REQ_CODE:
                self.send_chat_history_to_ui(session_id)
                continue

            if msg_code == LLM_NEW_CHAT_CODE:
                self.move_current_chat_record_to_history(session_id)
                continue

            if msg_code == LLM_LOAD_CHAT_BY_HISTORY_IDX:
                history_idx = user_query_msg.get('payload', {}).get('content', {}).get('history_idx')
                self.load_history_chat(session_id, history_idx)
                continue

            if msg_code == LLM_SERVER_URL_UPDATE_CODE:
                server_info = user_query_msg.get('payload', {})
                self.__llm_service_url = f"http://{server_info.get('llm_server')}:{server_info.get('llm_port')}"

    def store_chat_record(self):
        for chat_record_map in self.__session_chat_record_map.values():
            for chat_id, chat_record in chat_record_map.items():
                if chat_id == SIDE_CHAT_ID:
                    self.__history_chat_records.append(chat_record)

        with open(BASE_DIR / 'chat_records.json', 'w', encoding='utf-8') as f:
            json.dump(self.__history_chat_records, f, ensure_ascii=False, indent=4)

    def load_chat_record(self):
        try:
            with open(BASE_DIR / 'chat_records.json', 'r', encoding='utf-8') as f:
                self.__history_chat_records = json.load(f)
        except Exception:
            self.__history_chat_records = []

    def load_history_chat(self, session_id, history_idx):
        chat_record = self.pop_history_chat_record_by_idx(history_idx)
        self.move_current_chat_record_to_history(session_id)
        if not chat_record:
            return
        self.update_chat_record(session_id, chat_record)
        self.__response_queue.put(
            {
                'msg_code': LLM_RSP_CHAT_BY_CHAT_ID,
                'payload': {
                    'session_id': session_id,
                    'content': chat_record
                }
            }
        )

    def update_chat_record(self, session_id, chat_record):
        session_records = self.__session_chat_record_map.setdefault(session_id, {})
        session_records[SIDE_CHAT_ID] = chat_record

    def send_model_check_request(self, session_id: str, check_msg_code: int):
        url = f"{self.__llm_service_url}{self.__llm_api_map['model_check']['ollama']}"
        respones_code = (
            LLM_INLINE_MODEL_LIST_CODE if check_msg_code == LLM_INLINE_MODEL_CHECK else LLM_MODEL_LIST_CODE)
        try:
            response = requests.get(url)
            response.raise_for_status()
            model_info = response.json()
            self.__response_queue.put(
                {
                    'msg_code': respones_code,
                    'payload': {
                        'session_id': session_id,
                        'content': model_info
                    }
                }
            )
        except Exception as e:
            print(e)
            self.__response_queue.put(
                {
                    'msg_code': respones_code,
                    'payload': {
                        'session_id': session_id,
                        'content': {'models': []}
                    }
                }
            )

    def send_chat_history_to_ui(self, session_id: str):
        chat_history_brief = []
        for idx, chat_record in enumerate(self.__history_chat_records):
            chat_start_time = chat_record.get('start_time', '')
            chat_message_list = chat_record.get('message_list', [])
            if not chat_message_list:
                continue
            first_message_info = chat_message_list[0]
            if first_message_info.get('role') != 'user':
                continue
            first_message = first_message_info.get('org_user_msg', '')
            chat_history_brief.append(
                {
                    'history_idx': idx,
                    'start_time': chat_start_time,
                    'first_message': first_message
                }
            )
        if not chat_history_brief:
            return

        self.__response_queue.put(
            {
                'msg_code': LLM_CHAT_HISTORY_RSP_CODE,
                'payload': {
                    'session_id': session_id,
                    'content': chat_history_brief
                }
            }
        )

    def send_user_chat_message_to_llm(self, session_id, chat_session_id, message_list, llm_model_name: str):
        data = {
            "model": llm_model_name,
            "messages": message_list,
            "stream": True,
        }

        full_response = ""
        url = f"{self.__llm_service_url}{self.__llm_api_map['chat']['ollama']}"
        try:
            response = requests.post(url, json=data, stream=True)
            response.raise_for_status()

            is_think = False
            is_explicit_think_label = False

            for line in response.iter_lines():
                if line:
                    try:
                        # 解析每行的JSON响应
                        json_response = json.loads(line.decode('utf-8'))
                        # print(f'\x1b[01;32mjson_response\x1b[0m: {json_response}')

                        message = json_response.get('message', {})
                        is_done = json_response.get('done', False)
                        if not message:
                            continue

                        content = message.get('content', '')
                        thinking_msg = message.get('thinking')

                        if not is_think:
                            if content == '<think>' or thinking_msg:
                                is_think = True
                                if thinking_msg:
                                    is_explicit_think_label = True
                                    msg = f'<think>\n\n{thinking_msg}'
                                else:
                                    msg = content
                            else:
                                msg = content
                        else:
                            if content == '</think>' or (is_explicit_think_label and not thinking_msg):
                                is_think = False
                                if is_explicit_think_label:
                                    msg = f'\n\n</think>\n\n{content}'
                                else:
                                    msg = content
                            else:
                                msg = content or thinking_msg

                        if is_done:
                            msg += '\n\n'

                        self.__response_queue.put(
                            {
                                'msg_code': LLM_ANSWER_CODE,
                                'payload': {
                                    'session_id': session_id,
                                    'chat_session_id': chat_session_id,
                                    'is_think': is_think,
                                    'content': msg,
                                    'is_done': is_done
                                }
                            }
                        )
                        full_response += msg

                    except json.JSONDecodeError:
                        continue
            assistant = {'role': 'assistant', 'content': full_response}
            message_list.append(assistant)
        except requests.exceptions.RequestException as e:
            print(f"\n请求错误: {e}")
            return
