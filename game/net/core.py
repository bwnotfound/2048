import socket
from threading import Thread, Event
import logging


class NetManager:
    def __init__(self, is_server, host, port=32564):
        self.is_server = is_server
        self.host = host
        self.port = port
        self._listen_thread = None
        self._stop_event = Event()
        self.client: socket.socket = None

    def set_listen_callback(self, callback):
        self.listen_callback = callback

    def connect(self, connect_callback, receive_callback):
        if self._listen_thread is None or not self._listen_thread.is_alive():
            self._listen_thread = NetManagerThread(
                self.is_server,
                self._stop_event,
                connect_callback,
                receive_callback,
                self,
                host=self.host,
                port=self.port,
            )
            self._listen_thread.start()

    def send(self, data, callback):
        # send 需要在 connect 并 connect_callback 之后调用
        if self.client is None:
            logging.warning("连接未建立，无法发送数据")
            return
        self.client.send(data)
        if callback is not None:
            callback()


class NetManagerThread(Thread):
    def __init__(
        self,
        is_server,
        stop_event: Event,
        connect_callback,
        receive_callback,
        net_man: NetManager,
        host="localhost",
        port=32564,
    ):
        super().__init__()
        self.is_server = is_server
        self.stop_event = stop_event
        self.host = host
        self.port = port
        self.net_man = net_man
        self.connect_callback = connect_callback
        self.receive_callback = receive_callback

    def run(self):
        if self.is_server:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(3)
            self.client, addr = self.server.accept()
        else:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
        self.net_man.client = self.client
        self.connect_callback()
        while not self.stop_event.is_set():
            data = self.client.recv(2048)
            self.receive_callback(data)
