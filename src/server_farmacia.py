import socket
import threading
from common import (
    PojoInputStream,
    PojoOutputStream,
    MedicamentoComum,
    MedicamentoControlado,
)

# Configurações Multicast
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

# "Banco" simples para manter o estoque no servidor.
estoque = [MedicamentoComum(1, "Dipirona", 15.50, 100)]
estoque_lock = threading.Lock()

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


def _dict_para_medicamento(item_dict):
    """Converte dicionario recebido do cliente para POJO do dominio."""
    if "crm_medico" in item_dict:
        return MedicamentoControlado(
            item_dict.get("id", 0),
            item_dict.get("nome", ""),
            item_dict.get("preco", 0.0),
            item_dict.get("estoque", 0),
            item_dict.get("crm_medico", ""),
        )

    return MedicamentoComum(
        item_dict.get("id", 0),
        item_dict.get("nome", ""),
        item_dict.get("preco", 0.0),
        item_dict.get("estoque", 0),
    )

def lidar_com_cliente(conn, addr):
    try:
        input_stream = PojoInputStream(conn) # Use sua classe
        pedido = input_stream.ler()          # Use o método ler() dela

        if pedido:
            with estoque_lock:
                for item in pedido:
                    if verificar_receita(item['nome']):
                        print(f"Venda Registrada: {item['nome']} - R$ {item['preco']}")

                    estoque.append(_dict_para_medicamento(item))

                # Servidor empacota a reply e envia a lista atualizada.
                writer = PojoOutputStream(estoque, len(estoque), conn)
                writer.gravar()

            enviar_aviso_multicast("Atenção: Estoque de Medicamentos atualizado!")
        else:
            print(f"Conexão {addr} sem pedido válido.")
    except Exception as e:
        print(f"Erro ao lidar com cliente {addr}: {e}")
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