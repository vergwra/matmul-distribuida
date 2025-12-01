"""
Script para coletar dados de testes e gerar gráficos automaticamente
Permite entrada manual de dados ou importação de resultados
"""

from generate_graphs import PerformanceData, create_comparison_graphs, create_detailed_breakdown_chart


def input_test_data() -> PerformanceData:
    """
    Coleta dados de um teste via input do usuário
    """
    print("\n" + "="*60)
    print("ENTRADA DE DADOS DO TESTE")
    print("="*60)
    
    size = int(input("Tamanho da matriz (ex: 500 para 500×500): "))
    num_clients = int(input("Número de clientes: "))
    
    test = PerformanceData(size, num_clients)
    
    print("\n📊 Insira os tempos (em segundos):")
    test.t_sequential = float(input("  Tempo SEQUENCIAL: "))
    test.t_distributed = float(input("  Tempo DISTRIBUÍDO (total): "))
    
    print("\n🔧 Insira os componentes do overhead:")
    test.overhead_split = float(input("  Overhead de divisão: "))
    test.overhead_comm = float(input("  Overhead de comunicação: "))
    test.time_compute = float(input("  Computação paralela (média): "))
    test.overhead_reconstruct = float(input("  Overhead de reconstrução: "))
    
    print("\n✅ Dados coletados!")
    print(f"   Speedup: {test.speedup:.2f}x")
    print(f"   Eficiência: {test.efficiency:.1f}%")
    
    return test


def main():
    """
    Função principal - coleta dados e gera gráficos
    """
    print("="*70)
    print("COLETOR DE DADOS E GERADOR DE GRÁFICOS")
    print("="*70)
    print()
    print("Este script permite:")
    print("  1. Inserir dados manualmente de múltiplos testes")
    print("  2. Gerar gráficos comparativos automaticamente")
    print()
    
    tests = []
    
    while True:
        print("\n" + "="*70)
        choice = input("Deseja adicionar um teste? (s/n): ").lower()
        if choice != 's':
            break
        
        test = input_test_data()
        tests.append(test)
        
        print(f"\n📝 Total de testes coletados: {len(tests)}")
    
    if not tests:
        print("\n⚠️  Nenhum teste foi adicionado. Usando dados de exemplo...")
        
        # Dados de exemplo baseados no seu teste real
        test_real = PerformanceData(1000, 2)
        test_real.t_sequential = 47.650216
        test_real.t_distributed = 32.499075
        test_real.overhead_split = 0.000051
        test_real.overhead_comm = 0.129624
        test_real.time_compute = 26.182824
        test_real.overhead_reconstruct = 0.000015
        tests.append(test_real)
    
    print("\n" + "="*70)
    print("GERANDO GRÁFICOS...")
    print("="*70)
    
    # Gerar gráficos comparativos
    print("\n📊 Criando gráficos comparativos...")
    create_comparison_graphs(tests, "performance_analysis.png")
    
    # Gerar gráfico de pizza para o último teste
    if tests:
        print("\n🥧 Criando gráfico de decomposição detalhada...")
        create_detailed_breakdown_chart(tests[-1], "breakdown_chart.png")
    
    print("\n" + "="*70)
    print("✅ PROCESSO CONCLUÍDO!")
    print("="*70)
    print("\n📁 Arquivos gerados:")
    print("  • performance_analysis.png")
    print("  • breakdown_chart.png")
    print("\n💡 Use esses gráficos na sua apresentação!")
    print()


if __name__ == "__main__":
    main()
