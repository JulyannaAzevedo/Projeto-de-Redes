import Cliente_udp
import Servidor
import subprocess

# Função para executar os arquivos Cliente_udp.py e Servidor.py simultaneamente
def executar_arquivos_simultaneamente(arquivo1, arquivo2):
    # Executar o primeiro arquivo em um processo separado
    processo1 = subprocess.Popen(['python', arquivo1])

    # Executar o segundo arquivo em um processo separado
    processo2 = subprocess.Popen(['python', arquivo2])

    # Esperar até que ambos os processos terminem
    processo1.wait()
    processo2.wait()

# Chamada da função para executar os arquivos simultaneamente
executar_arquivos_simultaneamente('Cliente_raw.py', 'Servidor.py')