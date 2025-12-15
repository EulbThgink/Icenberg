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


import logging
from multiprocessing.connection import Connection

from PySide6.QtCore import Qt, Signal, QThread

from src.view.main_window import MainWindow


class UiBridge(QThread):
    SIG_2_FRONT = Signal(dict)

    SLEEP_MS = 30
    TO_FRONT_SHM_SIZE = 10 * 1024 * 1024  # 10MB
    TO_BACKEND_SHM_SIZE = 1024 * 1024  # 1MB

    def __init__(self, fr_side: Connection):
        super().__init__()
        self.fr_side = fr_side
        logging.info('ui bridge init')

    def connect_ui_signals(self, main_window: MainWindow):
        main_window.SIG_2_BACKEND.connect(
            self.send_msg_to_backend, type=Qt.ConnectionType.DirectConnection
        )
        self.SIG_2_FRONT.connect(
            main_window.update_view, type=Qt.ConnectionType.QueuedConnection
        )

    def run(self):
        logging.info('ui bridge start running')
        self.__loop_trigger_view_update()
        print('ui bridge stopped')

    def stop(self):
        try:
            if self.fr_side and not self.fr_side.closed:
                self.fr_side.close()
        except Exception:
            pass
        self.wait()

    def __loop_trigger_view_update(self):
        while True:
            try:
                msg = self.fr_side.recv()
                self.SIG_2_FRONT.emit(msg)
            except (EOFError, OSError, ValueError):
                break

    def send_msg_to_backend(self, data: dict):
        # print('\x1b[1:31msend_msg_to_backend\x1b[m', data)
        if not self.fr_side.closed:
            self.fr_side.send(data)
