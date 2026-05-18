import json
from protocol import RMIProtocol

class ServicoFarmacia:
    """Implementação real do serviço rodando localmente no Servidor"""
    def __init__(self):
        # Banco de dados simulado
        self.estoque = {
            1: {"nome": "Dipirona", "preco": 15.50, "estoque": 100, "controlado": False},
            2: {"nome": "Rivotril", "preco": 80.00, "estoque": 10, "controlado": True}
        }

    # MÉTODO REMOTO 1: Consultar estoque por ID
    def consultar_medicamento(self, id_med: int) -> dict:
        med = self.estoque.get(id_med)
        if med:
            return {"status": "sucesso", "dados": med}
        return {"status": "erro", "mensagem": "Medicamento não localizado"}

    # MÉTODO REMOTO 2: Adicionar novo medicamento ao estoque
    def cadastrar_medicamento(self, dados_med: dict) -> dict:
        id_med = dados_med.get("id")
        self.estoque[id_med] = {
            "nome": dados_med.get("nome"),
            "preco": dados_med.get("preco"),
            "estoque": dados_med.get("estoque"),
            "controlado": dados_med.get("crm_medico") is not None
        }
        print(f" [+] Novo item cadastrado via RMI: {dados_med.get('nome')}")
        return {"status": "sucesso", "mensagem": "Medicamento cadastrado"}

    # MÉTODO REMOTO 3: Processar uma venda complexa (Passagem por valor/JSON)
    def realizar_venda(self, pedido_dict: dict) -> dict:
        print(f" [Venda] Processando requisição de pedido ID: {pedido_dict['id_pedido']}")
        for item in pedido_dict["itens"]:
            med_id = item["medicamento"]["id"]
            qtd = item["quantidade"]

            if med_id not in self.estoque or self.estoque[med_id]["estoque"] < qtd:
                return {"status": "erro", "mensagem": f"Estoque insuficiente de {item['medicamento']['nome']}"}
            
            # Se for controlado, valida se o cliente passou o CRM
            if self.estoque[med_id]["controlado"] and "crm_medico" not in item["medicamento"]:
                return {"status": "erro", "mensagem": f"Venda negada: {item['medicamento']['nome']} exige CRM."}

        # Deduz do estoque se tudo estiver correto
        for item in pedido_dict["itens"]:
            med_id = item["medicamento"]["id"]
            self.estoque[med_id]["estoque"] -= item["quantidade"]
            print(f" [Estoque Atualizado] {self.estoque[med_id]['nome']} resta(m): {self.estoque[med_id]['estoque']}")

        return {"status": "sucesso", "mensagem": "Venda concluída com sucesso!"}

    # MÉTODO REMOTO 4: Verificar se um determinado nome precisa de retenção de receita
    def verificar_retencao_receita(self, nome_medicamento: str) -> dict:
        for med in self.estoque.values():
            if med["nome"].lower() == nome_medicamento.lower():
                return {"status": "sucesso", "exige_receita": med["controlado"]}
        return {"status": "erro", "mensagem": "Medicamento não encontrado para checagem"}


def iniciar_servidor():
    protocolo = RMIProtocol(port=5000)
    servico = ServicoFarmacia()
    print("=== Servidor de Objeto Remoto (RMI) Ativo na porta 5000 ===")

    while True:
        # 1. getRequest() aguarda uma mensagem estruturada via rede
        packet, client_addr = protocolo.getRequest()
        
        obj_ref = packet["objectReference"]
        method_name = packet["methodId"]
        req_id = packet["requestId"]
        # Passagem por valor: deserializa o argumento JSON recebido em formato texto
        args_deserializados = json.loads(packet["arguments"])

        print(f" -> Requisição RMI recebida para o objeto '{obj_ref}', método '{method_name}'")

        # 2. Despachante (Dispatcher): mapeia os nomes de métodos strings para a execução real
        resultado = {"status": "erro", "mensagem": "Método ou Objeto remoto inválido"}

        if obj_ref == "ServicoFarmacia":
            if method_name == "consultar_medicamento":
                resultado = servico.consultar_medicamento(args_deserializados["id"])
            elif method_name == "cadastrar_medicamento":
                resultado = servico.cadastrar_medicamento(args_deserializados)
            elif method_name == "realizar_venda":
                resultado = servico.realizar_venda(args_deserializados)
            elif method_name == "verificar_retencao_receita":
                resultado = servico.verificar_retencao_receita(args_deserializados["nome"])

        # 3. sendReply() envia os dados convertidos de volta para o cliente
        reply_bytes = json.dumps(resultado).encode('utf-8')
        protocolo.sendReply(reply_bytes, req_id, client_addr[0], client_addr[1])

if __name__ == "__main__":
    iniciar_servidor()
