import igraph as ig
import matplotlib.pyplot as plt
from cascading_extinction import ExtincaoEmCascata
import os

pasta = 'grafos_limpos'

files = os.listdir(f'data/{pasta}')
for file in files:
    print()
    print(30*"-=")
    print(f'{file.replace(".graphml", "")}\n')
    
    # Carrega o grafo da rede trófica
    g = ig.Graph.Read_GraphML(f'data/{pasta}/{file}')
    print(f"Grafo carregado: {len(g.vs)} espécies, {len(g.es)} interações")

    # Inicializa a simulação
    sim = ExtincaoEmCascata(g)

    print(f"Espécies basais (grau de entrada=0): {len(sim.especies_basais)}")
    
    robustez_inicial = sim.get_robustez()
    print(f"Robustez Inicial: {robustez_inicial:.4f}")

    result = sim.get_vulnerabilidade_ranking()
    
    total_especies = len(g.vs)
    
    # --- NOVO BLOCO DE CÓDIGO ---
    # Extrai apenas os números (tamanhos das cascatas) da lista de tuplas
    todos_tamanhos = [tamanho for _, tamanho in result]
    total_casos = len(todos_tamanhos)

    # Conta quantas vezes ocorreu apenas 1 extinção (sem efeitos secundários)
    qtd_apenas_1 = todos_tamanhos.count(1)
    
    # Conta quantas vezes ocorreram entre 1 e 5 extinções
    qtd_2_a_5 = sum(1 for t in todos_tamanhos if 2 <= t <= 5)
    qtd_6_a_10 = sum(1 for t in todos_tamanhos if 6 <= t <= 10)
    qtd_maior_10 = sum(1 for t in todos_tamanhos if t > 10)

    # Calcula as porcentagens
    pct_apenas_1 = (qtd_apenas_1 / total_casos) * 100
    pct_2_a_5 = (qtd_2_a_5 / total_casos) * 100
    pct_6_a_10 = (qtd_6_a_10 / total_casos) * 100
    pct_maior_10 = (qtd_maior_10 / total_casos) * 100
    # ----------------------------

    # Loop original de impressão (opcional: pode limitar para não poluir se o grafo for grande)
    for i, (especie, tamanho_cascata) in enumerate(result):
        robustez_final = (total_especies - tamanho_cascata) / total_especies
        print(f"{i:2d}. {especie:50s} -> {tamanho_cascata:3d} extinções | Robustez Final: {robustez_final:.4f}")
    
    # Prints estatísticos solicitados
    print("\n" + "-"*20)
    print("Resumo estatístico de danos:")
    print(f"Em {pct_apenas_1:.2f}% dos casos houve apenas uma espécie extinta.")
    print(f"Em {pct_2_a_5:.2f}% dos casos houve 1-5 espécies extintas.")
    print(f"Em {pct_6_a_10:.2f}% dos casos houve 6-10 espécies extintas.")
    print(f"Em {pct_maior_10:.2f}% dos casos houve mais de 10 espécies extintas.")
    print("-" * 20)