MESSAGES = {'HELLO': 1, 'QUERY': 2, 'CHUNK INFO': 3, 'GET': 4, 'RESPONSE': 5}
BUFFER_SIZE = 1030
INITIAL_TTL = 3


def encript_message(*args):
    """Receive some arguments in int or bytearray, concatenate then and returns a bytearray with each elements size 2"""
    message = bytearray()
    for arg in args:
        if type(arg) == bytes:
            message += arg
        elif type(arg) != list:
            message += arg.to_bytes(2, "big")
        else:
            for item in arg:
                message += item.to_bytes(2, "big")
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
    """Receive a message with required chunks and a list chunks ids available in the peer and return a ordered list
    of matches"""
    number_of_chunks = decode_position(message, 1)
    chunk_array_info = []
    for i in range(number_of_chunks):
        required_chunk = decode_position(message, i + 2)
        if required_chunk in id_list:
            chunk_array_info.append(required_chunk)
    return sorted(chunk_array_info)


def convert_address_to_int_list(address):
    """Receive a tuple (address, port) and convert it in a int list"""
    address_list = []
    for item in address[0].split('.'):
        address_list.append(int(item))
    address_list.append(address[1])
    return address_list
