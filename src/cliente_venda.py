import socket
import struct
from common import MedicamentoComum, MedicamentoControlado, PojoOutputStream, PojoInputStream

def escutar_aviso_multicast():
    #Ouve mensagens UDP enviadas pelo servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 5007)) #escuta em todas as interfaces

    mreq = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print("Aguardando avisos do sistema...")
    while True:
        data, _= sock.recvfrom(1024)
        print(f"Aviso recebido: {data.decode('utf-8')}")

def realizar_venda():
    #Cria objetos, vendas
    m1 = MedicamentoComum(1, "Dipirona", 15.50, 100)
    m2 = MedicamentoControlado(2, "Rivotril", 80.00, 10, "CRM-12345")
    lista = [m1, m2]

    #Conectando ao servidor TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_venda:
        sock_venda.connect(('localhost', 5000))

        # Cliente empacota e envia o request.
        output_stream = PojoOutputStream(lista, len(lista), sock_venda)
        output_stream.gravar()

        # Cliente desempacota o reply enviado pelo servidor.
        input_stream = PojoInputStream(sock_venda)
        resposta = input_stream.ler()

        print(f"Servidor retornou {len(resposta)} item(ns) no estoque:")
        for item in resposta:
            print(f"  - {item}")

if __name__ == "__main__":
    import threading
    
    # Inicia a escuta de avisos em uma thread separada para não travar o programa
    thread_avisos = threading.Thread(target=escutar_aviso_multicast, daemon=True)
    thread_avisos.start()
    
    # Agora você pode realizar vendas à vontade
    realizar_venda()
    
    # Mantém o programa vivo para ver os avisos chegando
    input("Pressione Enter para sair...\n")
