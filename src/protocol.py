import socket
import json

class MessageType:
    REQUEST = 0
    REPLY = 1

class RMIProtocol:
    def __init__(self, port=None, timeout=5.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if port:
            self.sock.bind(('localhost', port))
        self.sock.settimeout(timeout)
        self.request_id_counter = 0

    # Executado no CLIENTE (Bloqueante com Timeout)
    def doOperation(self, remoteObjectRef: str, methodId: str, arguments: bytes) -> bytes:
        self.request_id_counter += 1
        current_id = self.request_id_counter

        # Monta a estrutura da mensagem com base na tabela do enunciado
        packet = {
            "messageType": MessageType.REQUEST,
            "requestId": current_id,
            "objectReference": remoteObjectRef,
            "methodId": methodId,
            "arguments": arguments.decode('utf-8')
        }

        payload = json.dumps(packet).encode('utf-8')
        server_address = ('localhost', 5000)

        # Envia a requisição
        self.sock.sendto(payload, server_address)

        # Aguarda a resposta (Protocolo Requisição-Resposta com retransmissão básica)
        try:
            while True:
                data, addr = self.sock.recvfrom(65535)
                reply_packet = json.loads(data.decode('utf-8'))

                # Verifica se é a resposta correspondente à nossa requisição
                if (reply_packet["messageType"] == MessageType.REPLY and 
                    reply_packet["requestId"] == current_id):
                    return reply_packet["arguments"].encode('utf-8')
        except socket.timeout:
            print(f" [Erro] Timeout aguardando resposta do método {methodId}.")
            return json.dumps({"status": "erro", "mensagem": "Timeout no RMI"}).encode('utf-8')

    # Executado no SERVIDOR (Aguarda uma requisição)
    def getRequest(self):
        # Desativa temporariamente o timeout no servidor para ele esperar indefinidamente
        self.sock.settimeout(None)
        while True:
            data, client_addr = self.sock.recvfrom(65535)
            packet = json.loads(data.decode('utf-8'))
            if packet["messageType"] == MessageType.REQUEST:
                return packet, client_addr

    # Executado no SERVIDOR (Devolve o resultado)
    def sendReply(self, reply: bytes, requestId: int, clientHost: str, clientPort: int):
        reply_packet = {
            "messageType": MessageType.REPLY,
            "requestId": requestId,
            "objectReference": "",
            "methodId": "",
            "arguments": reply.decode('utf-8')
        }
        payload = json.dumps(reply_packet).encode('utf-8')
        self.sock.sendto(payload, (clientHost, clientPort))
