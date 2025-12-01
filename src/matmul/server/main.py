import socket
import threading
import time
import argparse
from typing import Dict, List, Tuple

from matmul.utils.matrix_utils import (
    generate_matrix,
    split_matrix_by_rows,
    print_matrix,
    multiply,
    Matrix,
)
from matmul.utils.protocol import send_json, recv_json


# CONFIGURAÇÕES DO SERVIDOR
HOST = "127.0.0.1"   # localhost
PORT = 5000          # porta do servidor


# FUNÇÃO PARA LIDAR COM CADA CLIENTE
def handle_client(
    conn: socket.socket,
    addr: Tuple[str, int],
    block_index: int,
    A_block: Matrix,
    B: Matrix,
    results: Dict[int, Matrix],
    lock: threading.Lock,
    metrics: Dict[str, float],
) -> None:
    """
    Envia o bloco de A e a matriz B para o cliente,
    recebe o bloco de C calculado e guarda no dicionário 'results'.
    """
    try:
        print(f"[SERVIDOR] Cliente conectado: {addr} | bloco_index={block_index}")

        # Monta a tarefa para o cliente
        task = {
            "type": "task",
            "block_index": block_index,
            "A_block": A_block,
            "B": B,
        }

        # Envia a tarefa (overhead de comunicação)
        t_send_start = time.perf_counter()
        send_json(conn, task)
        t_send_end = time.perf_counter()

        # Aguarda o resultado (tempo de computação no cliente)
        t_compute_start = time.perf_counter()
        response = recv_json(conn)
        t_compute_end = time.perf_counter()

        if response.get("type") != "result":
            print(f"[SERVIDOR] Resposta inesperada do cliente {addr}: {response}")
            return

        result_block_index = response["block_index"]
        C_block = response["C_block"]

        # Guarda o resultado no dicionário compartilhado
        with lock:
            results[result_block_index] = C_block
            # Acumula métricas
            metrics["overhead_send"] += (t_send_end - t_send_start)
            metrics["time_compute"] += (t_compute_end - t_compute_start)

        print(f"[SERVIDOR] Recebeu resultado do cliente {addr} (bloco {result_block_index})")

    except Exception as e:
        print(f"[SERVIDOR] Erro com cliente {addr}: {e}")
    finally:
        conn.close()
        print(f"[SERVIDOR] Conexão fechada com {addr}")


# FUNÇÃO PRINCIPAL DO SERVIDOR
def main(num_clients: int) -> None:
    print(f"[SERVIDOR] Iniciando servidor de multiplicação distribuída...")
    print(f"[SERVIDOR] Esperando {num_clients} clientes em {HOST}:{PORT}")

    # 1- gera matrizes A e B
    try:
        rows_A = int(input("Número de linhas da matriz A: "))
        cols_A = int(input("Número de colunas da matriz A (e linhas de B): "))
        cols_B = int(input("Número de colunas da matriz B: "))
    except ValueError:
        print("Valor inválido! Usando valores padrão A=6x4 e B=4x5.")
        rows_A, cols_A, cols_B = 6, 4, 5

    rows_B = cols_A  # obrigatório para compatibilidade

    # gerar matrizes A e B
    A = generate_matrix(rows_A, cols_A)
    B = generate_matrix(rows_B, cols_B)

    # print_matrix(A, "Matriz A")
    # print_matrix(B, "Matriz B")

    start_seq = time.perf_counter()
    C_seq = multiply(A, B)
    end_seq = time.perf_counter()
    seq_time = end_seq - start_seq

    # print_matrix(C_seq, "Matriz C_seq (resultado sequencial)")
    print(f"[SERVIDOR] Tempo total (sequencial): {seq_time:.4f} segundos\n")

    # 2- divide A em blocos de linhas, um para cada cliente
    t_split_start = time.perf_counter()
    blocks = split_matrix_by_rows(A, num_clients)
    t_split_end = time.perf_counter()
    print(f"[SERVIDOR] A foi dividida em {len(blocks)} blocos para {num_clients} clientes.")

    # dicionário para receber blocos de C e métricas
    results: Dict[int, Matrix] = {}
    metrics: Dict[str, float] = {
        "overhead_split": t_split_end - t_split_start,
        "overhead_send": 0.0,
        "time_compute": 0.0,
        "overhead_reconstruct": 0.0,
    }
    lock = threading.Lock()

    # 3- cria socket servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(num_clients)

        threads: List[threading.Thread] = []

        start_time = time.perf_counter()
        print("[SERVIDOR] Aguardando conexões dos clientes...")

        # 4- aceita conexões e dispara threads
        for block_index in range(num_clients):
            conn, addr = server_sock.accept()
            print(f"[SERVIDOR] Conexão aceita de {addr} para bloco {block_index}")

            A_block = blocks[block_index]

            t = threading.Thread(
                target=handle_client,
                args=(conn, addr, block_index, A_block, B, results, lock, metrics),
                daemon=True,
            )
            t.start()
            threads.append(t)

        # 5- espera todas as threads finalizarem
        for t in threads:
            t.join()

        end_time = time.perf_counter()

    # 6- junta os blocos de C na ordem
    if len(results) != num_clients:
        print("[SERVIDOR] Nem todos os resultados foram recebidos. Resultados parciais:")
        print(results)
        return

    # ordena pelos índices de bloco e concatena as linhas
    t_reconstruct_start = time.perf_counter()
    C: Matrix = []
    for idx in sorted(results.keys()):
        C.extend(results[idx])
    t_reconstruct_end = time.perf_counter()
    metrics["overhead_reconstruct"] = t_reconstruct_end - t_reconstruct_start

    # Calcula métricas finais
    dist_time = end_time - start_time
    total_overhead = (metrics["overhead_split"] + 
                      metrics["overhead_send"] + 
                      metrics["overhead_reconstruct"])
    time_parallel_computation = metrics["time_compute"] / num_clients  # Média por cliente
    
    # print_matrix(C, "Matriz C (resultado distribuído)")
    print("\n" + "="*70)
    print("ANÁLISE DE DESEMPENHO")
    print("="*70)
    print(f"⏱️  Tempo SEQUENCIAL:              {seq_time:.6f} segundos")
    print(f"⏱️  Tempo DISTRIBUÍDO (total):     {dist_time:.6f} segundos")
    print()
    print("📊 DECOMPOSIÇÃO DO TEMPO DISTRIBUÍDO:")
    print(f"   • Overhead de divisão:         {metrics['overhead_split']:.6f} s ({metrics['overhead_split']/dist_time*100:.1f}%)")
    print(f"   • Overhead de comunicação:     {metrics['overhead_send']:.6f} s ({metrics['overhead_send']/dist_time*100:.1f}%)")
    print(f"   • Computação paralela (média): {time_parallel_computation:.6f} s ({time_parallel_computation/dist_time*100:.1f}%)")
    print(f"   • Overhead de reconstrução:    {metrics['overhead_reconstruct']:.6f} s ({metrics['overhead_reconstruct']/dist_time*100:.1f}%)")
    print(f"   • Total de overhead:           {total_overhead:.6f} s ({total_overhead/dist_time*100:.1f}%)")
    print()
    print("🚀 MÉTRICAS DE PARALELISMO:")
    speedup = seq_time / dist_time
    efficiency = speedup / num_clients * 100
    print(f"   • Speedup:                     {speedup:.2f}x")
    print(f"   • Eficiência:                  {efficiency:.1f}%")
    print(f"   • Ganho de tempo:              {(seq_time - dist_time):.6f} s")
    
    if speedup > 1.0:
        print(f"   ✅ Distribuído é {speedup:.2f}x MAIS RÁPIDO!")
    else:
        print(f"   ⚠️  Distribuído é {1/speedup:.2f}x MAIS LENTO (overhead domina)")
        print(f"   💡 Dica: Use matrizes maiores para melhor desempenho")
    print("="*70)

    # 7- (opcional mas MUITO bom pra apresentação): validar com cálculo local
    print("\n[SERVIDOR] Validando resultado distribuído...")
    iguais = C == C_seq
    print(f"[SERVIDOR] Os resultados distribuído e sequencial são iguais? {iguais}")

# PONTO DE ENTRADA (CLI)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Servidor de multiplicação de matrizes distribuída"
    )
    parser.add_argument(
        "--num-clients",
        type=int,
        default=2,
        help="Número de clientes que o servidor deve aguardar (padrão: 2)",
    )
    args = parser.parse_args()

    main(args.num_clients)
