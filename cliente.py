from include import common
import sys
import socket

# Michael Páris Alexandre Xavier - 2014062018

ip_address = socket.gethostbyname(socket.gethostname())

# Peer's address data
peer_address = (sys.argv[1].split(':')[0], int(sys.argv[1].split(':')[1]))

# Chunk's data
chunks_needed_list = []
for i in range(len(sys.argv[2].split(','))):
    chunks_needed_list.append(int(sys.argv[2].split(',')[i]))
number_of_chunks = len(chunks_needed_list)
chunk_and_address_list = []

message = common.encript_message(common.MESSAGES['HELLO'], number_of_chunks, chunks_needed_list)

# Create a UDP socket at client side
client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
client_socket.settimeout(5.0)

# Send HELLO message to server using created UDP socket
client_socket.sendto(message, peer_address)
print(f'Sent HELLO to {peer_address[0]}:{peer_address[1]} asking chunks {chunks_needed_list}')

# Await and treat the chunks info
while True:
    chunks_to_ask = []
    try:
        message_received, peer_address = client_socket.recvfrom(common.BUFFER_SIZE)

        # Process chunk info information received
        number_of_chunks_informed = common.decode_position(message_received, 1)
        print(f'Received CHUNK INFO from {peer_address[0]}:{peer_address[1]} informing {number_of_chunks_informed} '
              f'chunks')
        for position in range(2, number_of_chunks_informed + 2):
            chunk_informed = common.decode_position(message_received, position)
            if chunk_informed in chunks_needed_list:
                chunks_needed_list.remove(chunk_informed)
                chunks_to_ask.append(chunk_informed)
        if len(chunks_to_ask) > 0:
            chunk_and_address_list.append((chunks_to_ask, peer_address))

    except socket.timeout:
        print(f'Chunk {chunks_needed_list} info missing')
        break

# Send the GET requests
for (chunks, peer_to_ask) in chunk_and_address_list:
    message = common.encript_message(common.MESSAGES['GET'], len(chunks), chunks)
    client_socket.sendto(message, peer_to_ask)
    print(f'Sent GET to {peer_to_ask[0]}:{peer_to_ask[1]} for chunks {chunks}')


# Process all RESPONSE messages
number_chunks_asked = number_of_chunks - len(chunks_needed_list)
log_file = open('output-' + ip_address + '.log', 'w')
print(ip_address)

for request in range(number_chunks_asked):
    message_received, peer_address = client_socket.recvfrom(common.BUFFER_SIZE)

    if common.get_type_of_message(message_received) == 'RESPONSE':
        chunk_id = common.decode_position(message_received, 1)
        print(f'Received RESPONSE from {peer_address[0]}:{peer_address[1]} for chunk {chunk_id}')
        chunk_size = common.decode_position(message_received, 2)
        chunk_data = message_received[6:]

        chunk_file = open('Chunk_received_' + str(chunk_id) + '.m4s', 'wb')
        chunk_file.write(chunk_data[:chunk_size])
        chunk_file.close()
        log_file.write(f'{peer_address[0]}:{peer_address[1]} - {chunk_id}\n')

for missed_chunk in chunks_needed_list:
    log_file.write(f'0.0.0.0:0 - {missed_chunk}\n')

log_file.close()
