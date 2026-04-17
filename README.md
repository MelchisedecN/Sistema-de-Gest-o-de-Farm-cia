# Trabalho de Sistemas Distribuídos - Farmácia

Projeto da disciplina de Sistemas Distribuídos para demonstrar comunicação entre processos com sockets e serialização de dados.

## Descrição do projeto

Este sistema simula um cenário de farmácia distribuída com dois papéis principais:

- um cliente que monta um pedido de medicamentos e envia para o servidor;
- um servidor que recebe e processa o pedido e envia notificações para os clientes.

O foco é mostrar, de forma prática, conceitos de:

- comunicação TCP (unicast) para troca de dados confiável entre cliente e servidor;
- comunicação UDP multicast para avisos informativos em grupo;
- empacotamento e desempacotamento de dados com streams customizados.

## Funcionalidades

- Envio de lista de medicamentos do cliente para o servidor.
- Desserialização dos itens no servidor para processamento da venda.
- Simulação de validação para medicamentos controlados.
- Envio de aviso multicast após atualização do estoque.
- Atendimento concorrente no servidor com threads.

## Estrutura

- `src/common.py`: classes de domínio e streams customizados (`PojoOutputStream` e `PojoInputStream`).
- `src/server_farmacia.py`: servidor TCP multi-thread e envio de notificações por UDP multicast.
- `src/cliente_venda.py`: cliente que envia pedido via TCP e escuta avisos multicast.

## Requisitos

- Python 3.10+

## Tecnologias utilizadas

- Python 3
- `socket` (TCP e UDP multicast)
- `threading`
- `json`

## Como executar

Abra dois terminais na raiz do repositório (`dest`).

### 1. Iniciar servidor

```bash
python src/server_farmacia.py
```

Saída esperada:

```text
Servidor Fármacia Rodando (Multi-thread TCP)...
```

### 2. Executar cliente

```bash
python src/cliente_venda.py
```

Saída esperada (resumo):

- cliente envia os itens para o servidor;
- servidor registra a venda;
- cliente recebe aviso multicast.



## Fluxo de comunicação

1. Cliente empacota os itens e envia ao servidor por TCP.
2. Servidor desempacota, processa os itens e registra no log.
3. Servidor envia nota informativa por UDP multicast.
4. Cliente inscrito no grupo multicast recebe o aviso.

## Observações

- Endereço TCP do servidor: `localhost:5000`.
- Grupo multicast: `224.1.1.1:5007`.
- O servidor atende clientes concorrentes usando `threading.Thread`.
