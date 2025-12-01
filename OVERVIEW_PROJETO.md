# Overview do Projeto - Multiplicação de Matrizes Distribuída

## 📋 Sumário Executivo

Este projeto implementa um sistema de **multiplicação de matrizes distribuída** usando **computação paralela e concorrente** em Python. O sistema utiliza uma arquitetura **cliente-servidor** com **sockets TCP** e **threading** para distribuir o processamento entre múltiplos clientes.

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios

```
matmul-distribuida/
├── src/matmul/
│   ├── server/
│   │   └── main.py          # Servidor coordenador
│   ├── client/
│   │   └── main.py          # Cliente worker
│   └── utils/
│       ├── protocol.py      # Protocolo de comunicação
│       └── matrix_utils.py  # Operações com matrizes
├── requirements.txt
└── README.md
```

### Componentes Principais

1. **Servidor (`server/main.py`)**: Coordenador central que distribui tarefas
2. **Cliente (`client/main.py`)**: Worker que processa blocos de matriz
3. **Protocolo (`utils/protocol.py`)**: Comunicação via JSON sobre TCP
4. **Utilitários (`utils/matrix_utils.py`)**: Operações matemáticas com matrizes

---

## 🔄 Fluxo de Execução Completo

### 1️⃣ Inicialização do Servidor

```
┌─────────────────────────────────────────┐
│ SERVIDOR INICIA                         │
│ - Define HOST:PORT (127.0.0.1:5000)     │
│ - Solicita dimensões das matrizes       │
│ - Gera matrizes A e B aleatoriamente    │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 78-91):
- Lê dimensões: `rows_A`, `cols_A`, `cols_B`
- Gera `A` (rows_A × cols_A) e `B` (cols_A × cols_B)

### 2️⃣ Cálculo Sequencial (Baseline)

```
┌─────────────────────────────────────────┐
│ EXECUÇÃO SEQUENCIAL                     │
│ - Calcula C_seq = A × B localmente      │
│ - Mede tempo de execução                │
│ - Serve como baseline para comparação   │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 96-102):
- `C_seq = multiply(A, B)` - multiplicação tradicional O(n³)
- Armazena tempo para comparação com versão distribuída

### 3️⃣ Divisão da Matriz A em Blocos

```
┌─────────────────────────────────────────┐
│ PARTICIONAMENTO                         │
│ - Divide A em N blocos horizontais      │
│ - N = número de clientes esperados      │
│ - Cada bloco tem ~(rows_A/N) linhas     │
└─────────────────────────────────────────┘

Exemplo: A(6×4) com 2 clientes
┌─────────┐
│ Bloco 0 │ → 3 linhas → Cliente 1
├─────────┤
│ Bloco 1 │ → 3 linhas → Cliente 2
└─────────┘
```

**Código relevante** (`server/main.py`, linhas 105-106):
- `blocks = split_matrix_by_rows(A, num_clients)`
- Função em `matrix_utils.py` (linhas 41-66) distribui linhas uniformemente

### 4️⃣ Servidor Aguarda Conexões

```
┌─────────────────────────────────────────┐
│ SERVIDOR ESCUTA                         │
│ - Cria socket TCP                       │
│ - Bind em HOST:PORT                     │
│ - Listen para N clientes                │
│ - Aceita conexões sequencialmente       │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 113-126):
- Socket com `SO_REUSEADDR` para reutilização rápida
- Loop aceita exatamente `num_clients` conexões

### 5️⃣ Clientes Conectam e Recebem Tarefas

```
┌──────────────┐                    ┌──────────────┐
│  CLIENTE 1   │◄───────────────────┤   SERVIDOR   │
│              │  Envia:            │              │
│              │  - block_index: 0  │              │
│              │  - A_block (3×4)   │              │
│              │  - B (4×5)         │              │
└──────────────┘                    └──────────────┘
       ▲                                    │
       │                                    ▼
       │                            ┌──────────────┐
       └────────────────────────────┤  CLIENTE 2   │
                                    │              │
                                    │ block_index:1│
                                    └──────────────┘
```

**Protocolo de Comunicação** (`protocol.py`):

```python
# Mensagem enviada pelo servidor
{
    "type": "task",
    "block_index": 0,
    "A_block": [[1, 2, 3, 4], [5, 6, 7, 8], ...],
    "B": [[...], [...], ...]
}
```

**Formato de Transmissão**:
1. **4 bytes**: Tamanho do JSON (big-endian)
2. **N bytes**: Payload JSON em UTF-8

### 6️⃣ Processamento Paralelo nos Clientes

```
┌──────────────────────────────────────────┐
│ CLIENTE PROCESSA                         │
│ 1. Recebe A_block e B                    │
│ 2. Calcula C_block = A_block × B         │
│ 3. Envia resultado de volta              │
└──────────────────────────────────────────┘

Exemplo:
A_block (3×4) × B (4×5) = C_block (3×5)
```

**Código relevante** (`client/main.py`, linhas 38-52):
- `C_block = multiply(A_block, B)` - multiplicação local
- Envia resposta com `block_index` para ordenação

**Algoritmo de Multiplicação** (`matrix_utils.py`, linhas 15-39):
```python
# Multiplicação clássica O(n³)
for i in range(n):
    for j in range(p):
        soma = 0
        for k in range(m):
            soma += A[i][k] * B[k][j]
        C[i][j] = soma
```

### 7️⃣ Threading no Servidor

```
┌─────────────────────────────────────────┐
│ SERVIDOR CRIA THREADS                   │
│                                         │
│ Thread 1 ──► handle_client(Cliente 1)  │
│ Thread 2 ──► handle_client(Cliente 2)  │
│ ...                                     │
│ Thread N ──► handle_client(Cliente N)  │
│                                         │
│ Todas executam CONCORRENTEMENTE         │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 130-136):
- Cada conexão gera uma thread daemon
- Threads executam `handle_client()` em paralelo
- Lock protege dicionário compartilhado `results`

### 8️⃣ Sincronização e Coleta de Resultados

```
┌─────────────────────────────────────────┐
│ SINCRONIZAÇÃO                           │
│                                         │
│ results = {}  ◄─── Lock protegido      │
│                                         │
│ Thread 1 ──► results[0] = C_block_0    │
│ Thread 2 ──► results[1] = C_block_1    │
│                                         │
│ servidor.join() ──► Aguarda todas      │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 60-62):
```python
with lock:
    results[result_block_index] = C_block
```

### 9️⃣ Reconstrução da Matriz Final

```
┌─────────────────────────────────────────┐
│ CONCATENAÇÃO                            │
│                                         │
│ results = {0: C_block_0, 1: C_block_1}  │
│                                         │
│ C = []                                  │
│ for idx in sorted(results.keys()):     │
│     C.extend(results[idx])             │
│                                         │
│ C = [linha1, linha2, ..., linha6]      │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 151-153):
- Ordena blocos por índice
- Concatena linhas na ordem correta

### 🔟 Validação e Comparação

```
┌─────────────────────────────────────────┐
│ VALIDAÇÃO                               │
│                                         │
│ C_seq == C_distribuído? ✓               │
│                                         │
│ Tempo sequencial:   0.0023s             │
│ Tempo distribuído:  0.0015s             │
│ Speedup: 1.53x                          │
└─────────────────────────────────────────┘
```

**Código relevante** (`server/main.py`, linhas 159-161):
- Compara resultado distribuído com baseline
- Mede tempo total de execução distribuída

---

## 🧵 Conceitos de Computação Paralela e Concorrente

### Paralelismo de Dados (Data Parallelism)

O projeto usa **paralelismo de dados** ao dividir a matriz A em blocos:

```
Tarefa: A × B = C

Decomposição:
┌─────────┐     ┌───┐     ┌─────────┐
│ A_0     │  ×  │ B │  =  │ C_0     │  ← Cliente 1
├─────────┤     ├───┤     ├─────────┤
│ A_1     │  ×  │ B │  =  │ C_1     │  ← Cliente 2
└─────────┘     └───┘     └─────────┘

Propriedade: Cada cliente executa a MESMA operação (multiplicação)
             em DADOS DIFERENTES (blocos de A)
```

### Concorrência com Threading

**Threads no Servidor**:
- Múltiplas threads executam simultaneamente
- Compartilham memória (dicionário `results`)
- Sincronização via `threading.Lock()`

```python
# Região crítica protegida
with lock:
    results[block_index] = C_block  # Acesso exclusivo
```

### Comunicação via Sockets TCP

**Modelo Cliente-Servidor**:
- **Servidor**: Coordenador central (1 processo)
- **Clientes**: Workers distribuídos (N processos)
- **Protocolo**: JSON sobre TCP com framing

**Vantagens**:
- ✅ Clientes podem estar em máquinas diferentes
- ✅ Protocolo simples e extensível
- ✅ Confiabilidade do TCP

---

## 📊 Análise de Desempenho

### Complexidade Computacional

**Multiplicação de Matrizes**:
- A (n × m) × B (m × p) = C (n × p)
- Complexidade: **O(n × m × p)**

**Versão Sequencial**:
- Tempo: T_seq = O(n × m × p)

**Versão Distribuída com k clientes**:
- Cada cliente processa n/k linhas
- Tempo ideal: T_dist = O((n/k) × m × p)
- **Speedup teórico**: k

### Overhead da Distribuição

**Custos adicionais**:
1. **Serialização**: Conversão matriz → JSON
2. **Transmissão**: Envio via rede (mesmo local)
3. **Sincronização**: Lock e join de threads
4. **Reconstrução**: Concatenação de blocos

**Trade-off**:
- Matrizes pequenas: Overhead > Ganho paralelo
- Matrizes grandes: Ganho paralelo > Overhead

---

## 🔧 Detalhamento Técnico das Funções

### `protocol.py`

#### `send_json(sock, data)`
**Propósito**: Envia dicionário Python via socket

**Implementação**:
```python
1. Serializa dict → JSON string
2. Codifica string → bytes UTF-8
3. Calcula tamanho (4 bytes big-endian)
4. Envia: [tamanho][payload]
```

**Por que usar framing?**
- TCP é stream-based (não tem delimitadores de mensagem)
- Cabeçalho de tamanho permite ler exatamente N bytes

#### `recv_json(sock)`
**Propósito**: Recebe JSON do socket

**Implementação**:
```python
1. Lê 4 bytes → tamanho
2. Lê exatamente 'tamanho' bytes → payload
3. Decodifica UTF-8 → string
4. Deserializa JSON → dict
```

#### `recv_exactly(sock, size)`
**Propósito**: Garante leitura completa de N bytes

**Por que necessário?**
- `sock.recv(N)` pode retornar < N bytes
- Loop acumula chunks até completar N bytes

---

### `matrix_utils.py`

#### `generate_matrix(rows, cols, min_val, max_val)`
**Propósito**: Cria matriz aleatória para testes

**Implementação**:
```python
[[random.randint(min_val, max_val) for _ in range(cols)]
 for _ in range(rows)]
```

#### `multiply(A, B)`
**Propósito**: Multiplicação clássica de matrizes

**Algoritmo**:
```
Para cada elemento C[i][j]:
    C[i][j] = Σ(k=0 até m-1) A[i][k] × B[k][j]
```

**Validação**:
- Verifica compatibilidade: `cols(A) == rows(B)`

#### `split_matrix_by_rows(A, num_parts)`
**Propósito**: Divide matriz em blocos horizontais

**Algoritmo**:
```python
block_size = rows // num_parts
remainder = rows % num_parts

# Distribui linhas extras nos primeiros blocos
for i in range(num_parts):
    extra = 1 if i < remainder else 0
    tamanho_bloco = block_size + extra
```

**Exemplo**:
- A com 10 linhas, 3 clientes
- Blocos: [4 linhas, 3 linhas, 3 linhas]

---

### `server/main.py`

#### `handle_client(conn, addr, block_index, A_block, B, results, lock)`
**Propósito**: Thread que gerencia comunicação com 1 cliente

**Fluxo**:
```
1. Monta tarefa (dict com A_block, B, block_index)
2. send_json(tarefa)
3. response = recv_json()
4. Valida tipo de resposta
5. Lock → results[block_index] = C_block
6. Fecha conexão
```

**Tratamento de Erros**:
- Try/except captura falhas de rede
- Finally garante fechamento do socket

#### `main(num_clients)`
**Propósito**: Função principal do servidor

**Etapas**:
1. Gera matrizes A e B
2. Calcula baseline sequencial
3. Divide A em blocos
4. Cria socket servidor
5. Loop: aceita N clientes e cria threads
6. Aguarda todas threads (`join()`)
7. Reconstrói matriz C
8. Valida resultado

---

### `client/main.py`

#### `main(host, port, verbose)`
**Propósito**: Função principal do cliente

**Fluxo**:
```
1. Conecta ao servidor
2. Recebe tarefa (A_block, B, block_index)
3. Calcula C_block = A_block × B
4. Envia resultado
5. Fecha conexão
```

**Modo Verbose**:
- Imprime matrizes recebidas e calculadas
- Útil para debugging

---

## 🚀 Como Executar

### Passo 1: Iniciar o Servidor

```bash
cd /Users/marinavergara/Documents/www/faculdade/matmul-distribuida
python -m matmul.server.main --num-clients 3
```

**Saída esperada**:
```
[SERVIDOR] Iniciando servidor de multiplicação distribuída...
[SERVIDOR] Esperando 3 clientes em 127.0.0.1:5000
Número de linhas da matriz A: 9
Número de colunas da matriz A (e linhas de B): 6
Número de colunas da matriz B: 8
[SERVIDOR] Tempo total (sequencial): 0.0012 segundos
[SERVIDOR] A foi dividida em 3 blocos para 3 clientes.
[SERVIDOR] Aguardando conexões dos clientes...
```

### Passo 2: Iniciar Clientes (em terminais separados)

**Terminal 2**:
```bash
python -m matmul.client.main
```

**Terminal 3**:
```bash
python -m matmul.client.main
```

**Terminal 4**:
```bash
python -m matmul.client.main
```

### Passo 3: Observar Resultados

**No servidor**:
```
[SERVIDOR] Conexão aceita de ('127.0.0.1', 54321) para bloco 0
[SERVIDOR] Conexão aceita de ('127.0.0.1', 54322) para bloco 1
[SERVIDOR] Conexão aceita de ('127.0.0.1', 54323) para bloco 2
[SERVIDOR] Recebeu resultado do cliente ('127.0.0.1', 54321) (bloco 0)
[SERVIDOR] Recebeu resultado do cliente ('127.0.0.1', 54322) (bloco 1)
[SERVIDOR] Recebeu resultado do cliente ('127.0.0.1', 54323) (bloco 2)
[SERVIDOR] Tempo total (distribuído): 0.0089 segundos
[SERVIDOR] Os resultados distribuído e sequencial são iguais? True
```

---

## 🎯 Conceitos-Chave para Apresentação

### 1. Paralelismo vs Concorrência

**Concorrência** (no servidor):
- Múltiplas threads gerenciando clientes
- Compartilhamento de memória (results dict)
- Sincronização com locks

**Paralelismo** (entre clientes):
- Múltiplos processos executando simultaneamente
- Cada um processa bloco independente
- Sem compartilhamento de memória

### 2. Escalabilidade

**Horizontal**:
- Adicionar mais clientes → mais paralelismo
- Limitado por overhead de comunicação

**Vertical**:
- Matrizes maiores → melhor aproveitamento
- Overhead fixo diluído

### 3. Balanceamento de Carga

**Estratégia atual**: Divisão estática uniforme
- Cada cliente recebe ~(n/k) linhas
- Assume clientes homogêneos

**Melhorias possíveis**:
- Divisão dinâmica (work stealing)
- Considerar capacidade de cada cliente

### 4. Tolerância a Falhas

**Limitações atuais**:
- Se 1 cliente falhar, servidor fica bloqueado
- Sem retry ou timeout

**Melhorias possíveis**:
- Timeout nas conexões
- Redistribuir tarefas de clientes falhados

---

## 📈 Experimentos Sugeridos

### Experimento 1: Speedup vs Número de Clientes

```python
# Testar com 1, 2, 4, 8 clientes
# Matriz fixa: 1000×1000 × 1000×1000
# Medir: T_seq, T_dist(k), Speedup(k) = T_seq / T_dist(k)
```

### Experimento 2: Overhead de Comunicação

```python
# Medir tempo de:
# - Serialização JSON
# - Transmissão via socket
# - Deserialização
# Comparar com tempo de computação
```

### Experimento 3: Escalabilidade

```python
# Fixar num_clients = 4
# Variar tamanho: 100×100, 500×500, 1000×1000, 2000×2000
# Observar quando distribuído supera sequencial
```

---

## 🔍 Pontos Fortes do Projeto

1. ✅ **Arquitetura clara**: Separação cliente/servidor bem definida
2. ✅ **Protocolo robusto**: Framing evita bugs de parsing
3. ✅ **Validação**: Compara com resultado sequencial
4. ✅ **Medição**: Tempos de execução para análise
5. ✅ **Modularidade**: Funções reutilizáveis em `utils/`

## 🚧 Limitações e Melhorias Futuras

### Limitações

1. ❌ **Sem tolerância a falhas**: Cliente falhando trava servidor
2. ❌ **Divisão estática**: Não considera heterogeneidade
3. ❌ **Sem timeout**: Servidor pode esperar indefinidamente
4. ❌ **Serialização ineficiente**: JSON não é ideal para arrays numéricos

### Melhorias Propostas

1. **Usar NumPy**:
   ```python
   # Substituir listas por np.ndarray
   # Serializar com pickle ou msgpack
   # Multiplicação otimizada: np.dot()
   ```

2. **Timeout e Retry**:
   ```python
   sock.settimeout(30)  # 30 segundos
   # Redistribuir tarefa se timeout
   ```

3. **Divisão Dinâmica**:
   ```python
   # Servidor mantém fila de tarefas
   # Clientes pedem nova tarefa ao terminar
   ```

4. **Métricas Detalhadas**:
   ```python
   # Tempo de cada etapa
   # Throughput (elementos/segundo)
   # Eficiência (speedup/num_clients)
   ```

---

## 📚 Referências Teóricas

### Algoritmos de Multiplicação de Matrizes

1. **Clássico** (usado no projeto): O(n³)
2. **Strassen**: O(n^2.807)
3. **Coppersmith-Winograd**: O(n^2.376)

### Modelos de Programação Paralela

1. **SPMD** (Single Program, Multiple Data): Usado no projeto
2. **Master-Worker**: Arquitetura do projeto
3. **MapReduce**: Possível extensão

### Lei de Amdahl

```
Speedup_max = 1 / (s + (p / N))

s = fração sequencial (overhead)
p = fração paralelizável
N = número de processadores
```

**Aplicação ao projeto**:
- p ≈ 0.95 (cálculo da multiplicação)
- s ≈ 0.05 (comunicação, sincronização)
- Speedup_max(4 clientes) ≈ 3.48

---

## 🎤 Roteiro de Apresentação Sugerido

### 1. Introdução (2 min)
- Problema: Multiplicação de matrizes grandes
- Solução: Distribuir processamento

### 2. Arquitetura (3 min)
- Diagrama cliente-servidor
- Divisão em blocos
- Protocolo de comunicação

### 3. Conceitos de Paralelismo (3 min)
- Paralelismo de dados
- Threading vs Multiprocessing
- Sincronização com locks

### 4. Demonstração (5 min)
- Executar com 3 clientes
- Mostrar logs
- Comparar tempos

### 5. Análise de Desempenho (3 min)
- Gráfico speedup vs clientes
- Overhead de comunicação
- Lei de Amdahl

### 6. Conclusões (2 min)
- Ganhos obtidos
- Limitações
- Trabalhos futuros

---

## 💡 Perguntas Frequentes

**Q: Por que dividir por linhas e não por colunas?**
A: Linhas de A são independentes no cálculo. Dividir B seria mais complexo.

**Q: Por que usar JSON e não formato binário?**
A: Simplicidade e debugging. Para produção, usar pickle ou msgpack.

**Q: Funciona com clientes em máquinas diferentes?**
A: Sim! Basta mudar HOST para IP da máquina do servidor.

**Q: Quantos clientes é ideal?**
A: Depende do tamanho da matriz. Testar empiricamente.

**Q: Por que threading no servidor e não multiprocessing?**
A: Threads são suficientes pois servidor só faz I/O (não CPU-bound).

---

## 📝 Checklist para Apresentação

- [ ] Entender fluxo completo (inicialização → validação)
- [ ] Saber explicar cada função principal
- [ ] Preparar demonstração ao vivo
- [ ] Ter gráficos de desempenho (se possível)
- [ ] Conhecer limitações e melhorias
- [ ] Revisar conceitos: paralelismo, concorrência, locks
- [ ] Preparar respostas para perguntas frequentes

---

**Boa sorte na apresentação! 🚀**
