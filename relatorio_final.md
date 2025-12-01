# AV3 Computação Paralela e Concorrente

## Sumário
1. [Introdução](#1-introdução)
2. [Conceitos Fundamentais](#2-conceitos-fundamentais)
    - [2.1 Concorrência](#21-concorrência)
    - [2.2 Paralelismo](#22-paralelismo)
    - [2.3 Diferença entre Concorrência e Paralelismo](#23-diferença-entre-concorrência-e-paralelismo)
3. [Computação Distribuída](#3-computação-distribuída)
4. [Metodologia de Foster](#4-metodologia-de-foster)
    - [4.1 Particionamento](#41-particionamento)
    - [4.2 Comunicação](#42-comunicação)
    - [4.3 Aglomeração](#43-aglomeração)
    - [4.4 Mapeamento](#44-mapeamento)
5. [Multiplicação de Matrizes](#5-multiplicação-de-matrizes)
6. [Relacionando a teoria com o projeto prático](#6-relacionando-a-teoria-com-o-projeto-prático)
7. [Resultados e Testes](#7-resultados-e-testes)
8. [Conclusão](#8-conclusão)

## 1. Introdução
A computação paralela e distribuída se tornou fundamental para resolver problemas que exigem alta capacidade de processamento. Um exemplo prático e cotidiano é uma busca no Google Imagens.

**Cenário Prático: A Busca por "Leão Amarelo"**
Quando um usuário pesquisa por "leão amarelo", o motor de busca não compara palavras-chave apenas. O sistema utiliza **bancos de dados vetoriais**:
1.  As imagens são convertidas em vetores numéricos (embeddings).
2.  O texto da busca ("leão amarelo") também é vetorizado.
3.  Para encontrar a melhor correspondência, o sistema realiza cálculos de similaridade (como similaridade de cosseno), que fundamentalmente envolvem **multiplicação de matrizes** gigantescas entre o vetor de busca e a matriz de todas as imagens indexadas.

Como o Google possui bilhões de imagens, essa operação de matriz cresce exponencialmente. Se a complexidade é $O(n^3)$ (ou quadrática dependendo da implementação de busca), um único computador levaria horas ou dias para responder. No entanto, o Google responde em milissegundos.
**Como isso é possível?** A resposta reside na **Computação Distribuída**. O trabalho é dividido entre milhares de máquinas que processam pedaços da matriz simultaneamente.

Este trabalho explora exatamente essa mecânica, abordando:
- conceitos fundamentais de concorrência e paralelismo,
- a metodologia de Foster para projetar soluções paralelas,
- princípios de computação distribuída,
- e a aplicação desses conceitos na multiplicação distribuída de matrizes, simulando em menor escala o que grandes motores de busca fazem.

## 2. Conceitos Fundamentais

### 2.1 Concorrência
Concorrência é a capacidade de avançar múltiplas tarefas ao mesmo tempo, independentemente de serem executadas simultaneamente no hardware. No nível de software, isso pode acontecer com threads, processos ou tarefas cooperativas.

Um sistema concorrente não garante execução ao mesmo tempo, apenas garante que várias tarefas progridem de forma intercalada.

**Aplicação no Código:**
O servidor utiliza a biblioteca `threading` para lidar com múltiplos clientes de forma concorrente. O trecho abaixo mostra como o servidor aceita conexões em um loop e, para cada novo cliente, dispara uma thread dedicada (`handle_client`). Isso permite que o servidor continue aceitando novos clientes ou processando outras tarefas enquanto aguarda a comunicação com os clientes já conectados. O uso de `daemon=True` indica que essas threads serão encerradas automaticamente se o programa principal terminar.

**Arquivo:** `src/matmul/server/main.py`
**Linhas:** 139-152
```python
        # 4- aceita conexões e dispara threads
        for block_index in range(num_clients):
            conn, addr = server_sock.accept()
            print(f"[SERVIDOR] Conexão aceita de {addr} para bloco {block_index}")

            A_block = blocks[block_index]

            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, block_index, A_block, B, results, lock, metrics),
                daemon=True,
            )
            t.start()
            threads.append(t)
```

### 2.2 Paralelismo
Paralelismo existe quando duas ou mais tarefas executam realmente ao mesmo tempo, em hardware físico distinto (múltiplos núcleos de CPU, múltiplos computadores, GPUs). É um subconjunto da concorrência.

**Aplicação no Código:**
O paralelismo real acontece porque temos múltiplos processos `client` rodando (potencialmente em máquinas diferentes). Cada cliente executa a função `multiply` de forma independente. O código abaixo mostra o momento exato em que o cliente recebe os dados e inicia o cálculo intensivo. Enquanto este cliente está na linha `multiply(A_block, B)`, outros clientes estão executando a mesma linha simultaneamente em seus próprios processos.

**Arquivo:** `src/matmul/client/main.py`
**Linhas:** 33-46
```python
        print(f"[CLIENTE] Tarefa recebida. Bloco de índice {block_index}.")

        if verbose:
            print_matrix(A_block, f"A_block (bloco {block_index}) recebido")
            print_matrix(B, "Matriz B recebida")

        # 3- calcula o bloco de C
        print(f"[CLIENTE] Iniciando computação do bloco {block_index}...")
        start_compute = time.perf_counter()
        C_block: Matrix = multiply(A_block, B)
        end_compute = time.perf_counter()
        compute_time = end_compute - start_compute
        
        print(f"[CLIENTE] Tempo de computação (bloco {block_index}): {compute_time:.6f} segundos")
```

### 2.3 Diferença entre Concorrência e Paralelismo
| Concorrência | Paralelismo |
| :--- | :--- |
| Múltiplas tarefas progridem | Múltiplas tarefas executam ao mesmo tempo |
| Pode ocorrer com 1 núcleo | Requer 2+ núcleos ou máquinas |
| Mais sobre estruturação | Mais sobre velocidade |
| É sobre “lidar com várias coisas” | É sobre “fazer várias coisas simultaneamente” |

Nosso projeto tem ambos:
- **Concorrência:** servidor usa threads para gerenciar I/O dos clientes.
  * *Analogia Google:* O servidor web do Google aceitando milhares de requisições de busca ("leão", "pizza", "carro") ao mesmo tempo.
- **Paralelismo:** clientes executam cálculos matemáticos ao mesmo tempo em processos distintos.
  * *Analogia Google:* Para uma única busca ("leão"), milhares de processadores calculam a similaridade em diferentes pedaços do banco de dados simultaneamente para devolver o resultado rápido.

## 3. Computação Distribuída
Computação distribuída é quando um sistema é composto por múltiplos computadores independentes, conectados por rede, que cooperam entre si para resolver um problema.

Voltando ao exemplo da busca: **Como o Google responde tão rápido?**
Ele não usa um "supercomputador" único. Ele usa **computação distribuída**. O índice de imagens é particionado (sharded) entre várias máquinas. Quando você busca "leão amarelo":
1.  Um nó coordenador recebe o pedido.
2.  Ele distribui a tarefa para centenas de nós trabalhadores.
3.  Cada nó calcula a multiplicação de matrizes no seu pequeno pedaço de dados.
4.  O coordenador agrega os resultados e devolve as melhores imagens.

Se não fosse distribuído, o tempo de resposta seria inviável devido ao crescimento cúbico do custo computacional.

Elementos importantes:
- Nós (processadores independentes)
- Comunicação por rede (TCP, HTTP, RPC...)
- Sincronização e troca de mensagens
- Distribuição do trabalho

**Aplicação no Código (Servidor):**
O servidor atua como o nó coordenador. Ele cria um socket TCP (`SOCK_STREAM`), faz o `bind` em um endereço IP e porta, e fica ouvindo (`listen`) por conexões. Isso estabelece a infraestrutura de rede necessária para a distribuição.

**Arquivo:** `src/matmul/server/main.py`
**Linhas:** 129-133
```python
    # 3- cria socket servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(num_clients)

        threads: List[threading.Thread] = []
```

**Aplicação no Código (Cliente):**
O cliente é um nó trabalhador. Ele não compartilha memória com o servidor; toda a interação é via rede. Ele se conecta ativamente ao servidor usando o IP e Porta fornecidos.

**Arquivo:** `src/matmul/client/main.py`
**Linhas:** 14-19
```python
def main(host: str, port: int, verbose: bool) -> None:
    print(f"[CLIENTE] Iniciando cliente. Conectando a {host}:{port}...")

    # 1- abre o socket e conecta no servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print("[CLIENTE] Conectado ao servidor. Aguardando tarefa...")
```

## 4. Metodologia de Foster
A metodologia de Foster (2000) fornece um guia para transformar um problema sequencial em um paralelo através de quatro etapas.

### 4.1 Particionamento
Primeira etapa: dividir o problema em tarefas independentes. No nosso projeto, dividimos a matriz A por linhas (Data Parallelism).

**Aplicação no Código:**
A função `split_matrix_by_rows` implementa essa lógica. Ela calcula o tamanho do bloco (`block_size`) dividindo o total de linhas pelo número de partes. O tratamento do `remainder` (resto da divisão) é crucial para garantir que todas as linhas sejam processadas, distribuindo as linhas "sobra" entre os primeiros blocos. Isso garante balanceamento de carga.

**Arquivo:** `src/matmul/utils/matrix_utils.py`
**Linhas:** 53-66
```python
    rows = len(A)
    block_size = rows // num_parts
    remainder = rows % num_parts

    blocks = []
    start = 0

    for i in range(num_parts):
        # Distribui o resto entre os primeiros blocos para balancear
        extra = 1 if i < remainder else 0
        end = start + block_size + extra
        blocks.append(A[start:end])
        start = end

    return blocks
```

### 4.2 Comunicação
Etapa de definir como os processadores trocam informações. No nosso projeto, o servidor envia o bloco de A e a matriz B, e o cliente devolve o bloco calculado de C. A comunicação é feita via Sockets TCP com payloads em JSON.

**Aplicação no Código:**
Para garantir a integridade das mensagens em TCP (que é um stream de bytes), implementamos um protocolo simples: enviamos primeiro 4 bytes contendo o tamanho da mensagem (usando `struct.pack("!I", ...)` para garantir big-endian), seguido pelo payload JSON. Isso permite que o receptor saiba exatamente quantos bytes ler.

**Arquivo:** `src/matmul/utils/protocol.py`
**Linhas:** 6-12 (Envio) e 33-44 (Recebimento)
```python
def send_json(sock: socket.socket, data: Dict[str, Any]) -> None:
    """
    Envia um dicionário Python como JSON pelo socket, com cabeçalho de tamanho.
    """
    raw = json.dumps(data).encode("utf-8")
    size = struct.pack("!I", len(raw))  # 4 bytes, network order (big-endian)
    sock.sendall(size + raw)

# ... (omitted recv_exactly)

def recv_json(sock: socket.socket) -> Dict[str, Any]:
    """
    Recebe um JSON com cabeçalho de tamanho e devolve como dicionário.
    """
    # Primeiro lê 4 bytes com o tamanho
    size_bytes = recv_exactly(sock, 4)
    size = struct.unpack("!I", size_bytes)[0]

    # Agora lê exatamente 'size' bytes de payload
    raw = recv_exactly(sock, size)
    data = json.loads(raw.decode("utf-8"))
    return data
```

### 4.3 Aglomeração
Agrupa tarefas pequenas em tarefas maiores para reduzir overhead. No nosso projeto, cada cliente recebe um **bloco de linhas** inteiro, e não linha por linha individualmente. Isso reduz drasticamente o overhead da rede.

**Aplicação no Código:**
Em vez de criar uma tarefa para cada linha da matriz (o que seria o particionamento mais fino possível), nós aglomeramos essas linhas em `num_clients` blocos. A variável `blocks` contém sub-matrizes completas. Se não fizéssemos isso, o tempo gasto enviando pacotes de rede superaria o tempo de cálculo.

**Arquivo:** `src/matmul/server/main.py`
**Linhas:** 112-116
```python
    # 2- divide A em blocos de linhas, um para cada cliente
    t_split_start = time.perf_counter()
    blocks = split_matrix_by_rows(A, num_clients)
    t_split_end = time.perf_counter()
    print(f"[SERVIDOR] A foi dividida em {len(blocks)} blocos para {num_clients} clientes.")
```

### 4.4 Mapeamento
Distribui as tarefas entre os processadores reais. No nosso projeto, cada bloco criado na etapa de aglomeração é mapeado diretamente para um cliente que se conecta.

**Aplicação no Código:**
O mapeamento é estático e direto: o primeiro cliente a conectar recebe o `block_index=0`, o segundo recebe `block_index=1`, e assim por diante. A variável `A_block` é extraída da lista `blocks` usando esse índice e passada para a thread que gerencia aquele cliente específico.

**Arquivo:** `src/matmul/server/main.py`
**Linhas:** 140-148
```python
        # 4- aceita conexões e dispara threads
        for block_index in range(num_clients):
            conn, addr = server_sock.accept()
            print(f"[SERVIDOR] Conexão aceita de {addr} para bloco {block_index}")

            # Mapeamento: Bloco i -> Cliente i
            A_block = blocks[block_index]

            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, block_index, A_block, B, results, lock, metrics),
                daemon=True,
            )
```

## 5. Multiplicação de Matrizes
A operação central é a multiplicação de matrizes: `C[i][j] = Σ (A[i][k] * B[k][j])`.

**Aplicação no Código:**
Aqui vemos a implementação do algoritmo cúbico O(n³). Três loops aninhados percorrem as linhas de A (`i`), as colunas de B (`j`) e o índice comum (`k`) para realizar o produto escalar. Esta é a parte "computacionalmente intensiva" que justifica a paralelização.

**Arquivo:** `src/matmul/utils/matrix_utils.py`
**Linhas:** 31-39
```python
    # Multiplicação clássica
    for i in range(n):
        for j in range(p):
            soma = 0
            # Produto escalar da linha i de A pela coluna j de B
            for k in range(m):
                soma += A[i][k] * B[k][j]
            C[i][j] = soma

    return C
```

## 6. Relacionando a teoria com o projeto prático

| Conceito | Aplicação no seu projeto |
| :--- | :--- |
| **Concorrência** | Threads do servidor lidando com vários clientes simultaneamente (`server/main.py`). |
| **Paralelismo** | Clientes executando `multiply()` em processos distintos (`client/main.py`). |
| **Comunicação** | Envio de matrizes por sockets TCP (`utils/protocol.py`). |
| **Foster – Partitioning** | `split_matrix_by_rows` dividindo A em fatias. |
| **Foster – Communication** | Troca de mensagens JSON (`type: task` / `type: result`). |
| **Foster – Agglomeration** | Envio de blocos contendo múltiplas linhas de uma vez. |
| **Foster – Mapping** | Atribuição de `block_index` para cada conexão aceita. |
| **Computação distribuída** | Separação física entre lógica de coordenação (Server) e cálculo (Client). |

## 7. Resultados e Testes

Para validar a solução e demonstrar o ganho de desempenho (ou o overhead em casos menores), foram realizados testes com diferentes tamanhos de matrizes e quantidades de clientes.

### Cenário de Teste 1: Matrizes Pequenas
**Configuração:**
- Matriz A: `[INSERIR TAMANHO, ex: 100x100]`
- Matriz B: `[INSERIR TAMANHO, ex: 100x100]`
- Número de Clientes: `[INSERIR QTD]`

**Resultado (Print do Servidor):**
```text
[COLE AQUI O OUTPUT DO TERMINAL DO SERVIDOR MOSTRANDO O TEMPO E O SPEEDUP]
```

---

### Cenário de Teste 2: Matrizes Médias
**Configuração:**
- Matriz A: `[INSERIR TAMANHO, ex: 500x500]`
- Matriz B: `[INSERIR TAMANHO, ex: 500x500]`
- Número de Clientes: `[INSERIR QTD]`

**Resultado (Print do Servidor):**
```text
[COLE AQUI O OUTPUT DO TERMINAL DO SERVIDOR MOSTRANDO O TEMPO E O SPEEDUP]
```

---

### Cenário de Teste 3: Matrizes Grandes (Stress Test)
**Configuração:**
- Matriz A: `[INSERIR TAMANHO, ex: 1000x1000]`
- Matriz B: `[INSERIR TAMANHO, ex: 1000x1000]`
- Número de Clientes: `[INSERIR QTD]`

**Resultado (Print do Servidor):**
```text
[COLE AQUI O OUTPUT DO TERMINAL DO SERVIDOR MOSTRANDO O TEMPO E O SPEEDUP]
```

## 8. Conclusão
A multiplicação distribuída de matrizes demonstra claramente como dividir um problema em partes independentes, distribuir o trabalho entre várias máquinas e coordenar a comunicação. A metodologia de Foster se encaixa perfeitamente na solução, oferecendo uma visão estruturada das decisões de projeto. O trabalho evidencia tanto os aspectos teóricos quanto práticos da computação paralela e distribuída.
