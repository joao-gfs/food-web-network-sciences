import igraph as ig
from cascading_extinction import ExtincaoEmCascata
import os
import random
import glob

def test_simultaneous_extinction(seed=42, qtd_para_remover=2): 
    random.seed(seed)
    
    print(f"=== Testando Extinção Simultânea e Perda de Dieta (Seed: {seed}) ===")
    
    grafo_file = 'Brasil (SP).graphml'
    path = f'data/grafos_limpos/{grafo_file}'
    
    if not os.path.exists(path):
        print(f"Erro: Arquivo {path} não encontrado.")
        files = glob.glob('data/grafos_limpos/*.graphml')
        if files:
            path = files[0]
            print(f"Usando alternativo: {path}")
        else:
            print("Nenhum grafo encontrado para teste.")
            return

    g = ig.Graph.Read_GraphML(path)
    sim = ExtincaoEmCascata(g)
    
    print(f"Grafo carregado: {len(g.vs)} espécies, {len(g.es)} conexões.")
    
    pool_candidatos = []
    for v in g.vs:
        nome = v['name'] if 'name' in v.attributes() else str(v.index)
        if nome not in sim.especies_basais:
            pool_candidatos.append(nome) 
    
    if len(pool_candidatos) < qtd_para_remover:
        print("Grafo muito pequeno ou poucas espécies não-basais para o teste.")
        grupo_alvo = pool_candidatos
    else:
        grupo_alvo = random.sample(pool_candidatos, qtd_para_remover)
        
    print(f"\nGrupo sorteado para remoção: {grupo_alvo}")
    
    resultado = sim.remover_grupo_simultaneo(grupo_alvo)
    
    print("\nResultado da Extinção:")
    print(f"  - Primárias: {resultado['extincao_primaria']}")
    print(f"  - Secundárias: {resultado['extincoes_secundarias']}")
    print(f"  - Total: {resultado['extincoes_totais']}")
    
    print("\nCalculando Perda de Dieta para sobreviventes...")
    perdas = sim.calcular_perda_dieta()
    
    perdas_significativas = {k: v for k, v in perdas.items() if v > 0}
    sorted_perdas = sorted(perdas_significativas.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Espécies com perda de dieta ({len(perdas_significativas)} afetadas):")
    for especie, perda in sorted_perdas[:5]:
        print(f"  - {especie}: {perda*100:.1f}% de perda")
        
    if not perdas_significativas:
        print("  - Nenhuma perda de dieta parcial detectada.")

if __name__ == "__main__":
    test_simultaneous_extinction(seed=10, qtd_para_remover=2)