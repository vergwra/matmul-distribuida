"""
Script rápido para gerar gráficos com seus dados reais
Basta editar os dados abaixo e executar!
"""

from generate_graphs import PerformanceData, create_comparison_graphs, create_detailed_breakdown_chart


# ============================================================
# EDITE AQUI COM SEUS DADOS REAIS
# ============================================================

# Teste 1: Seu teste real (1000×1500×1000)
test1 = PerformanceData(1000, 2)
test1.t_sequential = 47.650216
test1.t_distributed = 32.499075
test1.overhead_split = 0.000051
test1.overhead_comm = 0.129624
test1.time_compute = 26.182824  # Média dos 2 clientes
test1.overhead_reconstruct = 0.000015

# Teste 2: Adicione mais testes aqui (exemplo com matriz menor)
test2 = PerformanceData(500, 2)
test2.t_sequential = 5.234567  # Substitua pelo valor real
test2.t_distributed = 3.456789  # Substitua pelo valor real
test2.overhead_split = 0.000045
test2.overhead_comm = 0.045678
test2.time_compute = 3.389012
test2.overhead_reconstruct = 0.000023

# Teste 3: Adicione mais testes aqui (exemplo com matriz maior)
test3 = PerformanceData(1500, 2)
test3.t_sequential = 120.456789  # Substitua pelo valor real
test3.t_distributed = 75.234567   # Substitua pelo valor real
test3.overhead_split = 0.000089
test3.overhead_comm = 0.234567
test3.time_compute = 74.876543
test3.overhead_reconstruct = 0.000034

# Lista de testes (comente os que não quiser incluir)
tests = [
    test1,
    test2,
    test3,
]

# ============================================================
# GERAÇÃO DOS GRÁFICOS
# ============================================================

if __name__ == "__main__":
    print("="*70)
    print("GERAÇÃO RÁPIDA DE GRÁFICOS")
    print("="*70)
    print()
    
    print("📊 Testes incluídos:")
    for i, test in enumerate(tests, 1):
        print(f"  {i}. Matriz {test.size}×{test.size} com {test.num_clients} clientes")
        print(f"     Speedup: {test.speedup:.2f}x | Eficiência: {test.efficiency:.1f}%")
    
    print("\n" + "="*70)
    print("Gerando gráficos...")
    print("="*70)
    
    # Gráficos comparativos
    print("\n📊 Criando gráficos comparativos...")
    create_comparison_graphs(tests, "performance_analysis.png")
    
    # Gráfico de pizza para cada teste
    for i, test in enumerate(tests, 1):
        print(f"\n🥧 Criando gráfico de decomposição (Teste {i})...")
        create_detailed_breakdown_chart(test, f"breakdown_test{i}.png")
    
    print("\n" + "="*70)
    print("✅ GRÁFICOS GERADOS COM SUCESSO!")
    print("="*70)
    print("\n📁 Arquivos criados:")
    print("  • performance_analysis.png - Comparação de todos os testes")
    for i in range(len(tests)):
        print(f"  • breakdown_test{i+1}.png - Decomposição do teste {i+1}")
    print()
    print("💡 Abra os arquivos PNG para visualizar os gráficos!")
    print()
