import socket
import string
LEN_DELIMITER = "~"
END_CHARACTER = "\n"
def receive_length(socket: socket) -> int:
    length = ""
    while char_read := socket.recv(1).decode('utf-8') != "~":
        length += char_read
    return int(length)
def receive_msg(socket: socket) -> list[str]:
    fields: list[str] = []
    to_read = ""
    while (char_read := socket.recv(1).decode('utf-8')) != "\n":
        if char_read != "~":
            to_read += char_read
        else:
            field_len = int(to_read)
            to_read = ""
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
    
