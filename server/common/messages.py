import socket
from enum import Enum

LEN_BYTES = 1
AGENCY_ID_BYTES = 1
END_CHARACTER = "\n"
SEPARATOR = ","
EXPECTED_MSG_FIELDS = 6
BUFFER_SIZE = 1024

class MsgType(Enum):
    PLACE_BETS = 0
    NOTIFY = 1
    REQ_RESULTS = 2
    PLACE_BETS_OK = 3
    REQ_RESULTS_OK = 4
    SERVER_ERR = 5
    PLACE_BETS_ERR = 6
    
"""
Receives a bytes buffer and an amount of fields to read. If the buffer ends with the length of a packet 
it will return those bytes for them to be appended to the respective field. Otherwise it will read from the buffer said
length of bytes and decode them as a string.
"""

def parse_msg(buffer: bytes, fields_to_read: int) -> tuple[int, list[str]]:
    fields: list[str] = []
    idx: int = 0
    while idx < len(buffer):
        field_len = int.from_bytes(buffer[idx:idx+LEN_BYTES], 'big')
        if idx + LEN_BYTES + field_len <=  len(buffer):
            idx += LEN_BYTES
            field = bytes(buffer[idx:idx+field_len]).decode('utf-8')
            fields.append(field)
            idx += field_len
            if len(fields) == fields_to_read:
                break 
        else:
            break
    return idx, fields
"""
Receives a message from a buffer and if it is cut in half it reads more bytes from the stream.
Will return the parsed message and remaining buffer bytes
Will fail if the stream is close in the middle of a package. 
"""

def receive_msg(buffer: bytes, socket: socket)-> tuple[list[str], bytes]:
    read, msg = parse_msg(buffer, EXPECTED_MSG_FIELDS)
    while len(msg) < EXPECTED_MSG_FIELDS:
        buffer = buffer[read:len(buffer)]
        more_buffer = socket.recv(BUFFER_SIZE)
        if not more_buffer:
            return None, None
        buffer += more_buffer
        read, more_msg = parse_msg(buffer, EXPECTED_MSG_FIELDS - len(msg))
        msg += more_msg
    return msg, buffer[read:len(buffer)]
"""
Receives a length of a batch from socket and tries to read them
Will read a fixed amount of bytes and try to process all the packages there before requesting more bytes
Will return error = True if:
- The stream ended in the middle of a bet
- The socket was closed before the length or the amount of indicated packets could be read.
"""
def receive_bets(socket:socket)-> tuple[list[list[str]], bool]:
    packets: list[list[str]] = []
    error: bool = False
    batch_len_bytes: bytes = socket.recv(LEN_BYTES) 
    if not batch_len_bytes:
        return packets, True
    while len(batch_len_bytes) < LEN_BYTES:
        batch_len_bytes += socket.recv(LEN_BYTES) 
    batch_len = int.from_bytes(batch_len_bytes, 'big')
    while len(packets) < batch_len and not error:
        buffer: bytes = socket.recv(BUFFER_SIZE)
        if not buffer:
            return packets, True
        while True:
            if len(buffer) == 0:
                break
            packet, buffer = receive_msg(buffer, socket)
            if not packet:
                error = True
                break
            packets.append(packet)   
    return packets, error

def get_agency_id(socket: socket)-> int:
    return get_fixed_len_number_field(socket, AGENCY_ID_BYTES)

def get_msg_type(socket: socket)-> int:
    return get_fixed_len_number_field(socket, LEN_BYTES)

def get_fixed_len_number_field(socket: socket, fixed_len: int) -> int:
    field_bytes: bytes = socket.recv(fixed_len)
    if not field_bytes:
        return -1
    return int.from_bytes(field_bytes, 'big')

def format_list(list: list[str]) -> str:
    answer = ""
    for i in range(len(list)):
        answer += list[i]
        if i < len(list) - 1:
            answer += SEPARATOR
    return answer 

def format_and_encode(msg_type: MsgType, msg: str) -> bytes:
    formatted = str(msg_type.value) + SEPARATOR
    formatted += msg
    formatted += END_CHARACTER
    return formatted.encode('utf-8')

def send_msg(socket: socket, msg_type: MsgType, msg: str):
    msg_bytes = format_and_encode(msg_type, msg)
    socket.sendall(msg_bytes)
    
