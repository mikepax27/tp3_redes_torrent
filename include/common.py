MESSAGES = {'HELLO': 1, 'QUERY': 2, 'CHUNK INFO': 3, 'GET': 4, 'RESPONSE': 5}
BUFFER_SIZE = 1030
INITIAL_TTL = 3


def encript_message(*args):
    """Receive some arguments in int or bytearray, concatenate then and returns a bytearray"""
    message = bytearray()
    for arg in args:
        if type(arg) == int:
            message += arg.to_bytes(2, 'big')
        else:
            for item in arg:
                if type(item) == bytes:
                    message += item
                else:
                    message += item.to_bytes(2, 'big')
    return message


def get_type_of_message(message):
    """Determinate if the message is the type of HELLO, QUERY, CHUNK INFO, GET or RESPONSE"""
    for key, value in MESSAGES.items():
        if value == int.from_bytes(message[:2], 'big'):
            return key


def decode_position(message, position):
    """Decode one position of the array of byte array starting at 0 and size 2"""
    return int.from_bytes(message[position * 2: position * 2 + 2], 'big')


def generate_chunk_array_info(message, id_list):
    """Receive a message required chunks and a list chunks ids available in the peer and return a ordered list
    of matches"""
    if get_type_of_message(message) == 'HELLO':
        number_of_chunks = decode_position(message, 1)
        pointer = 2
    else:  # QUERY
        number_of_chunks = decode_position(message, 5)
        pointer = 6
    chunk_array_info = []
    for i in range(number_of_chunks):
        required_chunk = decode_position(message, pointer + i)
        if required_chunk in id_list:
            chunk_array_info.append(required_chunk)
    return sorted(chunk_array_info)


def convert_address_to_byte_list(address):
    """Receive a tuple (address, port) and convert it to a byte list [b, b, b, b, bb]"""
    byte_address = []
    for item in address[0].split('.'):
        byte_address.append((int(item)).to_bytes(1, 'big'))
    byte_address.append(address[1].to_bytes(2, 'big'))
    return byte_address


def extract_client_address_from_query(message):
    """Read a query message and return a set with the client ip and port"""
    ip = ''
    for position in range(2, 6):
        if ip != '':
            ip += '.'
        ip += str(int.from_bytes(message[position: position + 1], 'big'))
    port = int.from_bytes(message[6: 8], 'big')
    address = (ip, port)
    return address


def get_ttl_and_update_message(message):
    ttl = int.from_bytes(message[8: 10], 'big') - 1
    new_message = message[:8] + ttl.to_bytes(2, 'big') + message[10:]
    return ttl, new_message
