from enum import Enum
import socket

HEADER_SIZE = 2
class ApplicationStatus(Enum):
    OK = 0
    ERROR = 1
    PLACE_BET = 2
class Header:
    msg_size: int
    status: ApplicationStatus
class Message:
    header: Header
    payload: list[int]
def read_msg(socket: socket):
    header = socket.recv(len(Header))
    payload = []
    while len(payload) < header.msg_size:
        payload.append(socket.recv(1))
    return header.status, payload