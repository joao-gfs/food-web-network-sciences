"""
Teste rápido para verificar a funcionalidade de nós afetados (cor roxa).
"""

import igraph as ig
from cascading_extinction import ExtincaoEmCascata
import matplotlib.pyplot as plt

# Carrega grafo
print("Carregando grafo...")
g = ig.Graph.Read_GraphML('data/grafos/Switzerland, Lake Neuchatel.graphml')
print(f"Grafo: {len(g.vs)} espécies, {len(g.es)} interações")

# Inicializa simulação
sim = ExtincaoEmCascata(g)
print(f"Espécies basais: {len(sim.especies_basais)}")

# Encontra uma espécie para testar
ranking = sim.get_vulnerabilidade_ranking()
print(f"\nTop 3 espécies mais impactantes:")
for i, (especie, tamanho) in enumerate(ranking[:3], 1):
    print(f"  {i}. {especie}: {tamanho} extinções")

# Testa com a espécie mais impactante
if ranking[0][1] > 1:
    especie_teste = ranking[0][0]
    print(f"\nTestando com: {especie_teste}")
    
    # Remove espécie
    resultado = sim.remove_especie(especie_teste)
    
    # Conta estados
    contagem_estados = {}
    for nome, estado in sim.estados_nos.items():
        contagem_estados[estado] = contagem_estados.get(estado, 0) + 1
    
    print(f"\nResultados:")
    print(f"  Extinções totais: {resultado['extincoes_totais']}")
    print(f"\nContagem de estados:")
    for estado, count in sorted(contagem_estados.items()):
        print(f"  {estado}: {count}")
    
    # Plota
    print(f"\nGerando visualização...")
    fig, ax, layout = sim.plotar_passo(
        titulo=f'Teste - {especie_teste} removido',
        mostrar_legenda=True
    )
    
    fig.savefig('teste_nos_afetados.png', dpi=150, bbox_inches='tight')
    print(f"Imagem salva: teste_nos_afetados.png")
    
    # Verifica se há nós afetados
    if 'afetado' in contagem_estados:
        print(f"\n✓ Sucesso! {contagem_estados['afetado']} nós afetados (roxos) detectados!")
    else:
        print(f"\n⚠ Aviso: Nenhum nó afetado detectado.")
else:
    print("\nNenhuma cascata significativa encontrada para testar.")

plt.close('all')
print("\n✓ Teste concluído!")
