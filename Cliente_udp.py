import socket
import struct
import random
import time

# Endereço e porta do servidor
SERVER_IP = "127.0.0.1"
SERVER_PORT = 50000 
MAX_BYTES = 1024

# Função para construir o cabeçalho UDP
def build_udp_header(source_port, destination_port, length):
    checksum = 0  # O checksum será calculado posteriormente
    return struct.pack("!HHHH", source_port, destination_port, length, checksum)

# Função para construir a mensagem de requisição
def build_request(source_port, destination_port, identifier, request_type):
    udp_header = build_udp_header(source_port, destination_port, 0)  # Tamanho inicial 0, será ajustado posteriormente
    response_type = 0  # Tipo de requisição
    response_length = 0  # Tamanho inicial da resposta
    return struct.pack("!BBHH", response_type, request_type, identifier, response_length) + udp_header

# Função para enviar requisição ao servidor e receber resposta
def send_request(request):
    try:
        # Criar um socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Enviar a requisição para o servidor
        s.sendto(request, (SERVER_IP, SERVER_PORT))

        # Receber a resposta do servidor
        response, _ = s.recvfrom(1024)  # Tamanho do buffer pode ser ajustado conforme necessário
        return response

    finally:
        s.close()  # Fechar o socket após o término

# Função para exibir a resposta recebida
def display_response(response):
    response_type, request_type, identifier, response_length = struct.unpack("!BBHH", response[:6])
    # Verificar o tipo de resposta
    if response_type == 0:  # Requisição
        print("Requisição inválida.")
    elif response_type == 1:  # Resposta
        if request_type == 0: 
            print("Data e Hora Atual:", response[6:].decode())
        elif request_type == 1: 
            print("Mensagem Motivacional:", response[6:].decode())
        elif request_type == 2:
            num_responses = struct.unpack("!B", response[6:7])[0]
            print("Quantidade de Respostas:", num_responses)

# Função principal do cliente
def client():
    
    while True:
        # Solicitar entrada do usuário para selecionar o tipo de requisição
        print("\nEscolha o tipo de requisição:")
        print("1. Data e hora atual")
        print("2. Mensagem motivacional para o fim do semestre")
        print("3. Quantidade de respostas enviadas pelo servidor até o momento")
        print("4. Sair")
        choice = input("\nDigite o número da opção desejada: ")
        if choice == "4":
            print("Cliente encerrado...")
            break

        # Construir a requisição de acordo com a escolha do usuário
        if choice in ["1", "2", "3"]:
            identifier = random.randint(1, 65535)  # Número de identificação (pode ser aleatório)
            request_type = int(choice) - 1  # Converte a escolha do usuário para o tipo de requisição
            request = build_request(59155, SERVER_PORT, identifier, request_type)

            # Enviar a requisição para o servidor e receber a resposta
            response = send_request(request)

            # Exibir a resposta recebida
            display_response(response)

            # Adicionar atraso aleatório
            time.sleep(random.uniform(0.5, 2.0))

# Chamada da função principal do cliente
if __name__ == "__main__":
    client()