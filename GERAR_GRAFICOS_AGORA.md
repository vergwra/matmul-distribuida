# 🚀 GERAR GRÁFICOS AGORA - 3 Passos Simples

## ⚡ Passo 1: Instalar matplotlib

```bash
pip install matplotlib
```

## ⚡ Passo 2: Executar o script

```bash
cd /Users/marinavergara/Documents/www/faculdade/matmul-distribuida
python quick_graph.py
```

## ⚡ Passo 3: Abrir os gráficos

Os arquivos PNG estarão no mesmo diretório:
- `performance_analysis.png` - 6 gráficos comparativos
- `breakdown_test1.png` - Pizza do teste 1
- `breakdown_test2.png` - Pizza do teste 2
- `breakdown_test3.png` - Pizza do teste 3

---

## 📊 O que você vai ver:

### performance_analysis.png contém:

1. **Comparação de Tempos**: Barras mostrando sequencial vs distribuído
2. **Speedup**: Quantas vezes mais rápido (1.47x no seu caso)
3. **Eficiência**: Percentual de aproveitamento (73.3%)
4. **Decomposição**: Overhead vs Computação (empilhado)
5. **Percentuais**: Overhead (0.4%) vs Computação (99.6%)
6. **Comunicação + Computação**: Soma que você pediu! (26.31s vs 47.65s)

### breakdown_testN.png contém:

1. **Pizza Detalhada**: 4 fatias (divisão, comunicação, computação, reconstrução)
2. **Pizza Simplificada**: 2 fatias (overhead total vs computação)

---

## 🎯 Já tem seus dados reais incluídos!

O script já está configurado com:
- **Teste 1**: Matriz 1000×1000 (seus dados reais)
- **Teste 2**: Matriz 500×500 (exemplo)
- **Teste 3**: Matriz 1500×1500 (exemplo)

**Para usar APENAS seus dados reais**, edite `quick_graph.py`:

```python
# Comente os testes de exemplo:
tests = [
    test1,  # Seus dados reais - MANTER
    # test2,  # Exemplo - COMENTAR
    # test3,  # Exemplo - COMENTAR
]
```

---

## 🔄 Para adicionar mais testes seus:

1. Execute o servidor com outro tamanho de matriz
2. Copie os valores da saída
3. Adicione no `quick_graph.py`:

```python
test_novo = PerformanceData(TAMANHO, 2)
test_novo.t_sequential = ...      # Cole aqui
test_novo.t_distributed = ...     # Cole aqui
test_novo.overhead_split = ...    # Cole aqui
test_novo.overhead_comm = ...     # Cole aqui
test_novo.time_compute = ...      # Cole aqui
test_novo.overhead_reconstruct = ... # Cole aqui

tests = [test1, test_novo]  # Adicione na lista
```

4. Execute novamente: `python quick_graph.py`

---

## ✅ Pronto!

Seus gráficos profissionais estão prontos para a apresentação! 🎓📊

**Dica**: Abra os PNG e insira diretamente nos slides do PowerPoint/Google Slides.
