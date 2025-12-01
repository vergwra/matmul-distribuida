"""
Gera gráficos a partir do arquivo test_results.json
"""

import json
from generate_graphs import PerformanceData, create_comparison_graphs, create_detailed_breakdown_chart


def main():
    print("="*70)
    print("GERAR GRÁFICOS A PARTIR DOS DADOS SALVOS")
    print("="*70)
    print()
    
    try:
        with open('test_results.json', 'r') as f:
            all_tests = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo test_results.json não encontrado!")
        print()
        print("Execute primeiro: python save_test_data.py")
        return
    
    if not all_tests:
        print("⚠️  Nenhum teste encontrado no arquivo.")
        return
    
    # Converter para objetos PerformanceData
    tests = []
    for data in all_tests:
        test = PerformanceData(data['size'], data['num_clients'])
        test.t_sequential = data['t_sequential']
        test.t_distributed = data['t_distributed']
        test.overhead_split = data['overhead_split']
        test.overhead_comm = data['overhead_comm']
        test.time_compute = data['time_compute']
        test.overhead_reconstruct = data['overhead_reconstruct']
        tests.append(test)
    
    print(f"📊 Testes encontrados: {len(tests)}")
    for i, test in enumerate(tests, 1):
        print(f"  {i}. Matriz {test.size}×{test.size} - Speedup: {test.speedup:.2f}x")
    
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
    print("  • performance_analysis.png")
    for i in range(len(tests)):
        print(f"  • breakdown_test{i+1}.png")
    print()


if __name__ == "__main__":
    main()
