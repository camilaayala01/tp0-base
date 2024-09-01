import socket
import string
LEN_BYTES = 1
END_CHARACTER = "\n"
EXPECTED_MSG_FIELDS = 6
BUFFER_SIZE = 1024
def parse_msg(buffer: bytes) -> tuple[int, list[str]]:
    fields: list[str] = []
    idx: int = 0
    while idx < len(buffer):
        field_len = int.from_bytes(buffer[idx:idx+LEN_BYTES], 'big')
        idx += LEN_BYTES
        if idx + field_len <=  len(buffer):
            field = bytes(buffer[idx:idx+field_len]).decode('utf-8')
            fields.append(field)
            idx += field_len
            if len(fields) == EXPECTED_MSG_FIELDS:
                break 
        else:
            break
    return idx, fields
## Se parsea el len en el mismo parse msg que el field
## Si me queda el len suelto me lo guardo y le apendeo los nuevos bytes
def receive_msg(buffer: bytes, socket: socket)-> tuple[list[str], bytes]:
    read, msg = parse_msg(buffer)
    ## termino el buffer pero no termino el mensaje --> leo mas 
    while len(msg) < EXPECTED_MSG_FIELDS:
        buffer = socket.recv(BUFFER_SIZE)
        read, more_msg = parse_msg(buffer)
        msg += more_msg
    if read < len(buffer):
        return msg, buffer[read:len(buffer) - 1]
    return msg, []

def receive_msgs(socket:socket, batch_size: int)-> list[list[str]]:
    packets: list[list[str]] = []
    buffer: bytes = []
    for i in range(0,batch_size):
        rcved = socket.recv(BUFFER_SIZE)
        buffer += rcved
        packet, buffer = receive_msg(buffer, socket)
        packets.append(packet)
    return packets

def encode_field(field) -> bytes:
    return field.encode('utf-8') + "\n".encode('utf-8')

def send_msg(socket: socket, msg: string):
    bytes_sent = socket.send(encode_field(msg))
    while bytes_sent < len(msg):
        socket.send(encode_field(msg[bytes_sent:len(msg) -1]))
    
