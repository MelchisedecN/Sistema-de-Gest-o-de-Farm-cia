import socket
import json
import struct
import threading
from common import PojoInputStream

# Configurações Multicast
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

def verificar_receita(medicamento_nome):
    #simulação de interface
    if "Controlado" in medicamento_nome:
        print(f"Alerta: Verificando receita para {medicamento_nome}...")
        return True
    return True

def enviar_aviso_multicast(mensagem):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.sendto(mensagem.encode('utf-8'), (MCAST_GRP, MCAST_PORT))
    print(f"Aviso multicast enviado: {mensagem}")

def lidar_com_cliente(conn, addr):
    try:
        input_stream = PojoInputStream(conn) # Use sua classe
        pedido = input_stream.ler()          # Use o método ler() dela
        if pedido:
            for item in pedido:
                if verificar_receita(item['nome']):
                    print(f"Venda Registrada: {item['nome']} - R$ {item['preco']}")
            enviar_aviso_multicast("Atenção: Estoque de Medicamentos atualizado!")
    finally:
        conn.close()

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(5)
    print("Servidor Fármacia Rodando (Multi-thread TCP)...")

    while True:
        conn, addr = server.accept()
        # Aqui a mágica acontece: cria uma thread para cada novo cliente
        thread = threading.Thread(target=lidar_com_cliente, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()