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
import select
import socket
from threading import Thread, Event, Lock
from typing import Dict, Optional

from src.common.common_definition import RESPONSE_LOGIN_SUCCESS
from src.common.msg_code import SESSION_STRING_CODE, LOGIN_CODE, USER_COMMAND_CODE, REMOVE_SESSION_CODE, \
    REMOVE_AGENT_CODE, LOGIN_RSP_CODE, SESSION_INACTIVE_CODE, RECONNECT_SHELL_CODE, RECONNECT_SHELL_FAIL_CODE
from src.model.sync_ssh.ssh.ssh_client import XClient
from src.model.sync_ssh.ssh.ssh_shell import XShell


class NoActiveSessionsError(Exception):
    def __init__(self):
        super().__init__("No active sessions in RemoteAgent")


class RemoteAgent(Thread):
    def __init__(self, xclient: XClient, recv_queue: queue.Queue, sink_queue: queue.Queue):
        super().__init__()
        self.__xClient = xclient
        self.__recv_queue = recv_queue
        self.__sink_queue = sink_queue

        self.__x_shell_dict: Dict[str, XShell] = dict()
        self.__x_shell_dict_lock = Lock()
        self.__stop_event = Event()

        # wakeup self-pipe：用于打断阻塞的 select
        self.listener, self.notifier = socket.socketpair()
        self.listener.setblocking(False)
        self.notifier.setblocking(False)
        self.active_shell_count = 0

        self.__is_active = True
        self.__is_active_lock = Lock()

    @staticmethod
    def get_client(connect_params: dict) -> tuple:
        client = XClient()
        try:
            client.connect(**connect_params)
            client.set_connect_params(connect_params)
            return client, ''
        except Exception as e:
            client.close()
            del client
            return None, str(e)

    def is_active(self) -> bool:
        with self.__is_active_lock:
            return self.__is_active

    def set_active(self, is_active: bool):
        with self.__is_active_lock:
            self.__is_active = is_active

    def get_shell(self, session_id) -> Optional[XShell]:
        with self.__x_shell_dict_lock:
            return self.__x_shell_dict.get(session_id)

    def add_shell(self, session_id, x_shell: XShell):
        with self.__x_shell_dict_lock:
            self.__x_shell_dict[session_id] = x_shell

    def replace_shell_dict(self, new_shell_dict: Dict[str, XShell]):
        with self.__x_shell_dict_lock:
            self.__x_shell_dict = new_shell_dict

    def remove_shell(self, session_id) -> Optional[XShell]:
        with self.__x_shell_dict_lock:
            return self.__x_shell_dict.pop(session_id, None)

    def get_session_id_list(self):
        with self.__x_shell_dict_lock:
            return list(self.__x_shell_dict.keys())

    def get_active_shell_list(self):
        with self.__x_shell_dict_lock:
            return [shell for shell in self.__x_shell_dict.values() if not shell.is_closed()]

    def wakeup_listener(self):
        try:
            self.notifier.send(b'\x00')
        except Exception:
            pass

    def confirm_wakeup_signal(self):
        try:
            while self.listener.recv(1024):
                continue
        except BlockingIOError:
            pass
        except Exception:
            pass

    def get_recv_queue(self):
        return self.__recv_queue

    def run(self):
        front_msg_handler_thread = Thread(target=self.handle_front_msg)
        front_msg_handler_thread.start()

        while not self.__stop_event.is_set():
            self.deliver_all_session_rsp()

        print("RemoteAgent stopping...")
        front_msg_handler_thread.join()
        self.__recv_queue = None
        print("RemoteAgent thread exited")

    def deliver_all_session_rsp(self):
        try:
            if all_session_responses := self.recv_all_session_responses():
                self.__sink_queue.put(all_session_responses)
        except Exception as e:
            print(e)
            if isinstance(e, NoActiveSessionsError):
                self.set_active(False)
                self.notify_all_session_inactive()

    def notify_all_session_inactive(self):
        for session_id in self.get_session_id_list():
            self.__sink_queue.put(
                {
                    'msg_code': SESSION_INACTIVE_CODE,
                    'payload': {
                        'session_id': session_id
                    }
                }
            )

    def handle_front_msg(self):
        while True:
            msg = self.__recv_queue.get()
            msg_code = msg.get('msg_code')
            session_id = msg.get('payload', {}).get('session_id')
            if msg_code == LOGIN_CODE:
                page_line_count = msg.get('payload', {}).get('content', {}).get('page_line_count', 0)
                self.add_session(session_id, page_line_count)
                continue

            if msg_code == USER_COMMAND_CODE:
                command_str = msg.get('payload', {}).get('content', {}).get('command')
                if not self.is_active():
                    self.handle_user_command_inactive(session_id, command_str)
                else:
                    self.handle_user_command_active(session_id, command_str)
                continue

            if msg_code == REMOVE_SESSION_CODE:
                self.remove_session(msg.get('payload', {}).get('session_id'))
                self.wakeup_listener()
                continue

            if msg_code == REMOVE_AGENT_CODE:
                self.agent_release()
                self.__stop_event.set()
                self.wakeup_listener()
                print("Front message handler thread exited")
                return

            if msg_code == RECONNECT_SHELL_CODE:
                self.reconnect(session_id)
                continue

    def handle_user_command_inactive(self, session_id, command_str):
        if command_str == 'r':
            self.reconnect(session_id)
            return
        self.__sink_queue.put(
            {
                'msg_code': SESSION_INACTIVE_CODE,
                'payload': {
                    'session_id': session_id
                }
            }
        )

    def handle_user_command_active(self, session_id, command_str):
        self.execute_command(session_id, command_str)

    def reconnect(self, session_id):
        connect_params = self.__xClient.get_connect_params()
        client, result = RemoteAgent.get_client(connect_params)
        if not client:
            self.__sink_queue.put(
                {
                    'msg_code': RECONNECT_SHELL_FAIL_CODE,
                    'payload': {
                        'session_id': session_id
                    }
                }
            )
            return

        self.__xClient = client
        new_x_shell_dict = {}
        old_x_shell_dict = self.__x_shell_dict
        for session_id, inactive_shell in old_x_shell_dict.items():
            x_shell = self.__xClient.get_shell(inactive_shell.height)
            x_shell.session_id = session_id
            new_x_shell_dict[session_id] = x_shell

        del old_x_shell_dict
        self.replace_shell_dict(new_x_shell_dict)
        self.set_active(True)
        self.wakeup_listener()

    def add_session(self, session_id, page_line_count):
        try:
            if x_shell := self.__xClient.get_shell(page_line_count):
                x_shell.session_id = session_id
                self.add_shell(session_id, x_shell)
            self.__sink_queue.put(
                {
                    'msg_code': LOGIN_RSP_CODE,
                    'payload': {
                        'session_id': session_id,
                        'content': {
                            'result': RESPONSE_LOGIN_SUCCESS,
                            'page_line_count': page_line_count
                        }
                    }
                }
            )
        except Exception as e:
            self.__sink_queue.put(
                {
                    'msg_code': LOGIN_RSP_CODE,
                    'payload': {
                        'session_id': session_id,
                        'content': {
                            'result': str(e),
                        }
                    }
                }
            )
        finally:
            self.wakeup_listener()

    def execute_command(self, session_id, command):
        if shell := self.get_shell(session_id):
            shell.send(command)

    def recv_all_session_responses(self, buffer_size=10485760) -> Optional[Dict]:
        active_shell_list = self.get_active_shell_list()
        rlist = active_shell_list + [self.listener]

        current_active_shell_count = len(active_shell_list)
        last_active_shell_count = self.active_shell_count
        self.active_shell_count = current_active_shell_count

        if current_active_shell_count == 0 and last_active_shell_count > 0:
            raise NoActiveSessionsError()

        self.active_shell_count = current_active_shell_count
        ready_list = select.select(rlist, [], [], None)[0]
        payload = []

        for r in ready_list:
            if r is self.listener:
                self.confirm_wakeup_signal()
                continue

            shell = r
            if shell.recv_ready():
                inner_msgs = shell.recv_and_parser_bytes(buffer_size)
                payload.append({'session_id': shell.session_id, 'inner_msgs': inner_msgs})

        if payload:
            # print(f'\x1b[01;34mpayload\x1b[0m: {payload}')
            return {
                'msg_code': SESSION_STRING_CODE,
                'payload': payload
            }
        return None

    def remove_session(self, session_id):
        if shell := self.remove_shell(session_id):
            shell.close()

    def remove_all_session(self):
        for session_id in self.get_session_id_list():
            self.remove_session(session_id)

    def agent_release(self):
        self.remove_all_session()
        self.__xClient.close()
