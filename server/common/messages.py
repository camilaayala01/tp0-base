import socket
import string
LEN_BYTES = 1
END_CHARACTER = "\n"
EXPECTED_MSG_FIELDS = 6
def receive_length(socket: socket) -> int:
    buf = socket.recv(LEN_BYTES) 
    while len(buf) < LEN_BYTES:
        socket.recv(LEN_BYTES - len(buf)) 
    return int.from_bytes(buf,'big')
def receive_msg(socket: socket) -> list[str]:
    fields: list[str] = []
    while len(fields) < EXPECTED_MSG_FIELDS:
        field_len = receive_length(socket)
        field = socket.recv(field_len).decode('utf-8')
        while len(field.encode('utf-8')) < field_len:
            field += socket.recv(field_len - len(field.encode('utf-8'))).decode('utf-8')
        fields.append(field)
    return fields

def encode_field(field) -> bytes:
    return field.encode('utf-8')

def send_msg(socket: socket, msg: string):
    bytes_sent = socket.send(encode_field(msg))
    while bytes_sent < len(msg):
        socket.send(encode_field(msg[bytes_sent:len(msg) -1]))
    
