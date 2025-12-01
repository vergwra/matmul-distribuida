# 🚀 Multiplicação de Matrizes Distribuída

Sistema de multiplicação de matrizes distribuída usando sockets TCP e threading em Python.

## 📊 Documentação

- **`OVERVIEW_PROJETO.md`** - Arquitetura completa e fluxo do sistema
- **`METRICAS_DETALHADAS.md`** - Explicação das métricas de performance
- **`GUIA_RAPIDO.md`** - Roteiro para apresentação
- **`WORKFLOW_GRAFICOS.md`** - Como gerar gráficos com seus dados ⭐

## 🚀 Execução Rápida

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar servidor
```bash
python -m matmul.server.main --num-clients 2
# Digite: 1000, 1000, 1000
```

### 3. Iniciar clientes (em terminais separados)
```bash
python -m matmul.client.main
python -m matmul.client.main
```

## 📊 Gerar Gráficos

### Método Automático (Recomendado)

1. **Salvar dados do teste:**
```bash
python save_test_data.py
# Cole a saída completa do servidor
```

2. **Gerar gráficos:**
```bash
python generate_from_file.py
```

### Resultado
- `performance_analysis.png` - 6 gráficos comparativos
- `breakdown_testN.png` - Decomposição detalhada

## 🎯 Métricas Mostradas

- ⏱️ Tempo sequencial vs distribuído
- 🚀 Speedup (quantas vezes mais rápido)
- 📈 Eficiência do paralelismo
- 📊 Decomposição do overhead
- ⚡ Overhead comunicação + Computação paralela

## 📚 Estrutura

```
matmul-distribuida/
├── src/matmul/
│   ├── server/main.py          # Servidor coordenador
│   ├── client/main.py          # Cliente worker
│   └── utils/
│       ├── protocol.py         # Comunicação JSON/TCP
│       └── matrix_utils.py     # Operações com matrizes
├── save_test_data.py           # Salvar dados de teste
├── generate_from_file.py       # Gerar gráficos
└── test_results.json           # Dados salvos
```

## 🎓 Para Apresentação

1. Execute testes com diferentes tamanhos (500, 1000, 1500)
2. Salve cada teste com `save_test_data.py`
3. Gere gráficos com `generate_from_file.py`
4. Use os PNG nos slides

**Veja `GUIA_RAPIDO.md` para roteiro completo!**
