import json

class Medicamento:
    def __init__(self, id_med, nome, preco, estoque):
        self.id = id_med
        self.nome = nome
        self.preco = preco
        self.estoque = estoque

    def to_dict(self):
        return self.__dict__

class MedicamentoComum(Medicamento):
    def __init__(self, id_med, nome, preco, estoque):
        super().__init__(id_med, nome, preco, estoque)

class MedicamentoControlado(Medicamento):
    def __init__(self, id_med, nome, preco, estoque, crm_medico):
        super().__init__(id_med, nome, preco, estoque)
        self.crm_medico = crm_medico

class ItemPedido:
    """Um ItemPedido 'tem-um' Medicamento e uma quantidade."""
    def __init__(self, medicamento: Medicamento, quantidade: int):
        self.medicamento = medicamento
        self.quantidade = quantidade

    def to_dict(self):
        return {
            "medicamento": self.medicamento.to_dict(),
            "quantidade": self.quantidade
        }

class Pedido:
    """Um Pedido 'tem-uma' lista de ItemPedido."""
    def __init__(self, id_pedido: int):
        self.id_pedido = id_pedido
        self.itens = [] # Lista de objetos ItemPedido

    def adicionar_item(self, item: ItemPedido):
        self.itens.append(item)

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "itens": [item.to_dict() for item in self.itens]
        }
