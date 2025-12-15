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


import queue
import time
from multiprocessing import Process, Event
from multiprocessing.connection import Connection
from threading import Thread
from typing import Dict, Optional, Callable

from src.common.common_definition import RESPONSE_LOGIN_SUCCESS, get_llm_url
from src.common.msg_code import LOGIN_RSP_CODE, LOGIN_CODE, USER_COMMAND_CODE, LLM_ASK_CODE, \
    LLM_MODEL_CHECK, SESSION_STRING_CODE, SESSION_VIEW_CONTENT_CODE, SCROLL_WINDOW_CODE, LLM_MODEL_LIST_CODE, \
    LLM_ANSWER_CODE, LLM_CHAT_HISTORY_REQ_CODE, LLM_CHAT_HISTORY_RSP_CODE, REMOVE_SESSION_CODE, REMOVE_AGENT_CODE, \
    LLM_THREAD_STOP, LLM_INLINE_MODEL_CHECK, LLM_INLINE_MODEL_LIST_CODE, LLM_INLINE_ASK_CODE, \
    LLM_LOAD_CHAT_BY_HISTORY_IDX, \
    LLM_RSP_CHAT_BY_CHAT_ID, SESSION_INACTIVE_CODE, LLM_SERVER_URL_UPDATE_CODE, RECONNECT_SHELL_FAIL_CODE, \
    LLM_NEW_CHAT_CODE
from src.controller.llm_client import LlmClient
from src.controller.session_document import SessionDocument
from src.model.sync_ssh.remote_agent.remote_agent import RemoteAgent


class RemoteAgentRouter:
    def __init__(self):
        self.__agent_map: Dict[tuple, tuple] = {}  # agent_key: (recv_queue, agent)
        self.__session_2_agent_map: Dict[str, tuple] = {}  # session_id: (recv_queue, agent_key)

    def get_remote_agent(self, agent_key: tuple) -> Optional[RemoteAgent]:
        if item := self.__agent_map.get(agent_key):
            return item[1]

        return None

    def add_agent(self, agent_key: tuple, session_id: str, recv_queue, agent: RemoteAgent):
        self.__agent_map[agent_key] = (recv_queue, agent)
        self.__session_2_agent_map[session_id] = (recv_queue, agent_key)

    def map_session_id_2_agent_queue(self, agent_key: tuple, session_id: str):
        item = self.__agent_map.get(agent_key)
        if item:
            recv_queue, _ = item
            self.__session_2_agent_map[session_id] = (recv_queue, agent_key)

    def get_agent_queue(self, session_id: str) -> Optional[queue.Queue]:
        if item := self.__session_2_agent_map.get(session_id):
            return item[0]

        return None

    def remove_session_mapping(self, session_id: str):
        item = self.__session_2_agent_map.pop(session_id, None)
        if item:
            session_agent_key = item[1]

            for x in self.__session_2_agent_map.values():
                if x[1] == session_agent_key:
                    return

            # 当agent没有任何session映射时，关闭agent
            item = self.__agent_map.get(session_agent_key)
            if item:
                RemoteAgentRouter.notify_agent_close(*item)
            self.__agent_map.pop(session_agent_key, None)
            return

    def close_all_agent(self):
        for item in self.__agent_map.values():
            RemoteAgentRouter.notify_agent_close(*item)

    @staticmethod
    def notify_agent_close(agent_queue, agent: RemoteAgent):
        agent_queue.put(
            {
                'msg_code': REMOVE_AGENT_CODE,
                'payload': {}
            }
        )
        agent.join()


class MainController(Process):
    PERIOD_SLEEP_SECS = 0.05

    # 消息透传msg code 列表
    PASS_THROUGH_MSG_CODES = [
        LOGIN_RSP_CODE, LLM_MODEL_LIST_CODE, LLM_ANSWER_CODE, LLM_CHAT_HISTORY_RSP_CODE, LLM_INLINE_MODEL_LIST_CODE,
        LLM_RSP_CHAT_BY_CHAT_ID
    ]

    def __init__(self, bk_side: Connection):
        super().__init__()
        self.__bk_side = bk_side
        self.__agent_router = RemoteAgentRouter()
        self.__sink_queue = None
        self.__llm_query_queue = None
        self.__session_document_map: Dict[str, SessionDocument] = dict()
        self.__remote_msg_handler_method_map: Dict[int, Callable] = {
            LOGIN_RSP_CODE: self.process_login_rsp_msg,
            SESSION_STRING_CODE: self.process_session_string_msg,
            SESSION_INACTIVE_CODE: self.process_session_inactive_msg,
            RECONNECT_SHELL_FAIL_CODE: self.process_reconnect_shell_fail_msg,
        }
        self.__front_handle_thread: Optional[Thread] = None
        self.__llm_client_thread: Optional[LlmClient] = None
        self.__proces_stop_event = Event()

    def stop(self):
        print("set stop event for RemoteAgentsManager.")
        self.__proces_stop_event.set()

    def run(self):
        print("RemoteAgentsManager start running.")
        self.__sink_queue = queue.Queue()
        self.__llm_query_queue = queue.Queue()

        self.__front_handle_thread = Thread(target=self.__handle_msg_from_front)
        self.__front_handle_thread.start()

        llm_service_url = get_llm_url()
        self.__llm_client_thread = LlmClient(
            llm_service_url=llm_service_url, query_queue=self.__llm_query_queue,
            response_queue=self.__sink_queue
        )
        self.__llm_client_thread.start()

        while not self.__proces_stop_event.is_set():
            self.process_msg_from_sink_queue(max_read_msg_count=20)

            if view_update_contents := self.flush_view_update_contents():
                if not self.__bk_side.closed:
                    self.__bk_side.send(view_update_contents)

            time.sleep(MainController.PERIOD_SLEEP_SECS)

        if self.__llm_client_thread:
            self.__llm_query_queue.put({'msg_code': LLM_THREAD_STOP, 'payload': {}})
            self.__llm_client_thread.join()

        if self.__front_handle_thread:
            self.__front_handle_thread.join()

        if self.__bk_side and not self.__bk_side.closed:
            self.__bk_side.close()

        self.__agent_router.close_all_agent()
        print("MainController stop success.")

    def process_msg_from_sink_queue(self, max_read_msg_count: int):
        msg_count = 0
        while not self.__sink_queue.empty() and msg_count < max_read_msg_count:
            try:
                msg = self.__sink_queue.get_nowait()
            except Exception as e:
                break
            msg_count += 1
            view_update_msg = self.process_session_remote_msg(msg)
            if view_update_msg and not self.__bk_side.closed:
                self.__bk_side.send(view_update_msg)

    def process_session_remote_msg(self, msg: dict) -> dict | None:
        msg_code = msg.get('msg_code')
        handler_method = self.__remote_msg_handler_method_map.get(msg_code)

        result = None
        if handler_method:
            result = handler_method(msg)

        if msg_code in MainController.PASS_THROUGH_MSG_CODES:
            return msg

        return result

    def process_login_rsp_msg(self, msg: dict):
        payload = msg.get('payload')

        session_id = payload.get('session_id')
        login_result = payload.get('content', {}).get('result', 'fail')
        if login_result == RESPONSE_LOGIN_SUCCESS:
            page_line_count = payload.get('content', {}).get('page_line_count', 0)
            self.__session_document_map[session_id] = SessionDocument(page_line_count)
        return msg

    def process_session_string_msg(self, msg: dict) -> None:
        payload = msg.get('payload')
        for session_msg in payload:
            session_id = session_msg.get('session_id')
            if session_document := self.__session_document_map.get(session_id):
                session_document.handle_msgs(session_msg.get('inner_msgs', []))

    def process_session_inactive_msg(self, msg: dict) -> None:
        payload = msg.get('payload', {})
        session_id = payload.get('session_id')
        if session_document := self.__session_document_map.get(session_id):
            session_document.insert_session_fail_msg('session is disconnected. Press \'r\' to reconnect.')

    def process_reconnect_shell_fail_msg(self, msg: dict) -> None:
        payload = msg.get('payload', {})
        session_id = payload.get('session_id')
        if session_document := self.__session_document_map.get(session_id):
            session_document.insert_session_fail_msg(
                'reconnect shell failed. Please check network or server status, and Press \'r\' to retry.'
            )

    def flush_view_update_contents(self) -> dict:
        update_view_contents = []
        for session_id, session_document in self.__session_document_map.items():
            if current_content := session_document.view_area_content:
                view_area_max_row = session_document.get_max_row()
                update_view_contents.append(
                    {
                        'session_id': session_id,
                        'view_area': {
                            'view_area_content': current_content,
                            'cursor_pos': session_document.cursor_pos if session_document.is_stick_to_bottom() else None
                        },
                        'scroll_info': {
                            'total_lines': session_document.total_lines,
                            'visible_lines': min(view_area_max_row, session_document.total_lines),
                            'first_visible_line': max(
                                1, session_document.window_bottom_line_number - view_area_max_row + 1),
                            'hide_scrollbar': session_document.total_lines <= view_area_max_row
                        }
                    }
                )

        return {
            'msg_code': SESSION_VIEW_CONTENT_CODE,
            'payload': update_view_contents
        } if update_view_contents else None

    def __handle_msg_from_front(self):
        while True:
            try:
                msg = self.__bk_side.recv()
            except (EOFError, OSError, ValueError):
                print('Front connection closed, stop handling messages from front.')
                break

            msg_code = msg.get('msg_code')

            if msg_code == LOGIN_CODE:
                self.process_login_msg(msg)
                continue

            if msg_code == USER_COMMAND_CODE:
                self.process_user_command(msg)
                continue

            if msg_code == REMOVE_SESSION_CODE:
                self.remove_session(msg)
                continue

            if msg_code == SCROLL_WINDOW_CODE:
                self.process_scroll_window(msg)
                continue

            if msg_code in [LLM_ASK_CODE, LLM_MODEL_CHECK, LLM_CHAT_HISTORY_REQ_CODE, LLM_INLINE_MODEL_CHECK,
                            LLM_INLINE_ASK_CODE, LLM_LOAD_CHAT_BY_HISTORY_IDX, LLM_SERVER_URL_UPDATE_CODE,
                            LLM_NEW_CHAT_CODE]:
                self.__llm_query_queue.put(msg)
                continue

    def process_scroll_window(self, msg: dict):
        payload = msg.get('payload')
        session_id = payload.get('session_id')
        scroll_req = payload.get('content', {})
        if session_document := self.__session_document_map.get(session_id):
            session_document.add_ui_scroll_req(scroll_req)

    def process_login_msg(self, msg: dict):
        # print(f'process login msg')
        login_content = msg.get('payload').get('content', {})
        session_id = msg.get('payload').get('session_id')

        agent_key = (
            login_content.get('hostname'),
            login_content.get('port'),
            login_content.get('username'),
            login_content.get('password', ''),
        )

        remote_agent = self.__agent_router.get_remote_agent(agent_key)
        if not remote_agent:
            self.start_new_remote_agent(login_content, agent_key, session_id)
        else:
            self.__agent_router.map_session_id_2_agent_queue(agent_key, session_id)

        if agent_recv_queue := self.__agent_router.get_agent_queue(session_id):
            agent_recv_queue.put(msg)

    def start_new_remote_agent(self, login_content, agent_key, session_id):
        connect_params = {
            'hostname': login_content.get('hostname'),
            'port': login_content.get('port', 22),
            'username': login_content.get('username'),
            'password': login_content.get('password', ''),
        }
        client, result = RemoteAgent.get_client(connect_params)
        if client is None:
            self.__sink_queue.put(
                {
                    'msg_code': LOGIN_RSP_CODE,
                    'payload': {
                        'session_id': session_id,
                        'content': {'result': result},
                    }
                }
            )
            return

        recv_queue = queue.Queue()
        remote_agent = RemoteAgent(client, recv_queue, self.__sink_queue)
        self.__agent_router.add_agent(agent_key, session_id, recv_queue, remote_agent)
        remote_agent.start()

    def process_user_command(self, msg: dict):
        session_id = msg.get('payload', {}).get('session_id')
        if agent_recv_queue := self.__agent_router.get_agent_queue(session_id):
            agent_recv_queue.put(msg)
        content = msg.get('payload', {}).get('content', {})
        if 'command' in content:
            if session_document := self.__session_document_map.get(session_id):
                session_document.set_stick_to_bottom(True)

    def remove_session(self, msg: dict):
        session_id = msg.get('payload', {}).get('session_id')
        if agent_recv_queue := self.__agent_router.get_agent_queue(session_id):
            agent_recv_queue.put(msg)

        self.__agent_router.remove_session_mapping(session_id)
