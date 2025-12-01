"""
Script para gerar gráficos de análise de performance
Mostra comparação de tempos e decomposição de overhead
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict

# Configuração de estilo
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 10


class PerformanceData:
    """Armazena dados de um teste de performance"""
    def __init__(self, size: int, num_clients: int):
        self.size = size
        self.num_clients = num_clients
        self.t_sequential = 0.0
        self.t_distributed = 0.0
        self.overhead_split = 0.0
        self.overhead_comm = 0.0
        self.time_compute = 0.0
        self.overhead_reconstruct = 0.0
    
    @property
    def total_overhead(self) -> float:
        return self.overhead_split + self.overhead_comm + self.overhead_reconstruct
    
    @property
    def speedup(self) -> float:
        return self.t_sequential / self.t_distributed if self.t_distributed > 0 else 0
    
    @property
    def efficiency(self) -> float:
        return (self.speedup / self.num_clients) * 100 if self.num_clients > 0 else 0


def create_comparison_graphs(tests: List[PerformanceData], output_file: str = "performance_analysis.png"):
    """
    Cria um conjunto de gráficos comparativos
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Preparar dados
    sizes = [f"{t.size}×{t.size}" for t in tests]
    t_seq = [t.t_sequential for t in tests]
    t_dist = [t.t_distributed for t in tests]
    speedups = [t.speedup for t in tests]
    efficiencies = [t.efficiency for t in tests]
    
    # ============================================================
    # GRÁFICO 1: Comparação de Tempos (Barras)
    # ============================================================
    ax1 = plt.subplot(2, 3, 1)
    x = np.arange(len(tests))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, t_seq, width, label='Sequencial', color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x + width/2, t_dist, width, label='Distribuído', color='#3498db', alpha=0.8)
    
    ax1.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax1.set_ylabel('Tempo (segundos)', fontweight='bold')
    ax1.set_title('⏱️ Comparação: Sequencial vs Distribuído', fontsize=12, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(sizes, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}s',
                    ha='center', va='bottom', fontsize=8)
    
    # ============================================================
    # GRÁFICO 2: Speedup
    # ============================================================
    ax2 = plt.subplot(2, 3, 2)
    colors = ['#27ae60' if s > 1.0 else '#e74c3c' for s in speedups]
    bars = ax2.bar(x, speedups, color=colors, alpha=0.8)
    ax2.axhline(y=1.0, color='black', linestyle='--', linewidth=2, label='Break-even (1.0x)')
    
    ax2.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax2.set_ylabel('Speedup (x)', fontweight='bold')
    ax2.set_title('🚀 Speedup (T_seq / T_dist)', fontsize=12, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(sizes, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # Adicionar valores
    for i, (bar, speedup) in enumerate(zip(bars, speedups)):
        height = bar.get_height()
        label = f'{speedup:.2f}x'
        if speedup > 1.0:
            label += ' ✓'
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                label, ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # ============================================================
    # GRÁFICO 3: Eficiência
    # ============================================================
    ax3 = plt.subplot(2, 3, 3)
    colors_eff = ['#27ae60' if e >= 70 else '#f39c12' if e >= 50 else '#e74c3c' for e in efficiencies]
    bars = ax3.bar(x, efficiencies, color=colors_eff, alpha=0.8)
    ax3.axhline(y=100, color='black', linestyle='--', linewidth=1, alpha=0.5, label='Ideal (100%)')
    
    ax3.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax3.set_ylabel('Eficiência (%)', fontweight='bold')
    ax3.set_title('📈 Eficiência do Paralelismo', fontsize=12, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(sizes, rotation=45, ha='right')
    ax3.set_ylim(0, 110)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # Adicionar valores
    for bar, eff in zip(bars, efficiencies):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{eff:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # ============================================================
    # GRÁFICO 4: Decomposição do Tempo Distribuído (Stacked Bar)
    # ============================================================
    ax4 = plt.subplot(2, 3, 4)
    
    overhead_split = [t.overhead_split for t in tests]
    overhead_comm = [t.overhead_comm for t in tests]
    time_compute = [t.time_compute for t in tests]
    overhead_recon = [t.overhead_reconstruct for t in tests]
    
    ax4.bar(x, overhead_split, label='Overhead Divisão', color='#9b59b6', alpha=0.8)
    ax4.bar(x, overhead_comm, bottom=overhead_split, 
            label='Overhead Comunicação', color='#e67e22', alpha=0.8)
    
    bottom_compute = np.array(overhead_split) + np.array(overhead_comm)
    ax4.bar(x, time_compute, bottom=bottom_compute,
            label='Computação Paralela', color='#27ae60', alpha=0.8)
    
    bottom_recon = bottom_compute + np.array(time_compute)
    ax4.bar(x, overhead_recon, bottom=bottom_recon,
            label='Overhead Reconstrução', color='#95a5a6', alpha=0.8)
    
    ax4.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax4.set_ylabel('Tempo (segundos)', fontweight='bold')
    ax4.set_title('📊 Decomposição do Tempo Distribuído', fontsize=12, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(sizes, rotation=45, ha='right')
    ax4.legend(loc='upper left')
    ax4.grid(axis='y', alpha=0.3)
    
    # ============================================================
    # GRÁFICO 5: Overhead vs Computação (Percentual)
    # ============================================================
    ax5 = plt.subplot(2, 3, 5)
    
    overhead_pct = [(t.total_overhead / t.t_distributed * 100) for t in tests]
    compute_pct = [(t.time_compute / t.t_distributed * 100) for t in tests]
    
    ax5.bar(x, overhead_pct, label='Overhead Total', color='#e74c3c', alpha=0.8)
    ax5.bar(x, compute_pct, bottom=overhead_pct, 
            label='Computação Paralela', color='#27ae60', alpha=0.8)
    
    ax5.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax5.set_ylabel('Percentual (%)', fontweight='bold')
    ax5.set_title('🥧 Overhead vs Computação (%)', fontsize=12, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(sizes, rotation=45, ha='right')
    ax5.set_ylim(0, 100)
    ax5.legend()
    ax5.grid(axis='y', alpha=0.3)
    
    # Adicionar valores
    for i in range(len(tests)):
        # Overhead
        ax5.text(i, overhead_pct[i]/2, f'{overhead_pct[i]:.1f}%',
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        # Computação
        ax5.text(i, overhead_pct[i] + compute_pct[i]/2, f'{compute_pct[i]:.1f}%',
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
    
    # ============================================================
    # GRÁFICO 6: Soma Overhead Comunicação + Computação Paralela
    # ============================================================
    ax6 = plt.subplot(2, 3, 6)
    
    comm_plus_compute = [t.overhead_comm + t.time_compute for t in tests]
    
    bars = ax6.bar(x, comm_plus_compute, color='#3498db', alpha=0.8, label='Comunicação + Computação')
    
    # Adicionar linha de referência do tempo sequencial
    ax6.plot(x, t_seq, 'ro-', linewidth=2, markersize=8, label='Tempo Sequencial (ref)')
    
    ax6.set_xlabel('Tamanho da Matriz', fontweight='bold')
    ax6.set_ylabel('Tempo (segundos)', fontweight='bold')
    ax6.set_title('⚡ Overhead Comunicação + Computação Paralela', fontsize=12, fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels(sizes, rotation=45, ha='right')
    ax6.legend()
    ax6.grid(axis='y', alpha=0.3)
    
    # Adicionar valores
    for i, (bar, val) in enumerate(zip(bars, comm_plus_compute)):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}s', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráficos salvos em: {output_file}")
    plt.show()


def create_detailed_breakdown_chart(test: PerformanceData, output_file: str = "breakdown_chart.png"):
    """
    Cria um gráfico de pizza detalhado para um teste específico
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ============================================================
    # PIZZA 1: Decomposição completa
    # ============================================================
    labels = [
        f'Overhead Divisão\n{test.overhead_split:.6f}s',
        f'Overhead Comunicação\n{test.overhead_comm:.6f}s',
        f'Computação Paralela\n{test.time_compute:.6f}s',
        f'Overhead Reconstrução\n{test.overhead_reconstruct:.6f}s'
    ]
    sizes = [test.overhead_split, test.overhead_comm, test.time_compute, test.overhead_reconstruct]
    colors = ['#9b59b6', '#e67e22', '#27ae60', '#95a5a6']
    explode = (0.05, 0.1, 0.05, 0.05)
    
    wedges, texts, autotexts = ax1.pie(sizes, explode=explode, labels=labels, colors=colors,
                                         autopct='%1.1f%%', shadow=True, startangle=90)
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)
    
    ax1.set_title(f'📊 Decomposição Detalhada\nMatriz {test.size}×{test.size}', 
                  fontsize=12, fontweight='bold')
    
    # ============================================================
    # PIZZA 2: Overhead vs Computação
    # ============================================================
    total_overhead = test.total_overhead
    labels2 = [
        f'Total Overhead\n{total_overhead:.6f}s',
        f'Computação Paralela\n{test.time_compute:.6f}s'
    ]
    sizes2 = [total_overhead, test.time_compute]
    colors2 = ['#e74c3c', '#27ae60']
    explode2 = (0.1, 0)
    
    wedges2, texts2, autotexts2 = ax2.pie(sizes2, explode=explode2, labels=labels2, colors=colors2,
                                            autopct='%1.1f%%', shadow=True, startangle=90)
    
    for autotext in autotexts2:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    ax2.set_title(f'🥧 Overhead vs Computação\nMatriz {test.size}×{test.size}', 
                  fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico de pizza salvo em: {output_file}")
    plt.show()


# ============================================================
# EXEMPLO DE USO COM DADOS SIMULADOS
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("GERADOR DE GRÁFICOS DE PERFORMANCE")
    print("=" * 70)
    print()
    
    # Exemplo com dados simulados (substitua pelos seus dados reais)
    tests = []
    
    # Teste 1: Matriz pequena (50×50) - Overhead domina
    test1 = PerformanceData(50, 2)
    test1.t_sequential = 0.000234
    test1.t_distributed = 0.003456
    test1.overhead_split = 0.000012
    test1.overhead_comm = 0.002890
    test1.time_compute = 0.000120
    test1.overhead_reconstruct = 0.000008
    tests.append(test1)
    
    # Teste 2: Matriz média (200×200) - Break-even
    test2 = PerformanceData(200, 2)
    test2.t_sequential = 0.015234
    test2.t_distributed = 0.014567
    test2.overhead_split = 0.000045
    test2.overhead_comm = 0.006234
    test2.time_compute = 0.007890
    test2.overhead_reconstruct = 0.000023
    tests.append(test2)
    
    # Teste 3: Matriz grande (500×500) - Paralelismo compensa
    test3 = PerformanceData(500, 2)
    test3.t_sequential = 0.234567
    test3.t_distributed = 0.134890
    test3.overhead_split = 0.000123
    test3.overhead_comm = 0.015234
    test3.time_compute = 0.118567
    test3.overhead_reconstruct = 0.000067
    tests.append(test3)
    
    # Teste 4: Matriz muito grande (1000×1000) - Paralelismo domina
    test4 = PerformanceData(1000, 2)
    test4.t_sequential = 1.856789
    test4.t_distributed = 1.023456
    test4.overhead_split = 0.000234
    test4.overhead_comm = 0.045678
    test4.time_compute = 0.976543
    test4.overhead_reconstruct = 0.000123
    tests.append(test4)
    
    print("📊 Gerando gráficos comparativos...")
    create_comparison_graphs(tests, "performance_analysis.png")
    
    print("\n🥧 Gerando gráfico de pizza detalhado (último teste)...")
    create_detailed_breakdown_chart(tests[-1], "breakdown_chart.png")
    
    print("\n" + "=" * 70)
    print("✅ GRÁFICOS GERADOS COM SUCESSO!")
    print("=" * 70)
    print("\nArquivos criados:")
    print("  • performance_analysis.png - Comparação completa de todos os testes")
    print("  • breakdown_chart.png - Decomposição detalhada do último teste")
    print()
    print("💡 DICA: Substitua os dados simulados pelos seus dados reais!")
    print()
