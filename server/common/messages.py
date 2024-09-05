import socket
import string
LEN_BYTES = 1
END_CHARACTER = "\n"
EXPECTED_MSG_FIELDS = 6
BUFFER_SIZE = 1024
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

def receive_msgs(socket:socket)-> tuple[list[list[str]], bool]:
    packets: list[list[str]] = []
    error: bool = False
    batch_len_bytes: bytes = socket.recv(LEN_BYTES)
    if not batch_len_bytes:
        return packets, True
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

def encode_field(field) -> bytes:
    return field.encode('utf-8') + "\n".encode('utf-8')

def send_msg(socket: socket, msg: string):
    bytes_sent = socket.send(encode_field(msg))
    while bytes_sent < len(msg):
        socket.send(encode_field(msg[bytes_sent:len(msg) -1]))
    
