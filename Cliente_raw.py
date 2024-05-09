import random  # Importa o módulo random para gerar números aleatórios
import socket  # Importa o módulo socket para comunicação em rede
import struct  # Importa o módulo struct para empacotamento e desempacotamento de dados binários

# Configurações do servidor
ip_servidor = '127.0.0.1'  
porta_servidor = 50000  

# Configurações do cliente
ip_cliente = '127.0.0.1'  # local para testes
porta_cliente = 59155  

# Escolhas possíveis
tempoData = 0b0001  # Define a opção para obter data e hora atual
mensagemMotivacional = 0b0010  # Define a opção para receber uma mensagem motivacional
respostasContagem = 0b0011  # Define a opção para obter a quantidade de respostas do servidor
requisicaoInvalida = 0b0100  # Define a opção para indicar uma requisição inválida

def interpretar_resposta(bytes_resposta):
    """
    Interpreta a resposta recebida do servidor.
    
    Args:
        bytes_resposta (bytes): Os bytes da resposta recebida.
    
    Returns:
        str or int: A mensagem interpretada ou a quantidade de respostas.
    """
    # Ignora os primeiros 28 bytes (20 do cabeçalho IP e 8 do cabeçalho UDP)
    bytes_resposta = bytes_resposta[28:]
    
    # Extrai o tipo de mensagem e o identificador da resposta
    tipo_mensagem, identificador = struct.unpack('!BH', bytes_resposta[:3])
    
    # Obtém o tamanho da resposta
    tamanho_resposta = bytes_resposta[3]
    
    # Extrai o tipo da resposta (4 bits menos significativos)
    tipo_resposta = tipo_mensagem & 0x0F
    
    # Extrai os dados da resposta
    resposta = bytes_resposta[4:4 + tamanho_resposta]

    # Verifica o tipo de resposta e retorna a mensagem correspondente
    if tipo_resposta == requisicaoInvalida:
        identificador = 0
        return f"Requisição inválida {identificador}."
    elif tipo_resposta == respostasContagem:
        contador_respostas, = struct.unpack('!I', resposta)
        return contador_respostas
    else:
        return resposta.decode('utf-8', errors='ignore')


def criar_cabecalho_udp(porta_origem, porta_destino, dados, ip_origem, ip_destino):
    """
    Cria o cabeçalho UDP para empacotar os dados a serem enviados.
    
    Args:
        porta_origem (int): A porta de origem do pacote.
        porta_destino (int): A porta de destino do pacote.
        dados (bytes): Os dados a serem empacotados.
        ip_origem (str): O endereço IP de origem.
        ip_destino (str): O endereço IP de destino.
    
    Returns:
        bytes: O cabeçalho UDP empacotado juntamente com os dados.
    """
    comprimento = 8 + len(dados)
    
    pseudo_cabecalho = struct.pack('!4s4sBBH', socket.inet_aton(ip_origem), socket.inet_aton(ip_destino), 0, socket.IPPROTO_UDP, comprimento)
    
    cabecalho_udp = struct.pack('!HHHH', porta_origem, porta_destino, comprimento, 0)
    
    checksum_soma = calcular_checksum(pseudo_cabecalho + cabecalho_udp + dados) & 0xffff
    
    return struct.pack('!HHHH', porta_origem, porta_destino, comprimento, checksum_soma) + dados


def criar_requisicao(escolha):
    """
    Cria uma requisição para enviar ao servidor.
    
    Args:
        escolha (int): A opção escolhida pelo cliente.
    
    Returns:
        tuple: Uma tupla contendo a mensagem da requisição e o identificador.
    """
    tipo_mensagem = (0 << 4) | escolha
    
    identificador = random.randint(1, 65535)
    
    return struct.pack('!BHB', tipo_mensagem, identificador, 0), identificador


def calcular_checksum(string_fonte):
    """
    Calcula o checksum da string de origem para verificação de integridade dos dados.
    
    Args:
        string_fonte (bytes): A string de origem para calcular o checksum.
    
    Returns:
        int: O checksum calculado.
    """
    if len(string_fonte) % 2 == 1:
        string_fonte += b'\0'
    
    checksum_soma = sum(struct.unpack('!%dH' % (len(string_fonte) // 2), string_fonte))
    
    checksum_soma = (checksum_soma & 0xffff) + (checksum_soma >> 16)
    
    return ~checksum_soma


# Montando o socket
sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

try:
    while True:
        print("\n\nMenu de Opções:")
        print("1 - Data e hora atual")
        print("2 - Uma mensagem motivacional para o fim do semestre")
        print("3 - Quantidade de respostas emitidas pelo servidor até o momento")
        print("4 - Sair")
        escolha = int(input("Escolha uma opção: "))

        # Se o usuário escolheu sair
        if escolha == 4:
            break

        mensagem, identificador = criar_requisicao(escolha)    
        pacote_udp = criar_cabecalho_udp(porta_cliente, porta_servidor, mensagem, ip_cliente, ip_servidor)  
        sock.sendto(pacote_udp, (ip_servidor, porta_servidor))

        # Resposta servidor 
        conteudo, _ = sock.recvfrom(255)          
        resposta = interpretar_resposta(conteudo)
        
        print(f"\n\n{resposta}")

finally:
    sock.close()
    print('\nCanal de atendimento fechado')