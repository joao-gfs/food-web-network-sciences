"""
Script simplificado para visualizar a cascata de extinção da espécie #1 do ranking.

Este script plota apenas a cascata da espécie mais impactante, sem comparações.
"""

import igraph as ig
from cascading_extinction import ExtincaoEmCascata
import os
import matplotlib.pyplot as plt

# Diretório para salvar visualizações
OUTPUT_DIR = 'visualizacoes_cascatas'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carrega o grafo
print("Carregando grafo...")
grafo_file = 'Florida Key islands, Florida Bay, USA.graphml'
g = ig.Graph.Read_GraphML(f'data/grafos_limpos/{grafo_file}')
nome_rede = grafo_file.replace('.graphml', '')

print(f"Grafo carregado: {nome_rede}")
print(f"  - {len(g.vs)} espécies")
print(f"  - {len(g.es)} interações")

# Inicializa a simulação
sim = ExtincaoEmCascata(g)
print(f"  - {len(sim.especies_basais)} espécies basais")

# Encontra a espécie #1 do ranking
print("\nAnalisando vulnerabilidade das espécies...")
ranking = sim.get_vulnerabilidade_ranking()

# Mostra a espécie #1
especie_top1 = ranking[0][0]
tamanho_cascata = ranking[0][1]
print(f"\nEspécie #1 do ranking: {especie_top1}")
print(f"  - Causa {tamanho_cascata} extinções")

# Visualiza apenas a cascata da espécie #1
if tamanho_cascata > 1:  # Se houver cascata
    print(f"\n{'='*60}")
    print(f"Visualizando cascata para: {especie_top1}")
    print(f"{'='*60}")
    
    # Cria diretório para esta cascata
    cascata_dir = os.path.join(OUTPUT_DIR, f'{nome_rede}_{especie_top1}')
    
    # Plota a cascata completa (salva imagens)
    print(f"\nGerando visualizações da cascata...")
    caminhos = sim.plotar_cascata(
        especie=especie_top1,
        salvar_dir=cascata_dir,
        mostrar=False,
        dpi=150
    )
    
    print(f"\nImagens salvas em: {cascata_dir}/")
    print(f"Total de imagens: {len(caminhos)}")
    for caminho in caminhos:
        print(f"  - {os.path.basename(caminho)}")
else:
    print(f"\nA espécie #{especie_top1} não causa cascata significativa.")

# Fecha todas as figuras
plt.close('all')

print(f"\n{'='*60}")
print("Visualização concluída!")
print(f"Imagens salvas em: {OUTPUT_DIR}/")
print(f"{'='*60}")
print("\n✓ Script concluído com sucesso!")
