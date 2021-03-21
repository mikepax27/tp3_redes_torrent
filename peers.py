from include import common
import sys
import socket

# Peer's own address
udp_ip = sys.argv[1].split(':')[0]
udp_port = int(sys.argv[1].split(':')[1])

key_values_file = sys.argv[2]
file_list_id = []
file_list_name = []
for line in open(key_values_file):
    file_list_id.append(int(line.split(': ')[0]))
    file_list_name.append(line.split(': ')[1].replace('\n', '').replace(' ', ''))

known_peers_ip = []
for i in range(3, len(sys.argv)):
    known_peers_ip.append((sys.argv[i].split(':')[0], int(sys.argv[i].split(':')[1])))

# Create a UDP socket at client side
peer_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
peer_socket.bind((udp_ip, udp_port))
peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

while True:
    message_received, source_address = peer_socket.recvfrom(common.BUFFER_SIZE)
    print(message_received)
    print(source_address)

    if common.get_type_of_message(message_received) == 'HELLO':

        # Build and send the Query
        source_address_int = common.convert_address_to_int_list(source_address)
        new_message = common.encript_message(common.MESSAGES['QUERY'], source_address_int, common.INITIAL_TTL,
                                             message_received[2:])
        print(new_message)
        for other_peer in known_peers_ip:
            peer_socket.sendto(new_message, other_peer)

        # Build and send the Chunk Info
        match_id_list = common.generate_chunk_array_info(message_received, file_list_id)
        new_message = common.encript_message(common.MESSAGES['CHUNK INFO'], len(match_id_list), match_id_list)
        peer_socket.sendto(new_message, source_address)
