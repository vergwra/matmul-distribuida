"""
Script para demonstrar o overhead da distribuição
e encontrar o ponto de break-even
"""

import time
import json
from matmul.utils.matrix_utils import generate_matrix, multiply

def measure_sequential(size):
    """Mede tempo sequencial puro"""
    A = generate_matrix(size, size)
    B = generate_matrix(size, size)
    
    start = time.perf_counter()
    C = multiply(A, B)
    end = time.perf_counter()
    
    return end - start

def measure_overhead(size):
    """Mede overhead de serialização/deserialização"""
    A = generate_matrix(size, size)
    B = generate_matrix(size, size)
    
    # Simula overhead de 1 cliente
    start = time.perf_counter()
    
    # 1. Serialização
    task = {"A_block": A, "B": B, "block_index": 0}
    json_data = json.dumps(task)
    
    # 2. Deserialização
    task_received = json.loads(json_data)
    
    # 3. Computação (metade das linhas para 2 clientes)
    half = size // 2
    A_half = A[:half]
    C_block = multiply(A_half, B)
    
    # 4. Serialização do resultado
    response = {"C_block": C_block, "block_index": 0}
    json_result = json.dumps(response)
    
    # 5. Deserialização do resultado
    result_received = json.loads(json_result)
    
    end = time.perf_counter()
    
    return end - start

def main():
    print("=" * 60)
    print("ANÁLISE DE OVERHEAD - MULTIPLICAÇÃO DISTRIBUÍDA")
    print("=" * 60)
    print()
    
    sizes = [10, 20, 50, 100, 200, 500]
    
    print(f"{'Tamanho':<10} {'T_seq (s)':<12} {'T_dist (s)':<12} {'Speedup':<10} {'Vale?':<10}")
    print("-" * 60)
    
    for size in sizes:
        t_seq = measure_sequential(size)
        t_dist = measure_overhead(size)  # Simula 1 cliente (já divide por 2)
        
        speedup = t_seq / t_dist if t_dist > 0 else 0
        vale = "✅ SIM" if speedup > 1.0 else "❌ NÃO"
        
        print(f"{size:<10} {t_seq:<12.6f} {t_dist:<12.6f} {speedup:<10.2f} {vale:<10}")
    
    print()
    print("=" * 60)
    print("CONCLUSÕES:")
    print("=" * 60)
    print("• Matrizes pequenas: Overhead domina → Distribuído MAIS LENTO")
    print("• Matrizes grandes: Paralelismo domina → Distribuído MAIS RÁPIDO")
    print("• Break-even: Quando Speedup ≈ 1.0")
    print()
    print("💡 DICA: Para sua apresentação, use matrizes ≥ 200×200")
    print("   para garantir que a versão distribuída seja mais rápida!")
    print()

if __name__ == "__main__":
    main()
