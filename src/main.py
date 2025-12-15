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


from multiprocessing import Pipe
from multiprocessing.connection import Connection

from PySide6.QtWidgets import QApplication

from src.controller.main_controller import MainController
from src.view.main_window import MainWindow
from src.view.ui_bridge import UiBridge

if __name__ == '__main__':
    # MainWindow<->UiBridge<->MainController
    conns = Pipe()
    fr_side: Connection = conns[0]
    bk_side: Connection = conns[1]

    app = QApplication([])
    app.setQuitOnLastWindowClosed(True)

    main_window = MainWindow()

    ui_bridge = UiBridge(fr_side)
    ui_bridge.connect_ui_signals(main_window)

    controller_process = MainController(bk_side)

    main_window.show()
    ui_bridge.start()
    controller_process.start()

    app.aboutToQuit.connect(controller_process.stop)
    app.aboutToQuit.connect(ui_bridge.stop)

    app.exec()
