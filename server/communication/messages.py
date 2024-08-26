import datetime
from enum import Enum
import socket
import string
MAX_STRING_LEN = 30
LEN_BYTES = 1
DNI_LEN = 8
DATE_LEN = 10
BET_NUMBER_LEN = 4
AGENCY_ID_LEN = 1
def read_field(socket: socket, field_len: int) -> string:
    field = socket.recv(1).decode('utf-8')
    while len(field.encode('utf-8')) < field_len:
        field += socket.recv(1).decode('utf-8')
    return socket,field
def read_var_len_field(socket: socket, max_field_len: int, field_name: string) -> string:
    field_len = socket.recv(LEN_BYTES).decode('utf-8')
    while len(field_len) < LEN_BYTES:
        field_len = socket.recv(LEN_BYTES).decode('utf-8')
    field_len = int(field_len)
    if field_len > max_field_len:
        raise ValueError("The maximum length for the field {} is {}", field_name, max_field_len)
    return read_field(socket,field_len)
def read_msg(socket: socket):
    socket, agency = read_field(socket, AGENCY_ID_LEN)
    socket, name = read_var_len_field(socket,MAX_STRING_LEN, "Name")
    socket, lastname = read_var_len_field(socket,MAX_STRING_LEN,"Last Name")
    socket, dni = read_field(socket, DNI_LEN)
    socket, birthdate = read_field(socket, DATE_LEN)
    socket, betnumber = read_field(socket, BET_NUMBER_LEN)
    return agency, name, lastname, dni, birthdate, betnumber
def encode_msg(agency, name, lastname, dni, birthdate, betnumber)-> bytes:
    agency_bytes = agency.encode()
    name_len_bytes = len(name).encode()
    name_bytes = name.encode()
    lastname_len_bytes = len(lastname).encode()
    dni_bytes = dni.encode()
    birthdate_bytes = birthdate.encode()
    betnumber_bytes = betnumber.encode()
    return agency_bytes + name_len_bytes + name_bytes + lastname_len_bytes + dni_bytes + birthdate_bytes + betnumber_bytes
    
    
    
    
