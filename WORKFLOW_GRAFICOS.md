# 🔄 Workflow: Testes → Gráficos Automáticos

## ⚠️ IMPORTANTE

Os gráficos do `quick_graph.py` usam **dados de exemplo**!

Para usar **seus dados reais**, siga este workflow:

---

## 📋 Método 1: Salvar e Gerar (RECOMENDADO)

### Passo 1: Execute um teste

```bash
# Terminal 1 - Servidor
python -m matmul.server.main --num-clients 2
# Digite: 1000, 1000, 1000

# Terminal 2 - Cliente 1
python -m matmul.client.main

# Terminal 3 - Cliente 2
python -m matmul.client.main
```

### Passo 2: Copie TODA a saída do servidor

Exemplo do que copiar:

```
[SERVIDOR] Iniciando servidor de multiplicação distribuída...
[SERVIDOR] Esperando 2 clientes em 127.0.0.1:5000
Número de linhas da matriz A: 1000
Número de colunas da matriz A (e linhas de B): 1000
Número de colunas da matriz B: 1000
[SERVIDOR] Tempo total (sequencial): 47.6502 segundos

... (toda a saída) ...

======================================================================
ANÁLISE DE DESEMPENHO
======================================================================
⏱️  Tempo SEQUENCIAL:              47.650216 segundos
⏱️  Tempo DISTRIBUÍDO (total):     32.499075 segundos

📊 DECOMPOSIÇÃO DO TEMPO DISTRIBUÍDO:
   • Overhead de divisão:         0.000051 s (0.0%)
   • Overhead de comunicação:     0.129624 s (0.4%)
   • Computação paralela (média): 26.182824 s (80.6%)
   • Overhead de reconstrução:    0.000015 s (0.0%)
   • Total de overhead:           0.129690 s (0.4%)

🚀 MÉTRICAS DE PARALELISMO:
   • Speedup:                     1.47x
   • Eficiência:                  73.3%
   • Ganho de tempo:              15.151141 s
   ✅ Distribuído é 1.47x MAIS RÁPIDO!
======================================================================

[SERVIDOR] Validando resultado distribuído...
[SERVIDOR] Os resultados distribuído e sequencial são iguais? True
```

### Passo 3: Salvar os dados

```bash
python save_test_data.py
```

Cole a saída copiada e pressione ENTER duas vezes.

**Resultado**:
```
✅ Dados salvos com sucesso!
   Matriz: 1000×1000
   Speedup: 1.47x
📝 Total de testes salvos: 1
📁 Arquivo: test_results.json
```

### Passo 4: Repetir para outros tamanhos

Execute mais testes (500×500, 1500×1500, etc.) e salve cada um:

```bash
# Teste 2
python -m matmul.server.main --num-clients 2  # Digite: 500, 500, 500
# ... execute clientes ...
# Copie saída
python save_test_data.py  # Cole e salve

# Teste 3
python -m matmul.server.main --num-clients 2  # Digite: 1500, 1500, 1500
# ... execute clientes ...
# Copie saída
python save_test_data.py  # Cole e salve
```

### Passo 5: Gerar gráficos

```bash
python generate_from_file.py
```

**Resultado**:
```
✅ GRÁFICOS GERADOS COM SUCESSO!
📁 Arquivos criados:
  • performance_analysis.png
  • breakdown_test1.png
  • breakdown_test2.png
  • breakdown_test3.png
```

---

## 📋 Método 2: Editar Manualmente

Se preferir, edite diretamente o `quick_graph.py`:

```python
# Abra quick_graph.py e substitua:

# Teste 1: SEU TESTE REAL
test1 = PerformanceData(1000, 2)
test1.t_sequential = 47.650216      # ← Cole do servidor
test1.t_distributed = 32.499075     # ← Cole do servidor
test1.overhead_split = 0.000051     # ← Cole do servidor
test1.overhead_comm = 0.129624      # ← Cole do servidor
test1.time_compute = 26.182824      # ← Cole do servidor
test1.overhead_reconstruct = 0.000015  # ← Cole do servidor
```

Depois execute:
```bash
python quick_graph.py
```

---

## 📊 Estrutura do test_results.json

```json
[
  {
    "size": 1000,
    "num_clients": 2,
    "t_sequential": 47.650216,
    "t_distributed": 32.499075,
    "overhead_split": 0.000051,
    "overhead_comm": 0.129624,
    "time_compute": 26.182824,
    "overhead_reconstruct": 0.000015
  },
  {
    "size": 500,
    "num_clients": 2,
    "t_sequential": 5.234567,
    "t_distributed": 3.456789,
    ...
  }
]
```

---

## 🎯 Comparação dos Métodos

| Método | Vantagem | Desvantagem |
|--------|----------|-------------|
| **Salvar e Gerar** | Automático, não precisa editar código | Precisa copiar/colar |
| **Editar Manual** | Controle total | Precisa editar arquivo Python |
| **quick_graph.py** | Rápido para testar | Usa dados de exemplo |

---

## 💡 Dicas

### Para adicionar mais testes depois:

```bash
# Execute novo teste
python -m matmul.server.main --num-clients 2

# Salve os dados
python save_test_data.py  # Adiciona ao arquivo existente

# Regere os gráficos
python generate_from_file.py
```

### Para limpar e começar de novo:

```bash
rm test_results.json
# Agora salve novos testes
```

### Para ver os dados salvos:

```bash
cat test_results.json
# ou
python -m json.tool test_results.json
```

---

## 🔍 Exemplo Completo

```bash
# 1. Execute teste 1 (1000×1000)
python -m matmul.server.main --num-clients 2
# ... execute clientes ...
# Copie TODA a saída

# 2. Salve
python save_test_data.py
# Cole e pressione ENTER duas vezes

# 3. Execute teste 2 (500×500)
python -m matmul.server.main --num-clients 2
# ... execute clientes ...
# Copie TODA a saída

# 4. Salve
python save_test_data.py
# Cole e pressione ENTER duas vezes

# 5. Gere gráficos
python generate_from_file.py

# 6. Abra os arquivos PNG gerados
open performance_analysis.png
open breakdown_test1.png
open breakdown_test2.png
```

---

## ✅ Checklist

- [ ] Executar testes com diferentes tamanhos
- [ ] Copiar saída completa de cada teste
- [ ] Salvar cada teste com `save_test_data.py`
- [ ] Gerar gráficos com `generate_from_file.py`
- [ ] Verificar arquivos PNG criados
- [ ] Usar nos slides da apresentação

---

**Agora sim, os gráficos usarão seus dados reais! 📊✅**
