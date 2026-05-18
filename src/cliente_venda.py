import json
from common import MedicamentoComum, MedicamentoControlado, ItemPedido, Pedido
from protocol import RMIProtocol

class FarmaciaServiceStub:
    """Provedor proxy (Stub) que traduz métodos locais em chamadas doOperation"""
    def __init__(self):
        self.protocolo = RMIProtocol() # Cliente cria porta aleatória de saída
        self.remote_obj = "ServicoFarmacia"

    def consultar_medicamento(self, id_med: int) -> dict:
        args = json.dumps({"id": id_med}).encode('utf-8')
        resposta = self.protocolo.doOperation(self.remote_obj, "consultar_medicamento", args)
        return json.loads(resposta.decode('utf-8'))

    def cadastrar_medicamento(self, medicamento_obj) -> dict:
        args = json.dumps(medicamento_obj.to_dict()).encode('utf-8')
        resposta = self.protocolo.doOperation(self.remote_obj, "cadastrar_medicamento", args)
        return json.loads(resposta.decode('utf-8'))

    def realizar_venda(self, pedido_obj: Pedido) -> dict:
        # Passagem por valor utilizando a representação externa de dados em JSON
        args = json.dumps(pedido_obj.to_dict()).encode('utf-8')
        resposta = self.protocolo.doOperation(self.remote_obj, "realizar_venda", args)
        return json.loads(resposta.decode('utf-8'))

    def verificar_retencao_receita(self, nome: str) -> dict:
        args = json.dumps({"nome": nome}).encode('utf-8')
        resposta = self.protocolo.doOperation(self.remote_obj, "verificar_retencao_receita", args)
        return json.loads(resposta.decode('utf-8'))


def executar_fluxo_cliente():
    # Instancia o Stub do serviço
    stub = FarmaciaServiceStub()

    print("\n--- [Ação 1] Verificando se Rivotril precisa de receita ---")
    resp_receita = stub.verificar_retencao_receita("Rivotril")
    print(f"Resposta do Servidor: {resp_receita}")

    print("\n--- [Ação 2] Consultando Medicamento Remotamente (ID: 1) ---")
    resp_consulta = stub.consultar_medicamento(1)
    print(f"Dados retornados: {resp_consulta}")

    print("\n--- [Ação 3] Cadastrando Novo Medicamento via RMI ---")
    novo_med = MedicamentoComum(3, "Paracetamol", 8.90, 50)
    resp_cadastro = stub.cadastrar_medicamento(novo_med)
    print(f"Status do cadastro: {resp_cadastro}")

    print("\n--- [Ação 4] Efetuando um pedido composto (Agregação/Passagem por Valor) ---")
    # Criamos as entidades locais e montamos a agregação
    m1 = MedicamentoComum(1, "Dipirona", 15.50, 100)
    m2 = MedicamentoControlado(2, "Rivotril", 80.00, 10, "CRM-12345")
    
    item1 = ItemPedido(m1, 2) # 2 Dipironas
    item2 = ItemPedido(m2, 1) # 1 Rivotril

    pedido = Pedido(id_pedido=1001)
    pedido.adicionar_item(item1)
    pedido.adicionar_item(item2)

    # Envia o objeto composto completo serializado em JSON pelo RMI
    resp_venda = stub.realizar_venda(pedido)
    print(f"Resultado final da venda: {resp_venda}")

if __name__ == "__main__":
    executar_fluxo_cliente()
