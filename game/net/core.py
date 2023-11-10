import socket
from threading import Thread, Event
import logging
from time import sleep
from queue import Queue
import pickle
import struct


class NetManager:
    def __init__(self, is_server, host=None, port=11111):
        self.is_server = is_server
        self.host = host if host is not None else socket.gethostname()
        self.port = port
        self._listen_thread = None
        self._stop_event = Event()
        self.client: socket.socket = None
        self.data_queue = Queue()

    def connect(self, connect_callback):
        r'''
        connect_callback: 连接成功或失败时的回调函数，参数为异常对象，若连接成功则为 None
        '''
        if self._listen_thread is None or not self._listen_thread.is_alive():
            self._listen_thread = NetManagerThread(
                self.is_server,
                self._stop_event,
                connect_callback,
                self,
                self.host,
                self.port,
            )
            self._listen_thread.daemon = True
            self._listen_thread.start()

    def disconnect(self):
        self._stop_event.set()
        if self.client is not None:
            self.client.close()
        if self._listen_thread is not None and self._listen_thread.is_alive():
            self._listen_thread.join()
            
    def is_connected(self):
        if self.client is None:
            return False
        return True

    def send(self, data):
        r'''
        data: 要发送的数据
        return:
            0: 发送成功
            1: 连接未建立
        '''
        # send 需要在 connect 并 connect_callback 之后调用
        if self.client is None:
            logging.warning("连接未建立，无法发送数据")
            return 1
        try:
            b_data = pickle.dumps(data)
            b_length = struct.pack("i", len(b_data))
            self.client.sendall(b_length + b_data)
            return 0
        except Exception as e:
            logging.warning("发送数据失败，异常类型：{}".format(type(e).__name__))

    def recv(self):
        if self.data_queue.empty():
            return None
        return self.data_queue.get()


class NetManagerThread(Thread):
    def __init__(
        self,
        is_server,
        stop_event: Event,
        connect_callback,
        net_man: NetManager,
        host,
        port,
    ):
        super().__init__()
        self.is_server = is_server
        self.stop_event = stop_event
        self.host = host
        self.port = port
        self.net_man = net_man
        self.connect_callback = connect_callback

    def run(self):
        try:
            if self.is_server:
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((self.host, self.port))
                self.server.listen(3)
                self.server.setblocking(False)
                while not self.stop_event.is_set():
                    try:
                        self.client, addr = self.server.accept()
                        break
                    except BlockingIOError:
                        sleep(0.1)
                        logging.debug("waiting for connection")
                else:
                    logging.debug("net manager thread exit")
                    return
            else:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((self.host, self.port))
        except Exception as e:
            logging.warning("连接失败，异常类型：{}。异常信息：{}".format(type(e).__name__, str(e)))
            self.connect_callback(e)
            return
        self.client.setblocking(True)
        self.client.settimeout(0.1)
        self.net_man.client = self.client
        self.connect_callback(None)
        try:
            while not self.stop_event.is_set():
                try:
                    b_length = self.client.recv(4)
                    length = struct.unpack("i", b_length)[0]
                    b_data = self.client.recv(length)
                    data = pickle.loads(b_data)
                    self.net_man.data_queue.put(data)
                except socket.timeout as e:
                    continue
                except ConnectionResetError:
                    break
                except OSError:
                    break
                except Exception as e:
                    logging.warning("接收数据失败，异常类型：{}".format(type(e).__name__))
                    break
            logging.debug("net manager thread exit")
        finally:
            self.client.close()
            self.net_man.client = None
