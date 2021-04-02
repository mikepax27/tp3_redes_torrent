from include import common
import sys
import os
import socket

# Michael Páris Alexandre Xavier - 2014062018

# Peer's own address
udp_ip = sys.argv[1].split(':')[0]
udp_port = int(sys.argv[1].split(':')[1])

# Lists with Ids and names of possessed files
key_values_file = sys.argv[2]
file_list_id = []
file_list_name = []
for line in open(key_values_file):
    file_list_id.append(int(line.split(': ')[0]))
    file_list_name.append(line.split(': ')[1].replace('\n', '').replace(' ', ''))
print(f'Chunk stored: {file_list_id}')

# Array with sets (ip, port) of known peers
known_peers_ip_port = []
for i in range(3, len(sys.argv)):
    known_peers_ip_port.append((sys.argv[i].split(':')[0], int(sys.argv[i].split(':')[1])))

# Create a UDP socket at client side
peer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
peer_socket.bind((udp_ip, udp_port))
peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

while True:
    message_received, source_address = peer_socket.recvfrom(common.BUFFER_SIZE)

    if common.get_type_of_message(message_received) == 'HELLO':
        print(f'Received HELLO from {source_address[0]}:{source_address[1]}')

        # Build and send the Query to the known peers
        source_address_byte = common.convert_address_to_byte_list(source_address)
        new_message = common.encript_message(common.MESSAGES['QUERY'], source_address_byte, common.INITIAL_TTL,
                                             message_received[2:])
        for peer in known_peers_ip_port:
            peer_socket.sendto(new_message, peer)
            print(f'Sent a QUERY to {peer[0]}:{peer[1]}')

        # Build and send the Chunk Info to the Client
        match_id_list = common.generate_chunk_array_info(message_received, file_list_id)
        if len(match_id_list) > 0:
            new_message = common.encript_message(common.MESSAGES['CHUNK INFO'], len(match_id_list), match_id_list)
            peer_socket.sendto(new_message, source_address)
            print(f'Sent a CHUNK INFO to {source_address[0]}:{source_address[1]} informing {match_id_list}')

    elif common.get_type_of_message(message_received) == 'QUERY':
        print(f'Received QUERY from {source_address[0]}:{source_address[1]}')

        # Update the query e send to others peers
        updated_ttl, new_message = common.get_ttl_and_update_message(message_received)
        if updated_ttl > 0:
            for peer in known_peers_ip_port:
                if peer != source_address:
                    peer_socket.sendto(new_message, peer)
                    print(f'Sent a QUERY to {peer[0]}:{peer[1]}')

        # Build and send the Chunk Info to the Client
        match_id_list = common.generate_chunk_array_info(message_received, file_list_id)
        if len(match_id_list) > 0:
            client_address = common.extract_client_address_from_query(message_received)
            new_message = common.encript_message(common.MESSAGES['CHUNK INFO'], len(match_id_list), match_id_list)
            peer_socket.sendto(new_message, client_address)
            print(f'Sent a CHUNK INFO to {client_address[0]}:{client_address[1]} informing chunks {match_id_list}')

    else:
        print(f'Received GET from {source_address[0]}:{source_address[1]}')
        number_of_chunks_asked = common.decode_position(message_received, 1)

        for chunk in range(2, number_of_chunks_asked + 2):
            chunk_id = common.decode_position(message_received, chunk)
            chunk_index = file_list_id.index(chunk_id)

            chunk_file = open(file_list_name[chunk_index], 'rb')
            chunk_data = chunk_file.read(1026)
            chunk_size = os.path.getsize(file_list_name[chunk_index])
            new_message = common.encript_message(common.MESSAGES['RESPONSE'], chunk_id, chunk_size, chunk_data)
            chunk_file.close()

            peer_socket.sendto(new_message, source_address)
            print(f'Sent a RESPONSE to {source_address[0]}:{source_address[1]} with chunk {chunk_id}')
