import socket
import struct
import random

# Configurações do servidor
IP_SERVIDOR = '127.0.0.1'
PORTA_SERVIDOR = 50000

# Configurações do cliente
IP_CLIENTE = '127.0.0.1'
PORTA_CLIENTE = 59155

# mensagem pré-definidos com as escolhas
DATA_HORA = 0b0001  # 0001 para data e hora
MENSAGEM_MOTIVACIONAL = 0b0010  # 0010 para mensagem motivacional
CONTADOR_RESPOSTAS = 0b0011  # 0011 para contador de respostas
REQUISICAO_INVALIDA = 0b0100  # 0100 para requisição inválida

# Função para construir a mensagem de requisição
def construir_requisicao(tipo):
    # msg_type representa o tipo da mensagem
    msg_type = (0 << 4) | tipo
    
    # `identificador` é um número aleatório de 16 bits para identificar a requisição
    identificador = random.randint(1, 65535)
    
    # A mensagem é empacotada com !BHB (1 byte para msg_type, 2 bytes para identificador, e 1 byte vazio)
    return struct.pack('!BHB', msg_type, identificador, 0), identificador


# Função para calcular o checksum
def calcular_checksum(source_string):
    # Adiciona um byte de preenchimento se o comprimento da string de origem for ímpar
    if len(source_string) % 2 == 1:
        source_string += b'\0'
    
    # Soma todos os valores de 16 bits extraídos da string
    sum_result = sum(struct.unpack('!%dH' % (len(source_string) // 2), source_string))
    
    # Faz a soma usando apenas os 16 bits menos significativos
    sum_result = (sum_result & 0xffff) + (sum_result >> 16)
    
    # Retorna o complemento de 1 da soma
    return ~sum_result


# Função para construir o cabeçalho UDP
def construir_cabecalho_udp(orig_porta, dest_porta, dados, ip_origem, ip_destino):
    # Comprimento total do pacote UDP (8 bytes de cabeçalho + dados)
    comprimento = 8 + len(dados)
    
    # Pseudo-cabeçalho IP usado no cálculo do checksum, com informações IP e de protocolo
    pseudo_header = struct.pack('!4s4sBBH', socket.inet_aton(ip_origem), socket.inet_aton(ip_destino), 0, socket.IPPROTO_UDP, comprimento)
    
    # Cabeçalho UDP sem checksum
    cabecalho_udp = struct.pack('!HHHH', orig_porta, dest_porta, comprimento, 0)
    
    # Calcula o checksum usando o pseudo-cabeçalho, cabeçalho UDP e os dados
    checksum = calcular_checksum(pseudo_header + cabecalho_udp + dados) & 0xffff
    
    # Empacota o cabeçalho UDP com o checksum calculado e adiciona os dados (payload)
    return struct.pack('!HHHH', orig_porta, dest_porta, comprimento, checksum) + dados


# Função para interpretar a resposta
def interpretar_resposta(resposta_bytes):
    # Pula os primeiros 28 bytes (20 do cabeçalho IP e 8 do cabeçalho UDP)
    resposta_bytes = resposta_bytes[28:]
    
    # Desempacota os primeiros 3 bytes da resposta para obter `msg_type` e `identificador`
    msg_type, identificador = struct.unpack('!BH', resposta_bytes[:3]) 
    
    # O 4º byte é o tamanho da resposta
    tamanho_resposta = resposta_bytes[3]
    
    # Extrai o tipo da resposta (4 bits menos significativos)
    tipo = msg_type & 0x0F
    
    # Extrai a parte dos dados da resposta
    resposta = resposta_bytes[4:4+tamanho_resposta]

    # Verifica o tipo da resposta
    if tipo == REQUISICAO_INVALIDA:
        identificador = 0
        return f"Requisição inválida {identificador}."
    elif tipo == CONTADOR_RESPOSTAS:
        contador_respostas, = struct.unpack('!I', resposta)
        return contador_respostas
    else:
        return resposta.decode('utf-8', errors='ignore')


sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

try:
    while True:
        print("\nMenu de Opções:")
        print("1 - Data e hora atual")
        print("2 - Mensagem motivacional")
        print("3 - Quantidade de respostas do servidor")
        print("4 - Sair")
        opcao = int(input("Escolha uma opção: "))

        if opcao == 4:
            print("Saindo...")
            break

        # Constrói a mensagem e o identificador da requisição
        mensagem, identificador = construir_requisicao(opcao)

        # Constrói o pacote UDP com o cabeçalho e os dados
        pacote_udp = construir_cabecalho_udp(PORTA_CLIENTE, PORTA_SERVIDOR, mensagem, IP_CLIENTE, IP_SERVIDOR)
        
        # Envia o pacote UDP para o servidor
        sock.sendto(pacote_udp, (IP_SERVIDOR, PORTA_SERVIDOR))

        # Recebe a resposta do servidor
        data, _ = sock.recvfrom(255)
        ##print(f"Tamanho dos dados recebidos: {len(data)}")

        # Interpreta a resposta do servidor
        resposta = interpretar_resposta(data)
        print(f"Resposta do servidor para o identificador {identificador}: {resposta}")

finally:
    sock.close()
    print('Socket fechado')
