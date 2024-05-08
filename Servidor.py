import socket
import struct

# Endereço e porta do servidor
SERVER_IP = "127.0.0.1"
SERVER_PORT = 50000 

# Função para tratar as requisições do cliente
def handle_request(request):
    # Verificar se o tamanho do buffer é suficiente
    if len(request) < 6:
        # Se o tamanho do buffer for menor que 6, retornar uma mensagem de erro
        error_message = "Erro: Requisição inválida. Tamanho do buffer insuficiente."
        return struct.pack("!BBBBB", 1, 3, 0, 0, len(error_message)) + error_message.encode('utf-8')

    # Desempacotar a requisição se o tamanho do buffer for suficiente
    response_type, request_type, identifier_high, identifier_low, _ = struct.unpack("!BBHHH", request[:8])
    
    identifier = (identifier_high << 8) | identifier_low
    
    # Verificar o tipo de requisição e enviar a resposta correspondente
    if request_type == 0:  # Data e hora atual
        response = "2024-05-07 15:30:00\n"
    elif request_type == 1:  # Mensagem motivacional
        response = "Mantenha-se firme! Você está quase no final do semestre.\n"
    elif request_type == 2:  # Quantidade de respostas enviadas pelo servidor
        response = str(10)  # Número fictício de respostas
    
    # Codificar a resposta como bytes usando a codificação UTF-8
    response_bytes = response.encode('utf-8')
    
    # Construir a mensagem de resposta de acordo com o formato especificado
    response_message = struct.pack("!BBHHB", 1, request_type, identifier_high, identifier_low, len(response_bytes)) + response_bytes
    return response_message

# Função principal do servidor
def main():
    # Criar um socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Vincular o socket ao endereço e porta do servidor
    s.bind((SERVER_IP, SERVER_PORT))

    print("Servidor UDP fictício iniciado. Aguardando requisições...")

    while True:
        # Receber a requisição do cliente
        request, client_address = s.recvfrom(1024)

        # Processar a requisição e obter a resposta
        response = handle_request(request)

        # Enviar a resposta para o cliente
        s.sendto(response, client_address)

    # Fechar o socket após o término
    s.close()

# Chamada da função principal do servidor
if __name__ == "__main__":
    main()