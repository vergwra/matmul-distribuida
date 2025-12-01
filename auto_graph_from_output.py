"""
Script para extrair dados da saída do servidor e gerar gráficos automaticamente
Cole a saída completa do servidor quando solicitado
"""

import re
from generate_graphs import PerformanceData, create_comparison_graphs, create_detailed_breakdown_chart


def parse_server_output(output: str) -> PerformanceData:
    """
    Extrai dados da saída do servidor
    """
    # Extrair dimensões da matriz
    size_match = re.search(r'Número de linhas da matriz A: (\d+)', output)
    if not size_match:
        raise ValueError("Não foi possível encontrar o tamanho da matriz")
    
    size = int(size_match.group(1))
    
    # Extrair número de clientes
    clients_match = re.search(r'Esperando (\d+) clientes', output)
    num_clients = int(clients_match.group(1)) if clients_match else 2
    
    test = PerformanceData(size, num_clients)
    
    # Extrair tempo sequencial
    seq_match = re.search(r'Tempo SEQUENCIAL:\s+([\d.]+) segundos', output)
    if seq_match:
        test.t_sequential = float(seq_match.group(1))
    
    # Extrair tempo distribuído
    dist_match = re.search(r'Tempo DISTRIBUÍDO \(total\):\s+([\d.]+) segundos', output)
    if dist_match:
        test.t_distributed = float(dist_match.group(1))
    
    # Extrair overhead de divisão
    split_match = re.search(r'Overhead de divisão:\s+([\d.]+) s', output)
    if split_match:
        test.overhead_split = float(split_match.group(1))
    
    # Extrair overhead de comunicação
    comm_match = re.search(r'Overhead de comunicação:\s+([\d.]+) s', output)
    if comm_match:
        test.overhead_comm = float(comm_match.group(1))
    
    # Extrair computação paralela
    compute_match = re.search(r'Computação paralela \(média\):\s+([\d.]+) s', output)
    if compute_match:
        test.time_compute = float(compute_match.group(1))
    
    # Extrair overhead de reconstrução
    recon_match = re.search(r'Overhead de reconstrução:\s+([\d.]+) s', output)
    if recon_match:
        test.overhead_reconstruct = float(recon_match.group(1))
    
    return test


def main():
    print("="*70)
    print("GERADOR AUTOMÁTICO DE GRÁFICOS A PARTIR DA SAÍDA DO SERVIDOR")
    print("="*70)
    print()
    print("Este script extrai automaticamente os dados da saída do servidor")
    print("e gera os gráficos para você!")
    print()
    
    tests = []
    
    while True:
        print("\n" + "="*70)
        print("ADICIONAR TESTE")
        print("="*70)
        print()
        print("Cole TODA a saída do servidor abaixo (desde 'Iniciando servidor'")
        print("até 'Os resultados são iguais? True')")
        print()
        print("Quando terminar de colar, pressione ENTER duas vezes:")
        print()
        
        lines = []
        empty_count = 0
        
        while True:
            try:
                line = input()
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                    lines.append(line)
            except EOFError:
                break
        
        if not lines:
            break
        
        output = "\n".join(lines)
        
        try:
            test = parse_server_output(output)
            tests.append(test)
            
            print("\n✅ Dados extraídos com sucesso!")
            print(f"   Matriz: {test.size}×{test.size}")
            print(f"   Clientes: {test.num_clients}")
            print(f"   Speedup: {test.speedup:.2f}x")
            print(f"   Eficiência: {test.efficiency:.1f}%")
            print(f"\n📝 Total de testes coletados: {len(tests)}")
            
        except Exception as e:
            print(f"\n❌ Erro ao extrair dados: {e}")
            print("Verifique se colou a saída completa do servidor.")
            continue
        
        choice = input("\nDeseja adicionar outro teste? (s/n): ").lower()
        if choice != 's':
            break
    
    if not tests:
        print("\n⚠️  Nenhum teste foi adicionado. Encerrando...")
        return
    
    print("\n" + "="*70)
    print("GERANDO GRÁFICOS...")
    print("="*70)
    
    # Gerar gráficos comparativos
    print("\n📊 Criando gráficos comparativos...")
    create_comparison_graphs(tests, "performance_analysis.png")
    
    # Gerar gráfico de pizza para cada teste
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
