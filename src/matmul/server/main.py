import socket
import threading
import time
import argparse
from typing import Dict, List, Tuple, Optional

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


def handle_client_task(
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
    Envia uma tarefa para um cliente JÁ CONECTADO e aguarda o resultado.
    """
    try:
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

        # print(f"[SERVIDOR] Recebeu resultado do cliente {addr} (bloco {result_block_index})")

    except Exception as e:
        print(f"[SERVIDOR] Erro ao comunicar com cliente {addr}: {e}")


def run_multiplication(
    clients: List[Tuple[socket.socket, Tuple[str, int]]],
    rows_A: int,
    cols_A: int,
    cols_B: int
) -> None:
    num_clients = len(clients)
    rows_B = cols_A

    print(f"\n[SERVIDOR] Gerando matrizes A ({rows_A}x{cols_A}) e B ({rows_B}x{cols_B})...")
    A = generate_matrix(rows_A, cols_A)
    B = generate_matrix(rows_B, cols_B)

    # Cálculo Sequencial (para comparação)
    print("[SERVIDOR] Calculando sequencialmente para base de comparação...")
    start_seq = time.perf_counter()
    C_seq = multiply(A, B)
    end_seq = time.perf_counter()
    seq_time = end_seq - start_seq
    print(f"[SERVIDOR] Tempo sequencial: {seq_time:.4f} s")

    # Cálculo Distribuído
    print("[SERVIDOR] Iniciando cálculo distribuído...")
    start_time = time.perf_counter()

    # 1. Divisão
    t_split_start = time.perf_counter()
    blocks = split_matrix_by_rows(A, num_clients)
    t_split_end = time.perf_counter()

    results: Dict[int, Matrix] = {}
    metrics: Dict[str, float] = {
        "overhead_split": t_split_end - t_split_start,
        "overhead_send": 0.0,
        "time_compute": 0.0,
        "overhead_reconstruct": 0.0,
    }
    lock = threading.Lock()
    threads: List[threading.Thread] = []

    # 2. Distribuição e Execução
    for i, (conn, addr) in enumerate(clients):
        A_block = blocks[i]
        t = threading.Thread(
            target=handle_client_task,
            args=(conn, addr, i, A_block, B, results, lock, metrics),
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end_time = time.perf_counter()

    # 3. Reconstrução
    if len(results) != num_clients:
        print("[SERVIDOR] ERRO: Nem todos os resultados foram recebidos.")
        return

    t_reconstruct_start = time.perf_counter()
    C: Matrix = []
    for idx in sorted(results.keys()):
        C.extend(results[idx])
    t_reconstruct_end = time.perf_counter()
    metrics["overhead_reconstruct"] = t_reconstruct_end - t_reconstruct_start

    # Métricas Finais
    dist_time = end_time - start_time
    total_overhead = (metrics["overhead_split"] + 
                      metrics["overhead_send"] + 
                      metrics["overhead_reconstruct"])
    time_parallel_computation = metrics["time_compute"] / num_clients

    print("\n" + "="*70)
    print("ANÁLISE DE DESEMPENHO")
    print("="*70)
    print(f"⏱️  Tempo SEQUENCIAL:              {seq_time:.6f} segundos")
    print(f"⏱️  Tempo DISTRIBUÍDO (total):     {dist_time:.6f} segundos")
    print()
    print("📊 DECOMPOSIÇÃO DO TEMPO DISTRIBUÍDO:")
    print(f"   • Overhead de divisão:         {metrics['overhead_split']:.6f} s")
    print(f"   • Overhead de comunicação:     {metrics['overhead_send']:.6f} s")
    print(f"   • Computação paralela (média): {time_parallel_computation:.6f} s")
    print(f"   • Overhead de reconstrução:    {metrics['overhead_reconstruct']:.6f} s")
    print()
    print("🚀 MÉTRICAS DE PARALELISMO:")
    speedup = seq_time / dist_time
    efficiency = speedup / num_clients * 100
    print(f"   • Speedup:                     {speedup:.2f}x")
    print(f"   • Eficiência:                  {efficiency:.1f}%")
    
    if speedup > 1.0:
        print(f"   ✅ Distribuído é {speedup:.2f}x MAIS RÁPIDO!")
    else:
        print(f"   ⚠️  Distribuído é {1/speedup:.2f}x MAIS LENTO (overhead domina)")
    print("="*70)

    # Validação
    iguais = C == C_seq
    print(f"[SERVIDOR] Validação: Resultado distribuído == Sequencial? {iguais}\n")


def main(num_clients: int) -> None:
    print(f"[SERVIDOR] Iniciando servidor em {HOST}:{PORT}")
    print(f"[SERVIDOR] Aguardando conexão de {num_clients} clientes...")

    clients: List[Tuple[socket.socket, Tuple[str, int]]] = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((HOST, PORT))
        server_sock.listen(num_clients)

        # 1. Fase de Conexão (Bloqueante até todos conectarem)
        while len(clients) < num_clients:
            conn, addr = server_sock.accept()
            clients.append((conn, addr))
            print(f"[SERVIDOR] Cliente conectado: {addr} ({len(clients)}/{num_clients})")

        print("\n[SERVIDOR] Todos os clientes conectados! Iniciando modo interativo.")

        # 2. Loop Interativo
        try:
            while True:
                print("\n" + "-"*30)
                print(" MENU PRINCIPAL")
                print("-" * 30)
                print("1. Nova Multiplicação")
                print("2. Sair")
                
                opcao = input("Escolha uma opção: ").strip()

                if opcao == "1":
                    try:
                        rA = int(input("Linhas A: "))
                        cA = int(input("Colunas A (e Linhas B): "))
                        cB = int(input("Colunas B: "))
                        run_multiplication(clients, rA, cA, cB)
                    except ValueError:
                        print("Entrada inválida. Use números inteiros.")
                elif opcao == "2":
                    print("Encerrando servidor e avisando clientes...")
                    break
                else:
                    print("Opção inválida.")

        except KeyboardInterrupt:
            print("\nInterrupção manual.")
        finally:
            # Envia sinal de exit para clientes e fecha conexões
            for conn, _ in clients:
                try:
                    send_json(conn, {"type": "exit"})
                    conn.close()
                except:
                    pass
            print("[SERVIDOR] Encerrado.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de Matrizes Persistente")
    parser.add_argument("--num-clients", type=int, default=2, help="Número de clientes esperados")
    args = parser.parse_args()
    main(args.num_clients)
