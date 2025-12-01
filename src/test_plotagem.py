#!/usr/bin/env python
"""
Script de teste para verificar se todos os passos da cascata estão sendo plotados.
"""

import igraph as ig
import os
import sys
from cascading_extinction import ExtincaoEmCascata

def testar_plotagem_completa():
    """Testa se todos os passos da cascata são plotados corretamente."""
    
    # Carregar um grafo de teste
    caminho_grafo = 'data/grafos_limpos/Brasil (SP).graphml'
    
    if not os.path.exists(caminho_grafo):
        print(f"Erro: Arquivo não encontrado: {caminho_grafo}")
        print("Tentando usar arquivo alternativo...")
        # Listar arquivos disponíveis
        if os.path.exists('data/grafos_limpos'):
            arquivos = [f for f in os.listdir('data/grafos_limpos') if f.endswith('.graphml')]
            if arquivos:
                caminho_grafo = os.path.join('data/grafos_limpos', arquivos[0])
                print(f"Usando: {caminho_grafo}")
            else:
                print("Nenhum arquivo .graphml encontrado!")
                return
        else:
            print("Diretório data/grafos_limpos não encontrado!")
            return
    
    print(f"Carregando grafo: {caminho_grafo}")
    grafo = ig.Graph.Read_GraphML(caminho_grafo)
    
    # Criar simulação
    sim = ExtincaoEmCascata(grafo)
    
    print(f"\nGrafo original:")
    print(f"  - Nós: {len(sim.grafo_original.vs)}")
    print(f"  - Arestas: {len(sim.grafo_original.es)}")
    print(f"  - Espécies basais: {len(sim.especies_basais)}")
    
    # Encontrar espécie mais crítica
    print("\nCalculando ranking de vulnerabilidade...")
    ranking = sim.get_vulnerabilidade_ranking()
    especie_critica = ranking[0][0]
    extincoes_esperadas = ranking[0][1]
    
    print(f"Espécie mais crítica: {especie_critica}")
    print(f"Extinções totais esperadas: {extincoes_esperadas}")
    
    # Resetar e simular
    sim.reset()
    print(f"\nSimulando cascata para: {especie_critica}")
    resultado = sim.remove_especie(especie_critica)
    
    print(f"\nResultado da simulação:")
    print(f"  - Extinção primária: {resultado['extincao_primaria']}")
    print(f"  - Extinções secundárias: {len(resultado['extincoes_secundarias'])}")
    print(f"  - Total de extinções: {resultado['extincoes_totais']}")
    print(f"  - Espécies restantes: {resultado['restantes']}")
    
    # Verificar histórico de estados
    print(f"\nHistórico de estados:")
    print(f"  - Número de passos no histórico: {len(sim.historico_estados)}")
    print(f"  - Número de eventos no histórico de extinções: {len(sim.historico_extincoes)}")
    
    # Informações detalhadas sobre cada passo do histórico
    for i, estados in enumerate(sim.historico_estados):
        vivos = sum(1 for e in estados.values() if e == 'vivo')
        afetados = sum(1 for e in estados.values() if e == 'afetado')
        extintos_prim = sum(1 for e in estados.values() if e == 'extinto_primario')
        extintos_sec = sum(1 for e in estados.values() if e == 'extinto_secundario')
        print(f"  Passo {i}: {vivos} vivos, {afetados} afetados, {extintos_prim} ext.prim, {extintos_sec} ext.sec")
    
    # Plotar cascata
    output_dir = 'test_plotagem_cascata'
    print(f"\nGerando plots em: {output_dir}")
    
    sim.reset()
    caminhos = sim.plotar_cascata(
        especie=especie_critica,
        salvar_dir=output_dir,
        mostrar=False,
        dpi=150,
        mostrar_legenda=True
    )
    
    print(f"\nImagens geradas:")
    if caminhos:
        for i, caminho in enumerate(caminhos):
            print(f"  {i}: {caminho}")
        print(f"\nTotal de imagens: {len(caminhos)}")
        print(f"Esperado: 1 (inicial) + {len(sim.historico_estados)} (passos) = {1 + len(sim.historico_estados)}")
        
        if len(caminhos) == 1 + len(sim.historico_estados):
            print("\n✓ SUCESSO: Número correto de imagens geradas!")
        else:
            print("\n✗ ERRO: Número incorreto de imagens!")
    else:
        print("Nenhum caminho retornado (salvar_dir pode não estar configurado)")
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    testar_plotagem_completa()
