import random
from typing import List, Tuple

Matrix = List[List[float]]

def generate_matrix(rows: int, cols: int, min_val: int = 1, max_val: int = 10) -> Matrix:
    """
    Gera uma matriz linhas x colunas com valores aleatórios entre valor minimo e valor maximo.
    """
    return [
        [random.randint(min_val, max_val) for _ in range(cols)]
        for _ in range(rows)
    ]

def multiply(A: Matrix, B: Matrix) -> Matrix:
    """
    Multiplica duas matrizes A e B usando a definição matemática:
    C[i][j] = sum(A[i][k] * B[k][j])
    """

    if len(A[0]) != len(B):
        raise ValueError(f"Dimensões incompatíveis: {len(A[0])} != {len(B)}")

    n = len(A)
    m = len(A[0])
    p = len(B[0])

    # Cria matriz C resultado (n x p)
    C = [[0 for _ in range(p)] for _ in range(n)]

    # Multiplicação clássica
    for i in range(n):
        for j in range(p):
            soma = 0
            for k in range(m):
                soma += A[i][k] * B[k][j]
            C[i][j] = soma

    return C

def split_matrix_by_rows(A: Matrix, num_parts: int) -> List[Matrix]:
    """
    Divide a matriz A em `num_parts` blocos de linhas.

    Exemplo:
    A com 10 linhas, num_parts = 2 →
        - bloco1: 5 linhas
        - bloco2: 5 linhas

    Retorna: [A1, A2, ...]
    """

    rows = len(A)
    block_size = rows // num_parts
    remainder = rows % num_parts

    blocks = []
    start = 0

    for i in range(num_parts):
        extra = 1 if i < remainder else 0
        end = start + block_size + extra
        blocks.append(A[start:end])
        start = end

    return blocks

def print_matrix(M: Matrix, name: str = "Matriz"):
    """
    Exibe a matriz de forma legível.
    """
    print(f"\n{name}:")
    for row in M:
        print("  ", row)
    print()


def dimensions(M: Matrix) -> Tuple[int, int]:
    """
    Retorna (linhas, colunas) da matriz.
    """
    return len(M), len(M[0])

