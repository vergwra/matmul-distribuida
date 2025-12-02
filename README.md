# Multiplicação de Matrizes Distribuída

Este projeto implementa um sistema de multiplicação de matrizes distribuída utilizando Sockets TCP em Python. O sistema é composto por um **Servidor** (Coordenador) e múltiplos **Clientes** (Trabalhadores).

## 📋 Pré-requisitos

- Python 3.8 ou superior instalado.
- Biblioteca `numpy` (opcional, usada apenas para geração de matrizes no utils, mas o código principal usa listas puras para fins didáticos. Se der erro de import, instale).

### Configuração do Ambiente Virtual (Recomendado)

É uma boa prática usar um ambiente virtual para isolar as dependências.

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Instalação das dependências

Com o ambiente virtual ativado, instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🚀 Como Rodar

> [!IMPORTANT]
> **Todos os comandos abaixo devem ser executados de dentro da pasta `src`**.
> Isso é necessário para que o Python encontre o pacote `matmul` corretamente.

O projeto deve ser executado a partir da pasta `src` para que as importações funcionem corretamente.

### Passo 1: Iniciar o Servidor

O servidor agora aguarda a conexão de todos os clientes e depois entra em um **Modo Interativo**.

**No Windows (Command Prompt ou PowerShell):**
```powershell
cd src
python -m matmul.server.main --num-clients 2
```

**No macOS / Linux:**
```bash
cd src
python3 -m matmul.server.main --num-clients 2
```

> **Nota:** O servidor ficará esperando até que o número exato de clientes (definido em `--num-clients`) se conecte.

### Passo 2: Iniciar os Clientes

Abra **novos terminais** (um para cada cliente) e execute o comando abaixo. Os clientes agora ficam rodando em loop, esperando tarefas.

**No Windows:**
```powershell
cd src
python -m matmul.client.main
```

**No macOS / Linux:**
```bash
cd src
python3 -m matmul.client.main
```

### Passo 3: Executar Multiplicações (Menu)

Após todos os clientes conectarem, o terminal do **Servidor** mostrará um menu:

```text
------------------------------
 MENU PRINCIPAL
------------------------------
1. Nova Multiplicação
2. Sair
Escolha uma opção:
```

1.  Digite `1` e pressione Enter.
2.  Informe as dimensões das matrizes quando solicitado.
3.  O servidor distribuirá o trabalho para os clientes já conectados.
4.  Ao final, você verá os resultados e o menu aparecerá novamente.
5.  Você pode rodar quantos testes quiser sem precisar reiniciar os clientes!

---

## 🧪 Como Testar (Cenários)

Para reproduzir os testes do relatório, siga os passos abaixo.

### Cenário 1: Teste Pequeno (Funcionalidade)
1.  Inicie o servidor esperando **2 clientes**:
    `python3 -m matmul.server.main --num-clients 2`
2.  Quando pedir o tamanho, digite:
    -   Linhas A: `100`
    -   Colunas A: `100`
    -   Colunas B: `100`
3.  Abra 2 terminais e inicie 2 clientes.
4.  Observe o tempo total e verifique se o resultado bate com o sequencial.

### Cenário 2: Teste Médio
1.  Inicie o servidor esperando **3 clientes**:
    `python3 -m matmul.server.main --num-clients 3`
2.  Tamanhos: `500` x `500` x `500`.
3.  Abra 3 terminais e inicie 3 clientes.

### Cenário 3: Stress Test (Matrizes Grandes)
1.  Inicie o servidor esperando **4 clientes** (ou mais, se tiver máquinas/núcleos disponíveis):
    `python3 -m matmul.server.main --num-clients 4`
2.  Tamanhos: `1000` x `1000` x `1000` (ou maior).
3.  Abra 4 terminais e inicie 4 clientes.
4.  **Atenção:** O cálculo sequencial pode demorar bastante aqui. O distribuído deve mostrar vantagem se o overhead de rede não for gargalo.

---

## 🛠️ Solução de Problemas

**Erro: `ModuleNotFoundError: No module named 'matmul'`**
- Certifique-se de que você está executando o comando de dentro da pasta `src`.
- Use `python -m matmul.server.main` em vez de `python matmul/server/main.py`.

**Erro: `ConnectionRefusedError` no cliente**
- O servidor não está rodando ou já encerrou. Inicie o servidor primeiro.

**O programa trava**
- Verifique se você iniciou o número exato de clientes que configurou no `--num-clients`. O servidor espera todos conectarem antes de iniciar.
