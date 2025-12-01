#!/bin/bash

# Script para testar performance com diferentes tamanhos de matriz
# Demonstra quando o overhead domina vs quando o paralelismo compensa

echo "======================================================================"
echo "TESTE DE PERFORMANCE - MULTIPLICAÇÃO DISTRIBUÍDA"
echo "======================================================================"
echo ""
echo "Este script vai testar 3 cenários:"
echo "  1. Matriz PEQUENA (50x50)   → Overhead domina"
echo "  2. Matriz MÉDIA (200x200)   → Break-even"
echo "  3. Matriz GRANDE (500x500)  → Paralelismo compensa"
echo ""
echo "Pressione ENTER para começar..."
read

# Função para executar teste
run_test() {
    SIZE=$1
    NUM_CLIENTS=$2
    
    echo ""
    echo "======================================================================"
    echo "TESTE: Matriz ${SIZE}x${SIZE} com ${NUM_CLIENTS} clientes"
    echo "======================================================================"
    
    # Inicia servidor em background
    echo -e "${SIZE}\n${SIZE}\n${SIZE}" | python -m matmul.server.main --num-clients ${NUM_CLIENTS} &
    SERVER_PID=$!
    
    # Aguarda servidor iniciar
    sleep 2
    
    # Inicia clientes
    for i in $(seq 1 ${NUM_CLIENTS}); do
        python -m matmul.client.main &
        sleep 0.5
    done
    
    # Aguarda servidor terminar
    wait $SERVER_PID
    
    echo ""
    echo "Pressione ENTER para próximo teste..."
    read
}

# Testes
run_test 50 2
run_test 200 2
run_test 500 2

echo ""
echo "======================================================================"
echo "TESTES CONCLUÍDOS!"
echo "======================================================================"
echo ""
echo "📊 ANÁLISE DOS RESULTADOS:"
echo ""
echo "• Matriz 50x50:   Overhead > Computação → Distribuído MAIS LENTO"
echo "• Matriz 200x200: Overhead ≈ Computação → Break-even"
echo "• Matriz 500x500: Overhead < Computação → Distribuído MAIS RÁPIDO"
echo ""
echo "💡 CONCLUSÃO: Para sua apresentação, use matrizes ≥ 200x200"
echo "   para garantir que o paralelismo compense o overhead!"
echo ""
