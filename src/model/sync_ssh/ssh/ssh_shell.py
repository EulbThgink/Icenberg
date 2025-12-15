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


from src.common.decorate import exception_catch
from src.model.parser.buffer.session_bytes_buffer import SessionBytesBuffer


class XShell:
    def __init__(self, shell, height: int):
        self.__session_id = None
        self.__shell = shell
        self.__height = height
        self.__session_bytes_buffer = SessionBytesBuffer()
        self.__send_record = []

    @property
    def height(self):
        return self.__height

    @property
    def session_id(self):
        return self.__session_id

    @session_id.setter
    def session_id(self, session_id: str):
        self.__session_id = session_id

    @exception_catch(exception_result=None)
    def close(self):
        print("Closing XShell...!!!")
        self.__shell.close()

    @exception_catch(exception_result=None)
    def send(self, command: str):
        send_bytes = command.encode('utf-8')
        self.__send_record.append(send_bytes)
        self.__shell.send(command.encode('utf-8'))

    @exception_catch(exception_result=[])
    def recv_and_parser_bytes(self, buffer_size=2048) -> list:
        recv_bytes = self.__shell.recv(buffer_size)
        # print(f"\x1b[01;34mrecv_bytes\x1b[0m: {recv_bytes}")
        last_send_bytes = self.__send_record[-1] if self.__send_record else b''

        return [x for x in self.__session_bytes_buffer.parse(recv_bytes, last_send_bytes)]

    def recv_ready(self) -> bool:
        return self.__shell.recv_ready()

    def fileno(self) -> int:
        return self.__shell.fileno()

    def is_closed(self) -> bool:
        return self.__shell.closed