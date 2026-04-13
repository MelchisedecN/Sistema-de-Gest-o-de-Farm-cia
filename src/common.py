import json
import struct

class Medicamento:
    def __init__(self, id, nome, preco, estoque):
        self.id = id
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def to_dict(self): #facilita a serealização
        return self.__dict__

class MedicamentoControlado(Medicamento):
    def __init__(self, id, nome, preco, estoque, crm_medico):
        super().__init__(id, nome, preco, estoque)
        self.crm_medico = crm_medico

class MedicamentoComum(Medicamento):
    def __init__(self, id, nome, preco, estoque):
        super().__init__(id, nome, preco, estoque)
    
class PojoOutputStream:
    # O construtor deve receber a quantidade para filtrar a lista antes de enviar (Anexo 2)
    def __init__(self, lista_objetos, quantidade, destino_stream):
        self.objetos = [obj.to_dict() for obj in lista_objetos[:quantidade]]
        self.stream = destino_stream

    def gravar(self):
        corpo_mensagem = json.dumps(self.objetos).encode('utf-8')
        print(f"--- Relatório de Saída ---")
        print(f"Total de objetos: {len(self.objetos)}")
        print(f"Bytes totais: {len(corpo_mensagem)} bytes")
        
        if hasattr(self.stream, 'sendall'): # Se for Socket
            # Para socket, envia primeiro o tamanho (4 bytes) e depois o payload.
            header = struct.pack('!I', len(corpo_mensagem))
            self.stream.sendall(header + corpo_mensagem)
        else: # Se for arquivo ou sys.stdout
            # Em arquivo/stdout textual, envia JSON em uma linha.
            self.stream.write(corpo_mensagem.decode('utf-8') + '\n')

class PojoInputStream:
    # O InputStream do Anexo 3 só precisa saber de onde ler os dados
    def __init__(self, origem_stream):
        self.stream = origem_stream

    def _recv_exato(self, total_bytes):
        """Lê exatamente N bytes de um socket ou retorna b'' em EOF."""
        chunks = []
        bytes_lidos = 0

        while bytes_lidos < total_bytes:
            chunk = self.stream.recv(total_bytes - bytes_lidos)
            if not chunk:
                return b''
            chunks.append(chunk)
            bytes_lidos += len(chunk)

        return b''.join(chunks)

    def ler(self):
        if hasattr(self.stream, 'recv'): # Se for Socket
            # Lê cabeçalho de tamanho e depois o payload completo.
            header = self._recv_exato(4)
            if not header:
                return []

            tamanho_payload = struct.unpack('!I', header)[0]
            data = self._recv_exato(tamanho_payload)
        elif hasattr(self.stream, 'read'): # Se for Arquivo
            data = self.stream.read()
        else:
            return []
            
        if not data:
            return []

        if isinstance(data, str):
            return json.loads(data)

        return json.loads(data.decode('utf-8'))