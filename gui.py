import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, QThreadPool, QTimer, QRunnable

from stego_slack_app import StegoSlackApp

my_format = 'utf-8'

class SecretWindow:
    def __init__(self, parent, is_left: bool, is_sender: bool):
        self.parent = parent
        self.is_left = is_left
        self.is_sender = is_sender
        self.history_secrets = []
        self.left_border = 20 if is_left else parent.width - 300
    
    def initUI(self):
        # Display history
        parent = self.parent
        self.history_labels = [QLabel(parent) for i in range(0, 20)]
        for i, label in enumerate(self.history_labels):
            label.move(self.left_border, parent.height - 100 - 40 * (i+1))
            label.resize(280, 40)
        if self.is_sender:
            # Secret textbox
            self.textbox = QLineEdit(parent)
            self.textbox.move(self.left_border, parent.height - 90)
            self.textbox.resize(280,40)
            # Send button
            self.send_button = QPushButton('Send secret', parent)
            self.send_button.move(self.left_border, parent.height - 40)
            self.send_button.clicked.connect(self.on_click_send)

    def add_secret(self, secret_message):
        self.history_secrets = [secret_message] + self.history_secrets
        for i in range(0, min(len(self.history_secrets), len(self.history_labels))):
            self.history_labels[i].setText(self.history_secrets[i])

    def on_click_send(self):
        secret_message = self.textbox.text()
        self.textbox.setText("")
        self.add_secret(secret_message)
        self.parent.stego_app.post_secret(bytes(secret_message, my_format))

class UpdateWorker(QRunnable):
    def __init__(self, stego_app: StegoSlackApp, secret_window_receive: SecretWindow):
        super().__init__()
        self.stego_app = stego_app
        self.secret_window_receive = secret_window_receive
    def run(self):
        received_secret = self.stego_app.update()
        if received_secret is not None:
            self.secret_window_receive.add_secret(str(received_secret, my_format))

class MyApp(QMainWindow):

    def __init__(self, stego_app: StegoSlackApp, is_alice: bool):
        super().__init__()
        self.title = 'Stego App'
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.is_alice = is_alice
        self.stego_app = stego_app
        self.secret_window_send = SecretWindow(parent=self, is_left=is_alice, is_sender=True)
        self.secret_window_receive = SecretWindow(parent=self, is_left=not is_alice, is_sender=False)
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
        # Init secret windows
        self.secret_window_send.initUI()
        self.secret_window_receive.initUI()

        self.threadpool = QThreadPool()
        self.timer = QTimer()
        self.timer.setInterval(10000)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start()

        self.show()

    def on_timer(self):
        worker = UpdateWorker(self.stego_app, self.secret_window_receive)
        self.threadpool.start(worker)

if __name__ == '__main__':
    print(str(sys.argv))
    assert(len(sys.argv) == 2 and sys.argv[1] in ['--alice', '--bob'])
    app = QApplication(sys.argv)
    is_alice = sys.argv[1] == '--alice'
    ex = MyApp(stego_app = StegoSlackApp(is_alice=is_alice), is_alice=is_alice)
    sys.exit(app.exec_())
