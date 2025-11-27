import igraph as ig
import matplotlib.pyplot as plt
from cascading_extinction import ExtincaoEmCascata
import os

pasta = 'grafos_limpos'

files = os.listdir(f'data/{pasta}')
for file in files:
    print()
    print(30*"-=")
    print(f'{file.replace('.graphml', '')}\n')
    # Carrega o grafo da rede trófica
    g = ig.Graph.Read_GraphML(f'data/{pasta}/{file}')
    print(f"Grafo carregado: {len(g.vs)} espécies, {len(g.es)} interações")

    # Inicializa a simulação
    sim = ExtincaoEmCascata(g)

    print(f"Espécies basais (grau de entrada=0): {len(sim.especies_basais)}")
    result = sim.get_vulnerabilidade_ranking()

    for i, (species, cascade_size) in enumerate(result[:5], 1):
        print(f"{i:2d}. {species:50s} -> {cascade_size:3d} extinções")