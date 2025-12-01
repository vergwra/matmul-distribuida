# 📊 Guia de Geração de Gráficos

## 🎯 O que foi implementado

Criei **3 scripts** para gerar gráficos profissionais da análise de performance:

1. **`generate_graphs.py`**: Biblioteca base com funções de geração
2. **`quick_graph.py`**: Script rápido - edite os dados e execute! ⭐ **RECOMENDADO**
3. **`collect_and_graph.py`**: Script interativo para entrada manual

---

## 🚀 Uso Rápido (Recomendado)

### Passo 1: Instalar matplotlib

```bash
pip install matplotlib
# ou
pip install -r requirements.txt
```

### Passo 2: Editar dados no `quick_graph.py`

Abra o arquivo e edite com seus dados reais:

```python
# Teste 1: Seu teste real (1000×1500×1000)
test1 = PerformanceData(1000, 2)
test1.t_sequential = 47.650216        # ← Cole do servidor
test1.t_distributed = 32.499075       # ← Cole do servidor
test1.overhead_split = 0.000051       # ← Cole do servidor
test1.overhead_comm = 0.129624        # ← Cole do servidor
test1.time_compute = 26.182824        # ← Cole do servidor
test1.overhead_reconstruct = 0.000015 # ← Cole do servidor
```

### Passo 3: Executar

```bash
python quick_graph.py
```

### Resultado:

```
✅ GRÁFICOS GERADOS COM SUCESSO!
📁 Arquivos criados:
  • performance_analysis.png - Comparação de todos os testes
  • breakdown_test1.png - Decomposição do teste 1
  • breakdown_test2.png - Decomposição do teste 2
  • breakdown_test3.png - Decomposição do teste 3
```

---

## 📊 Gráficos Gerados

### 1. **performance_analysis.png** (6 gráficos em 1)

#### Gráfico 1: Comparação de Tempos (Barras)
- Compara tempo sequencial vs distribuído
- Mostra valores exatos em cada barra
- Vermelho = Sequencial, Azul = Distribuído

#### Gráfico 2: Speedup
- Mostra quantas vezes mais rápido
- Linha tracejada em 1.0x (break-even)
- Verde = Speedup > 1.0 (mais rápido)
- Vermelho = Speedup < 1.0 (mais lento)

#### Gráfico 3: Eficiência
- Percentual de aproveitamento do paralelismo
- Verde ≥ 70%, Amarelo 50-70%, Vermelho < 50%
- Linha tracejada em 100% (ideal)

#### Gráfico 4: Decomposição do Tempo Distribuído (Stacked Bar)
- Mostra cada componente empilhado:
  - Roxo = Overhead de divisão
  - Laranja = Overhead de comunicação
  - Verde = Computação paralela
  - Cinza = Overhead de reconstrução

#### Gráfico 5: Overhead vs Computação (Percentual)
- Mostra proporção de overhead vs computação
- Vermelho = Overhead total
- Verde = Computação paralela
- Valores em % dentro das barras

#### Gráfico 6: **Overhead Comunicação + Computação Paralela** ⭐
- **Exatamente o que você pediu!**
- Barras azuis = Soma de comunicação + computação
- Linha vermelha = Tempo sequencial (referência)
- Mostra valores exatos

---

### 2. **breakdown_testN.png** (2 gráficos de pizza)

#### Pizza 1: Decomposição Detalhada
- Mostra os 4 componentes com valores exatos
- Percentual de cada componente
- Destaque no overhead de comunicação

#### Pizza 2: Overhead vs Computação
- Simplificado: apenas 2 fatias
- Vermelho = Total de overhead
- Verde = Computação paralela
- Mostra claramente qual domina

---

## 🎨 Exemplo Visual

### Quando Overhead Domina (Matriz Pequena):

```
Overhead vs Computação (%)
┌─────────────────────────┐
│ ████████████ 84.2%      │ ← Overhead (Vermelho)
│ ███ 15.8%               │ ← Computação (Verde)
└─────────────────────────┘
Speedup: 0.07x ❌ (14x mais lento)
```

### Quando Paralelismo Compensa (Matriz Grande):

```
Overhead vs Computação (%)
┌─────────────────────────┐
│ ██ 11.4%                │ ← Overhead (Vermelho)
│ ████████████████ 88.6%  │ ← Computação (Verde)
└─────────────────────────┘
Speedup: 1.74x ✅ (quase 2x mais rápido)
```

---

## 📝 Como Coletar Dados do Servidor

Quando você executar o servidor, ele mostra:

```
======================================================================
ANÁLISE DE DESEMPENHO
======================================================================
⏱️  Tempo SEQUENCIAL:              47.650216 segundos    ← Cole aqui
⏱️  Tempo DISTRIBUÍDO (total):     32.499075 segundos    ← Cole aqui

📊 DECOMPOSIÇÃO DO TEMPO DISTRIBUÍDO:
   • Overhead de divisão:         0.000051 s (0.0%)      ← Cole aqui
   • Overhead de comunicação:     0.129624 s (0.4%)      ← Cole aqui
   • Computação paralela (média): 26.182824 s (80.6%)    ← Cole aqui
   • Overhead de reconstrução:    0.000015 s (0.0%)      ← Cole aqui
```

**Copie esses valores** e cole no `quick_graph.py`!

---

## 🔄 Workflow Completo

### 1. Execute múltiplos testes

```bash
# Teste 1: Matriz 500×500
python -m matmul.server.main --num-clients 2
# Digite: 500, 500, 500
# Copie os resultados

# Teste 2: Matriz 1000×1000
python -m matmul.server.main --num-clients 2
# Digite: 1000, 1000, 1000
# Copie os resultados

# Teste 3: Matriz 1500×1500
python -m matmul.server.main --num-clients 2
# Digite: 1500, 1500, 1500
# Copie os resultados
```

### 2. Cole os dados no `quick_graph.py`

```python
test1 = PerformanceData(500, 2)
test1.t_sequential = ...  # Cole do Teste 1
test1.t_distributed = ... # Cole do Teste 1
# etc...

test2 = PerformanceData(1000, 2)
test2.t_sequential = ...  # Cole do Teste 2
# etc...

test3 = PerformanceData(1500, 2)
test3.t_sequential = ...  # Cole do Teste 3
# etc...
```

### 3. Gere os gráficos

```bash
python quick_graph.py
```

### 4. Use na apresentação

- Abra os arquivos PNG gerados
- Insira nos slides
- Explique cada gráfico

---

## 💡 Dicas para Apresentação

### Gráfico de Comparação de Tempos:
> "Vejam que com matriz 1000×1000, o tempo distribuído (32s) é significativamente menor que o sequencial (47s)."

### Gráfico de Speedup:
> "Conseguimos um speedup de 1.47x, ou seja, o sistema distribuído é quase 1.5x mais rápido."

### Gráfico de Decomposição:
> "A computação paralela representa 80.6% do tempo, enquanto o overhead de comunicação é apenas 0.4%."

### Gráfico de Overhead + Computação:
> "A soma do overhead de comunicação (0.13s) com a computação paralela (26.18s) totaliza 26.31s, que é o núcleo do processamento distribuído."

---

## 🎯 Gráfico Especial: Overhead Comunicação + Computação

Este gráfico mostra **exatamente o que você pediu**:

```python
# No Gráfico 6 de performance_analysis.png
comm_plus_compute = overhead_comm + time_compute

Exemplo com seus dados:
0.129624s + 26.182824s = 26.312448s
```

**Interpretação**:
- Esta soma representa o "tempo útil" do sistema distribuído
- Exclui overheads negligíveis (divisão e reconstrução)
- Compara diretamente com tempo sequencial
- Mostra onde o tempo realmente é gasto

---

## 🔧 Personalização

### Mudar cores:

```python
# Em generate_graphs.py, linha ~40
colors = ['#e74c3c', '#3498db']  # Vermelho, Azul
# Substitua por suas cores preferidas
```

### Mudar tamanho:

```python
# Em generate_graphs.py, linha ~12
plt.rcParams['figure.figsize'] = (16, 12)  # Largura, Altura
```

### Adicionar mais testes:

```python
# Em quick_graph.py
test4 = PerformanceData(2000, 2)
test4.t_sequential = ...
# etc...

tests = [test1, test2, test3, test4]  # Adicione test4
```

---

## 📊 Exemplo Real com Seus Dados

Baseado no seu teste (1000×1500×1000):

```
Tempo Sequencial:              47.65s
Tempo Distribuído:             32.50s
Speedup:                       1.47x ✅
Eficiência:                    73.3%

Decomposição:
├─ Overhead divisão:           0.000051s (0.0%)
├─ Overhead comunicação:       0.129624s (0.4%)
├─ Computação paralela:        26.182824s (80.6%)
└─ Overhead reconstrução:      0.000015s (0.0%)

Overhead Comunicação + Computação: 26.31s
Ganho de tempo: 15.15s (economizou 31.8%)
```

---

## ✅ Checklist

- [ ] Instalar matplotlib (`pip install matplotlib`)
- [ ] Executar testes com diferentes tamanhos de matriz
- [ ] Copiar dados do servidor para `quick_graph.py`
- [ ] Executar `python quick_graph.py`
- [ ] Verificar arquivos PNG gerados
- [ ] Inserir gráficos nos slides
- [ ] Preparar explicação de cada gráfico

---

## 🆘 Troubleshooting

### Erro: "No module named 'matplotlib'"
```bash
pip install matplotlib
```

### Erro: "No module named 'generate_graphs'"
```bash
# Certifique-se de estar no diretório correto
cd /Users/marinavergara/Documents/www/faculdade/matmul-distribuida
python quick_graph.py
```

### Gráficos não aparecem
```python
# Em generate_graphs.py, comente a linha:
# plt.show()  # ← Comente se não quiser janela interativa
```

### Quero apenas salvar, sem mostrar
```python
# Em generate_graphs.py, após plt.savefig():
# plt.show()  # ← Comente esta linha
```

---

## 🎓 Conceitos Demonstrados nos Gráficos

1. **Lei de Amdahl**: Speedup limitado pelo overhead
2. **Escalabilidade**: Como desempenho varia com tamanho
3. **Trade-off**: Overhead vs ganho de paralelismo
4. **Eficiência**: Aproveitamento dos recursos paralelos
5. **Decomposição**: Onde o tempo é realmente gasto

---

**Boa apresentação com os gráficos! 📊🚀**
