import igraph as ig
from cascading_extinction import ExtincaoEmCascata
import os

def test_simultaneous_extinction():
    print("=== Testando Extinção Simultânea e Perda de Dieta ===")
    
    # Setup: Carregar grafo
    grafo_file = 'Florida Key islands, Florida Bay, USA.graphml'
    path = f'data/grafos_limpos/{grafo_file}'
    
    if not os.path.exists(path):
        print(f"Erro: Arquivo {path} não encontrado.")
        # Tenta encontrar qualquer arquivo graphml no diretório
        import glob
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
    
    # 1. Identificar 3 espécies para remover (que não sejam basais)
    candidatos = []
    for v in g.vs:
        nome = v['name'] if 'name' in v.attributes() else str(v.index)
        if nome not in sim.especies_basais:
            candidatos.append(nome)
            if len(candidatos) >= 3:
                break
    
    if len(candidatos) < 2:
        print("Grafo muito pequeno para teste de grupo.")
        return
        
    grupo_alvo = candidatos[:2]
    print(f"\nRemovendo grupo simultaneamente: {grupo_alvo}")
    
    # 2. Executar remoção simultânea
    resultado = sim.remover_grupo_simultaneo(grupo_alvo)
    
    print("\nResultado da Extinção:")
    print(f"  - Primárias: {resultado['extincao_primaria']}")
    print(f"  - Secundárias: {resultado['extincoes_secundarias']}")
    print(f"  - Total: {resultado['extincoes_totais']}")
    
    # 3. Calcular Perda de Dieta
    print("\nCalculando Perda de Dieta para sobreviventes...")
    perdas = sim.calcular_perda_dieta()
    
    # Mostra top 5 maiores perdas (que não são 0)
    perdas_significativas = {k: v for k, v in perdas.items() if v > 0}
    sorted_perdas = sorted(perdas_significativas.items(), key=lambda x: x[1], reverse=True)
    
    print(f"Espécies com perda de dieta ({len(perdas_significativas)} afetadas):")
    for especie, perda in sorted_perdas[:5]:
        print(f"  - {especie}: {perda*100:.1f}% de perda")
        
    if not perdas_significativas:
        print("  - Nenhuma perda de dieta parcial detectada (ou tudo morreu ou nada foi afetado parcialmente).")

if __name__ == "__main__":
    test_simultaneous_extinction()
