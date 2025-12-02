import socket
import argparse
import time
import struct
from typing import Tuple

from matmul.utils.matrix_utils import multiply, print_matrix, Matrix
from matmul.utils.protocol import send_json, recv_json


HOST_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 5000


def main(host: str, port: int, verbose: bool) -> None:
    print(f"[CLIENTE] Iniciando cliente. Conectando a {host}:{port}...")

    # 1- abre o socket e conecta no servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((host, port))
            print("[CLIENTE] Conectado ao servidor. Aguardando tarefas...")

            while True:
                # 2- recebe a tarefa do servidor
                try:
                    data = recv_json(sock)
                except (ConnectionError, struct.error):
                    print("[CLIENTE] Conexão com o servidor perdida.")
                    break

                if data.get("type") == "exit":
                    print("[CLIENTE] Recebido comando de saída. Encerrando.")
                    break

                if data.get("type") != "task":
                    print(f"[CLIENTE] Mensagem inesperada do servidor: {data}")
                    continue

                block_index = data["block_index"]
                A_block: Matrix = data["A_block"]
                B: Matrix = data["B"]

                print(f"[CLIENTE] Tarefa recebida. Bloco de índice {block_index}.")

                if verbose:
                    print_matrix(A_block, f"A_block (bloco {block_index}) recebido")
                    print_matrix(B, "Matriz B recebida")

                # 3- calcula o bloco de C
                print(f"[CLIENTE] Iniciando computação do bloco {block_index}...")
                start_compute = time.perf_counter()
                C_block: Matrix = multiply(A_block, B)
                end_compute = time.perf_counter()
                compute_time = end_compute - start_compute
                
                print(f"[CLIENTE] Tempo de computação (bloco {block_index}): {compute_time:.6f} segundos")

                if verbose:
                    print_matrix(C_block, f"C_block calculado (bloco {block_index})")

                # 4- envia o resultado de volta para o servidor
                response = {
                    "type": "result",
                    "block_index": block_index,
                    "C_block": C_block,
                }

                send_json(sock, response)
                print(f"[CLIENTE] Resultado do bloco {block_index} enviado ao servidor.")
                print("[CLIENTE] Aguardando próxima tarefa...\n")

        except ConnectionRefusedError:
            print(f"[CLIENTE] Não foi possível conectar a {host}:{port}. O servidor está ligado?")
        except KeyboardInterrupt:
            print("\n[CLIENTE] Encerrando manualmente.")
        except Exception as e:
            print(f"[CLIENTE] Erro: {e}")

    print("[CLIENTE] Conexão encerrada.")
     

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Cliente de multiplicação de matrizes distribuída"
    )
    parser.add_argument(
        "--host",
        type=str,
        default=HOST_DEFAULT,
        help=f"Endereço do servidor (padrão: {HOST_DEFAULT})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PORT_DEFAULT,
        help=f"Porta do servidor (padrão: {PORT_DEFAULT})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostra as matrizes recebidas e o bloco calculado.",
    )

    args = parser.parse_args()
    main(args.host, args.port, args.verbose)
