"""
Script SIMPLES: Cole os dados do servidor e salva em arquivo
Depois use generate_from_file.py para gerar os gráficos
"""

import json
import re


def extract_data_from_output(output: str) -> dict:
    """Extrai dados da saída do servidor"""
    data = {}
    
    # Tamanho da matriz
    size_match = re.search(r'Número de linhas da matriz A: (\d+)', output)
    data['size'] = int(size_match.group(1)) if size_match else 0
    
    # Número de clientes
    clients_match = re.search(r'Esperando (\d+) clientes', output)
    data['num_clients'] = int(clients_match.group(1)) if clients_match else 2
    
    # Tempo sequencial
    seq_match = re.search(r'Tempo SEQUENCIAL:\s+([\d.]+) segundos', output)
    data['t_sequential'] = float(seq_match.group(1)) if seq_match else 0.0
    
    # Tempo distribuído
    dist_match = re.search(r'Tempo DISTRIBUÍDO \(total\):\s+([\d.]+) segundos', output)
    data['t_distributed'] = float(dist_match.group(1)) if dist_match else 0.0
    
    # Overhead de divisão
    split_match = re.search(r'Overhead de divisão:\s+([\d.]+) s', output)
    data['overhead_split'] = float(split_match.group(1)) if split_match else 0.0
    
    # Overhead de comunicação
    comm_match = re.search(r'Overhead de comunicação:\s+([\d.]+) s', output)
    data['overhead_comm'] = float(comm_match.group(1)) if comm_match else 0.0
    
    # Computação paralela
    compute_match = re.search(r'Computação paralela \(média\):\s+([\d.]+) s', output)
    data['time_compute'] = float(compute_match.group(1)) if compute_match else 0.0
    
    # Overhead de reconstrução
    recon_match = re.search(r'Overhead de reconstrução:\s+([\d.]+) s', output)
    data['overhead_reconstruct'] = float(recon_match.group(1)) if recon_match else 0.0
    
    return data


def main():
    print("="*70)
    print("SALVAR DADOS DO TESTE")
    print("="*70)
    print()
    print("Cole TODA a saída do servidor abaixo e pressione ENTER duas vezes:")
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
    
    output = "\n".join(lines)
    
    try:
        data = extract_data_from_output(output)
        
        # Carregar dados existentes
        try:
            with open('test_results.json', 'r') as f:
                all_tests = json.load(f)
        except FileNotFoundError:
            all_tests = []
        
        # Adicionar novo teste
        all_tests.append(data)
        
        # Salvar
        with open('test_results.json', 'w') as f:
            json.dump(all_tests, f, indent=2)
        
        print("\n✅ Dados salvos com sucesso!")
        print(f"   Matriz: {data['size']}×{data['size']}")
        print(f"   Speedup: {data['t_sequential']/data['t_distributed']:.2f}x")
        print(f"\n📝 Total de testes salvos: {len(all_tests)}")
        print(f"📁 Arquivo: test_results.json")
        print()
        print("💡 Execute 'python generate_from_file.py' para gerar os gráficos!")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
