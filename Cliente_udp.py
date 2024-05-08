import socket
import struct
import random
import time

# Endereço e porta do servidor
SERVIDOR_IP = "127.0.0.1"
SERVIDOR_PORTA = 50000 
MAX_BYTES = 1024

# Função para construir o cabeçalho UDP
def construir_cabecalho_udp(porta_origem, porta_destino, comprimento):
    checksum = 0  # O checksum será calculado posteriormente
    return struct.pack("!HHHH", porta_origem, porta_destino, comprimento, checksum)

# Função para construir a mensagem de requisição
def construir_requisicao(porta_origem, porta_destino, identificador, tipo_requisicao):
    cabecalho_udp = construir_cabecalho_udp(porta_origem, porta_destino, 0)  # Tamanho inicial 0, será ajustado posteriormente
    tipo_resposta = 0  # Tipo de requisição
    comprimento_resposta = 0  # Tamanho inicial da resposta
    return struct.pack("!BBHH", tipo_resposta, tipo_requisicao, identificador, comprimento_resposta) + cabecalho_udp

# Função para enviar requisição ao servidor e receber resposta
def enviar_requisicao(requisicao):
    try:
        # Criar um socket UDP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Enviar a requisição para o servidor
        s.sendto(requisicao, (SERVIDOR_IP, SERVIDOR_PORTA))

        # Receber a resposta do servidor
        resposta, _ = s.recvfrom(1024)  # Tamanho do buffer pode ser ajustado conforme necessário
        return resposta

    finally:
        s.close()  # Fechar o socket após o término

# Função para exibir a resposta recebida
def exibir_resposta(resposta):
    tipo_resposta, tipo_requisicao, identificador, comprimento_resposta = struct.unpack("!BBHH", resposta[:6])
    # Verificar o tipo de resposta
    if tipo_resposta == 0:  # Requisição
        print("Requisição inválida.")
    elif tipo_resposta == 1:  # Resposta
        if tipo_requisicao == 0: 
            print("Data e Hora Atual:", resposta[7:].decode())
        elif tipo_requisicao == 1: 
            print("Mensagem Motivacional:", resposta[7:].decode())  # Corrigindo o índice para 7
        elif tipo_requisicao == 2:
            num_respostas = struct.unpack("!B", resposta[6:7])[0]
            print("Quantidade de Respostas:", num_respostas)

# Função principal do cliente
def cliente():
    
    while True:
        # Solicitar entrada do usuário para selecionar o tipo de requisição
        print("\nEscolha o tipo de requisição:")
        print("1. Data e hora atual")
        print("2. Mensagem motivacional para o fim do semestre")
        print("3. Quantidade de respostas enviadas pelo servidor até o momento")
        print("4. Sair")

        escolha = input("\nDigite o número da opção desejada: ")

        if escolha == "4":
            print("Cliente encerrado...")
            break

        # Construir a requisição de acordo com a escolha do usuário
        if escolha in ["1", "2", "3"]:
            identificador = random.randint(1, 65535)  # Número de identificação (pode ser aleatório)
            tipo_requisicao = int(escolha) - 1  # Converte a escolha do usuário para o tipo de requisição
            requisicao = construir_requisicao(59155, SERVIDOR_PORTA, identificador, tipo_requisicao)

            # Enviar a requisição para o servidor e receber a resposta
            resposta = enviar_requisicao(requisicao)

            # Exibir a resposta recebida
            exibir_resposta(resposta)

            # Adicionar atraso aleatório
            time.sleep(random.uniform(0.5, 2.0))

# Chamada da função principal do cliente
if __name__ == "__main__":
    cliente()