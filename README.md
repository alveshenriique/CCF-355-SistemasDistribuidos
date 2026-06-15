# GridCity

## Descrição

O **GridCity** é um sistema distribuído colaborativo onde múltiplos usuários constroem uma cidade juntos em uma grade 7×7. Cada célula da grade pode receber uma estrutura urbana (Casa, Estrada, Hospital, etc.), e todas as alterações são sincronizadas em tempo real para todos os clientes conectados. O estado da cidade é persistido em banco de dados SQLite.

O projeto foi desenvolvido em duas etapas com abordagens distintas de comunicação distribuída:

- **Parte 3** — implementação com API de Sockets TCP e protocolo JSON manual
- **Parte 4** — reimplementação com middleware Pyro5 (RMI), visão de objetos distribuídos

---

## Estrutura do Projeto

```
GridCity/
│
├── docs/                          # Documentações do trabalho
│
├── parte3/                        # Implementação com Sockets TCP
│   ├── src/
│   │   ├── server/
│   │   │   ├── server.py          # Loop de accept, 1 thread por cliente
│   │   │   ├── state_manager.py   # Grade 7×7, SQLite, threading.Lock
│   │   │   ├── client_handler.py  # Processa mensagens e faz broadcast
│   │   │   └── models/
│   │   │       └── structure.py   # Modelo de estrutura (tipo, autor, horário)
│   │   └── client/
│   │       ├── client.py          # Ponto de entrada do cliente
│   │       ├── network.py         # NetworkClient com thread e pyqtSignal
│   │       ├── protocol.py        # Funções de criação de mensagens JSON
│   │       └── ui.py              # LoginDialog, CityGrid, MainWindow
│   ├── Makefile
│   └── requirements.txt
│
├── parte4/                        # Reimplementação com Pyro5 (RMI)
│   ├── src/
│   │   ├── server/
│   │   │   ├── server.py          # Registra objetos remotos no Name Server
│   │   │   ├── grid_manager.py    # Objeto remoto: grade 7×7 e SQLite
│   │   │   ├── session_manager.py # Objeto remoto: controle de usuários
│   │   │   └── models/
│   │   │       └── structure.py   # Modelo de estrutura (tipo, autor, horário)
│   │   └── client/
│   │       ├── client.py          # Ponto de entrada do cliente
│   │       ├── network.py         # Proxies Pyro5 e polling periódico
│   │       └── ui.py              # LoginDialog, CityGrid, MainWindow
│   ├── Makefile
│   └── requirements.txt
```

---

## Funcionalidades

- Login com nome de usuário
- Visualização da grade 7×7 em tempo real
- Colocação de estruturas em células vazias
- Remoção de estruturas
- Exibição dos usuários conectados
- Identificação de autor e horário de cada estrutura
- Persistência do mapa entre sessões do servidor

**Estruturas disponíveis:** Casa, Estrada, Hospital, Loja, Praça, Escola, Parque, Fábrica

---

## Como Executar

### Requisitos do sistema

- Ubuntu 22.04
- Python 3.10 ou superior

```bash
sudo apt-get install libxcb-cursor0
```

### 1. Clonar o repositório

```bash
git clone https://github.com/alveshenriique/CCF-355-SistemasDistribuidos.git
cd CCF-355-SistemasDistribuidos
```

---

### Parte 3 — Sockets TCP

```bash
cd parte3
make install
```

**Terminal 1 — Servidor:**
```bash
make server
```

**Terminal 2 — Cliente:**
```bash
make client
```

> Para simular múltiplos usuários, abra mais terminais e execute `make client` em cada um.

**Resetar o mapa:**
```bash
rm cidade.db
```

---

### Parte 4 — Pyro5 (RMI)

```bash
cd parte4
make install
```

**Terminal 1 — Name Server** (deve permanecer ativo durante toda a execução):
```bash
make nameserver
```

**Terminal 2 — Servidor** (iniciar somente após o Name Server estar ativo):
```bash
make server
```

**Terminal 3 — Cliente:**
```bash
make client
```

> Para simular múltiplos usuários, abra mais terminais e execute `make client` em cada um.

**Resetar o mapa:**
```bash
rm cidade.db
```

---

## Tecnologias Utilizadas

- Python 3.10+
- Sockets TCP — módulo `socket` (Parte 3)
- Pyro5 — middleware RMI (Parte 4)
- PyQt6 — interface gráfica
- SQLite — persistência via módulo `sqlite3`
- Threading — módulo `threading`

---

## Contexto Acadêmico

Projeto desenvolvido para a disciplina de **Sistemas Distribuídos** — UFV Campus Florestal, 2026/01.
Professora: Thais Regina de M. B. Silva

Partes 3 e 4 do trabalho prático — implementação com API de Sockets (visão de processos) e reimplementação com Pyro5 (visão de objetos).

---

## Autores

- Henrique Alves Campos — Protocolo e Comunicação
- Henrique de Souza Campos — Servidor e Persistência
- Heron Fillipe Silveira Santos — Interface Gráfica

---

## Licença

Este projeto é destinado exclusivamente para fins acadêmicos.
