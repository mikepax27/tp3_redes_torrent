from include import common
import sys
import socket

# Peer's address data
peer_ip = sys.argv[1].split(':')[0]
peer_port = int(sys.argv[1].split(':')[1])

# Chunk's data
chunks_needed = []
for i in range(len(sys.argv[2].split(','))):
    chunks_needed.append(int(sys.argv[2].split(',')[i]))
number_of_chunks = len(chunks_needed)

message = common.encript_message(common.MESSAGES['HELLO'], number_of_chunks, chunks_needed)

# Create a UDP socket at client side
client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Send HELLO message to server using created UDP socket
client_socket.sendto(message, (peer_ip, peer_port))
print(f'Sent HELLO to {peer_ip}:{peer_port}')

while True:
    message_received, peer_address = client_socket.recvfrom(common.BUFFER_SIZE)
    print(message_received)
    print(peer_address)
