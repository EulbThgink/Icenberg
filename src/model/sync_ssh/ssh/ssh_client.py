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


import copy
from typing import Optional

import paramiko

from src.common.common_definition import VIEW_WIDTH
from src.common.decorate import exception_catch
from src.model.sync_ssh.ssh.ssh_shell import XShell


class XClient:
    def __init__(self):
        self.__ssh_client = paramiko.SSHClient()
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.__connect_params = None

    def set_connect_params(self, connect_params: dict):
        self.__connect_params = connect_params

    def get_connect_params(self) -> dict:
        return copy.copy(self.__connect_params)

    def connect(self, **kwargs):
        self.__ssh_client.connect(timeout=10, **kwargs)
        # 设置 keepalive，每个client只有一个transport
        self.__ssh_client.get_transport().set_keepalive(3)

    @exception_catch(exception_result=False)
    def close(self):
        self.__ssh_client.close()

    @exception_catch(exception_result=None)
    def get_shell(self, page_line_count, **kwargs) -> Optional[XShell]:
        return XShell(
            self.__ssh_client.invoke_shell(**kwargs, width=VIEW_WIDTH, height=page_line_count,term='xterm'),
            page_line_count
        )
