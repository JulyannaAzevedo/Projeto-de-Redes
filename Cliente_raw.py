import socket
import struct
import random

# Configurações do servidor
SERVER_IP = "127.0.0.1"  # Endereço IP do servidor local
SERVER_PORT = 50000  # Porta do servidor para as conexões dos clientes

# Função para calcular o checksum
def calcular_checksum(data):
    # Se o tamanho dos dados for ímpar, adiciona um byte zero ao final
    if len(data) % 2 != 0:
        data += b'\x00'
    
    # Soma de todos os shorts de 16 bits na mensagem
    total = sum(struct.unpack('!HH', data))

    # Adiciona o carry de volta ao resultado (se houver)
    total = (total & 0xffff) + (total >> 16)

    # Faz a negação bitwise do resultado
    return (~total) & 0xffff

# Função para construir o cabeçalho IP
def construir_cabecalho_ip(ip_origem, ip_destino, protocolo_transporte, comprimento):
    # Estrutura do cabeçalho IP
    cabecalho_ip = struct.pack("!BBHHHBBH4s4s", 69, 0, comprimento, 12345, 0, 64, protocolo_transporte, 0, socket.inet_aton(ip_origem), socket.inet_aton(ip_destino))
    
    return cabecalho_ip

# Função para construir a mensagem de requisição
def construir_requisicao(tipo, identificador, dados):
    # req_res_tipo representa o tipo da mensagem, armazenando req/res no nibble mais significativo e o tipo nos bits menos significativos
    req_res_tipo = (0 << 4) | tipo
    
    # A mensagem é empacotada com !BHB (1 byte para req_res_tipo, 2 bytes para identificador, e 1 byte vazio)
    return struct.pack('!BHB', req_res_tipo, identificador, 0) + dados, identificador

# Função para enviar requisição ao servidor e receber resposta
def enviar_requisicao(requisicao):
    try:
        # Criar um socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

        # Enviar a requisição para o servidor
        s.sendto(requisicao, (SERVER_IP, SERVER_PORT))

        # Receber a resposta do servidor
        resposta, _ = s.recvfrom(1024)  # Tamanho do buffer pode ser ajustado conforme necessário

        return resposta

    finally:
        s.close()  # Fechar o socket após o término

# Função para exibir a resposta recebida
def exibir_resposta(resposta):
    if resposta is None:
        print("Não foi possível receber a resposta do servidor.")
        return
    
    # Desempacotar o cabeçalho da resposta
    req_res, tipo, identificador, tamanho_resposta = struct.unpack("!BBHH", resposta[28:6])

    # Exibir tamanho da resposta
    print("Tamanho da resposta:", tamanho_resposta)

    if tamanho_resposta == 0:  # Resposta indicando recebimento de requisição inválida
        print("Requisição inválida.")
    else:
        # Pular os 20 bytes do cabeçalho IP e os 8 bytes do cabeçalho UDP para chegar ao conteúdo do payload
        dados_resposta = resposta[28:]
        resposta_decodificada = dados_resposta.decode('utf-8')  # Decodificar os dados da resposta
        print("Resposta:", resposta_decodificada)

# Função principal do cliente
def client():

    while True:
        # Solicitar entrada do usuário para selecionar o tipo de requisição
        print("\nEscolha o tipo de requisição:")
        print("1. Data e hora atual")
        print("2. Mensagem motivacional para o fim do semestre")
        print("3. Quantidade de respostas enviadas pelo servidor até o momento")
        print("4. Sair")

        escolha = input("\nDigite o número da opção desejada: ")

        # Sair do loop se a escolha for "4"
        if escolha == "4":
            print("Cliente encerrado.")
            break

        # Validar a escolha do usuário e construir a requisição correspondente
        if escolha in ["1", "2", "3"]:
            identificador = random.randint(1, 65535)  # Número de identificação (pode ser aleatório)
            tipo_requisicao = int(escolha) - 1  # Converte a escolha do usuário para o tipo de requisição
            dados = b''  # Dados vazios para inicialização

            # Construir a requisição final
            requisicao, identificador = construir_requisicao(tipo_requisicao, identificador, dados)

            # Enviar a requisição e receber a resposta do servidor
            resposta = enviar_requisicao(requisicao)

            # Exibir a resposta recebida
            exibir_resposta(resposta)

# Chamada da função principal do cliente
if __name__ == "__main__":
    client()