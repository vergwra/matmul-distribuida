import json
import struct
import socket
from typing import Any, Dict

def send_json(sock: socket.socket, data: Dict[str, Any]) -> None:
    """
    Envia um dicionário Python como JSON pelo socket, com cabeçalho de tamanho.
    """
    raw = json.dumps(data).encode("utf-8")
    size = struct.pack("!I", len(raw))  # 4 bytes, network order (big-endian)
    sock.sendall(size + raw)


def recv_exactly(sock: socket.socket, size: int) -> bytes:
    """
    Lê exatamente 'size' bytes do socket, ou levanta erro se a conexão fechar.
    """
    chunks = []
    bytes_read = 0

    while bytes_read < size:
        chunk = sock.recv(size - bytes_read)
        if not chunk:
            # conexão fechada antes de receber tudo
            raise ConnectionError("Conexão encerrada inesperadamente.")
        chunks.append(chunk)
        bytes_read += len(chunk)

    return b"".join(chunks)


def recv_json(sock: socket.socket) -> Dict[str, Any]:
    """
    Recebe um JSON com cabeçalho de tamanho e devolve como dicionário.
    """
    # Primeiro lê 4 bytes com o tamanho
    size_bytes = recv_exactly(sock, 4)
    size = struct.unpack("!I", size_bytes)[0]

    # Agora lê exatamente 'size' bytes de payload
    raw = recv_exactly(sock, size)
    data = json.loads(raw.decode("utf-8"))
    return data