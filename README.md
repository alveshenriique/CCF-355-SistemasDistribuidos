# GridCity

## Descrição

O **GridCity** é um sistema distribuído colaborativo onde múltiplos usuários se conectam a um servidor central via TCP e constroem uma cidade juntos em uma grade 7x7. Cada célula da grade pode receber uma estrutura urbana (Casa, Estrada, Hospital, etc.), e todas as alterações são sincronizadas em tempo real para todos os clientes conectados.

O estado da cidade é persistido em banco de dados SQLite, garantindo que o mapa seja restaurado mesmo após reinicializações do servidor.

---

## Arquitetura

O sistema segue o modelo **cliente-servidor TCP centralizado**:

**Servidor**
- Aceita conexões de múltiplos clientes, criando uma thread por conexão
- Gerencia o estado global da grade 7x7 com `threading.Lock`
- Valida operações de PLACE e REMOVE
- Propaga atualizações para todos os clientes via broadcast
- Persiste o mapa em `cidade.db` (SQLite)

**Cliente**
- Interface gráfica desenvolvida em PyQt6
- Thread dedicada para comunicação com o servidor (não bloqueia a UI)
- Recebe atualizações em tempo real via sinais Qt (`pyqtSignal`)

---

## Funcionalidades

- Login com nome de usuário
- Visualização da grade 7x7 em tempo real
- Colocação de estruturas em células vazias
- Remoção de estruturas pelo autor original
- Exibição do número de usuários conectados
- Identificação de autor e horário de cada estrutura
- Persistência do mapa entre sessões do servidor

**Estruturas disponíveis:** Casa, Estrada, Hospital, Loja, Praça, Escola, Parque, Fábrica

---

## Estrutura do Projeto

```
GridCity/
│
├── docs/                        # Enunciados do trabalho
│
├── src/
│   ├── server/
│   │   ├── server.py            # Aceita conexões, cria 1 thread por cliente
│   │   ├── state_manager.py     # Grade 7x7, SQLite, threading.Lock
│   │   ├── client_handler.py    # Processa mensagens e faz broadcast
│   │   └── models/
│   │       └── structure.py     # Modelo de estrutura (tipo, autor, horário)
│   │
│   └── client/
│       ├── client.py            # Ponto de entrada do cliente
│       ├── network.py           # NetworkClient com thread e pyqtSignal
│       ├── protocol.py          # Funções de criação de mensagens JSON
│       └── ui.py                # LoginDialog, CityGrid (QPainter), MainWindow
│
├── requirements.txt
├── Makefile
└── cidade.db                    # Gerado automaticamente pelo servidor
```

---

## Protocolo de Mensagens

A comunicação é feita via **TCP com mensagens JSON** separadas por `\n`.

### Cliente → Servidor

```json
{ "type": "JOIN", "username": "Henrique" }
{ "type": "PLACE", "x": 3, "y": 5, "structure_type": "Casa", "author": "Henrique" }
{ "type": "REMOVE", "x": 3, "y": 5 }
```

### Servidor → Cliente

```json
{ "type": "UPDATE", "state": [[...]] }
{ "type": "USERS", "count": 2, "usernames": ["Henrique", "Heron"] }
{ "type": "RESPONSE", "success": true, "message": "Estrutura alocada", "action": "PLACE", "x": 3, "y": 5, "structure_type": "Casa" }
```

---

## Uso de Threads

| Local | Thread | Finalidade |
|---|---|---|
| Servidor | 1 por cliente conectado | Processar mensagens de cada cliente de forma independente |
| Cliente | 1 thread de rede | Receber mensagens do servidor sem bloquear a interface Qt |

O `StateManager` usa `threading.Lock` para proteger toda leitura e escrita na grade, evitando condições de corrida entre as threads do servidor.

---

## Como Executar 🚀

### Requisitos do sistema

- Ubuntu 22.04
- Python 3.10 ou superior
- Dependência de sistema:

```bash
sudo apt-get install libxcb-cursor0
```

### 1. Clonar o repositório

```bash
git clone https://github.com/alveshenriique/CCF-355-SistemasDistribuidos.git
cd CCF-355-SistemasDistribuidos
```

### 2. Instalar dependências Python

```bash
make install
```

### 3. Iniciar o servidor

```bash
make server
```

### 4. Iniciar o cliente (em outro terminal)

```bash
make client
```

> Para simular múltiplos usuários, abra mais terminais e execute `make client` em cada um.

### Resetar o mapa (opcional)

```bash
rm cidade.db
```

---

## Tecnologias Utilizadas

- Python 3.10+
- Sockets TCP (módulo `socket`)
- PyQt6 (interface gráfica)
- SQLite (persistência via módulo `sqlite3`)
- Threading (módulo `threading`)

---

## Contexto Acadêmico

Projeto desenvolvido para a disciplina de **Sistemas Distribuídos** — UFV Campus Florestal, 2026/01.
Professora: Thais Regina de M. B. Silva

Parte 3 de 4 do trabalho prático — implementação com API de Sockets (visão de processos).
A Parte 4 utilizará RMI (visão de objetos).

---

## Autores

- Henrique Alves Campos — Protocolo e Comunicação
- Henrique de Souza Campos — Servidor e Persistência
- Heron Fillipe Silveira Santos — Interface Gráfica

---

## Licença

Este projeto é destinado exclusivamente para fins acadêmicos.
