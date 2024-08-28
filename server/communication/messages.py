import socket
import string
MAX_STRING_LEN = 255
LEN_BYTES = 1
DNI_LEN = 8
DATE_LEN = 10
NUMBER_LEN = 4
AGENCY_ID_LEN = 1

def read_field(socket: socket, field_len: int) -> string:
    field = socket.recv(field_len).decode('utf-8')
    while len(field.encode('utf-8')) < field_len:
        field += socket.recv(field_len - len(field.encode('utf-8'))).decode('utf-8')
    return socket,field
def read_var_len_field(socket: socket, max_field_len: int, field_name: string) -> string:
    field_len = socket.recv(LEN_BYTES).decode('utf-8')
    while len(field_len) < LEN_BYTES:
        field_len = socket.recv(LEN_BYTES).decode('utf-8')
    field_len = int(field_len)
    if field_len > max_field_len:
        raise ValueError("The maximum length for the field {} is {}", field_name, max_field_len)
    return read_field(socket,field_len)
def receive_bet(socket: socket):
    socket, agency = read_field(socket, AGENCY_ID_LEN)
    socket, name = read_var_len_field(socket,MAX_STRING_LEN, "Name")
    socket, lastname = read_var_len_field(socket,MAX_STRING_LEN,"Last Name")
    socket, dni = read_field(socket, DNI_LEN)
    socket, birthdate = read_field(socket, DATE_LEN)
    socket, number = read_field(socket, NUMBER_LEN)
    return agency, name, lastname, dni, birthdate, number
def encode_field(field) -> bytes:
    return field.encode('utf-8')
def encode_field_len(field, byte_num) -> bytes:
    return len(field).to_bytes(byte_num, 'big')
def encode_bet_msg(agency, name, lastname, dni, birthdate, number)-> bytes:
    return encode_field(agency) + encode_field_len(name) + encode_field(name) + encode_field_len(lastname) + encode_field(lastname) + encode_field(dni) + encode_field(birthdate) + encode_field(number)
def confirm_bet(socket: socket, msg: string):
    bytes_sent = socket.send(encode_field(msg))
    while bytes_sent < len(msg):
        socket.send(encode_field(msg[bytes_sent:len(msg) -1]))
    
