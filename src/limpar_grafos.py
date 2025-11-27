#!/usr/bin/env python3
"""
Script para remover arestas duplicadas dos grafos.

Este script:
1. Lê todos os arquivos .graphml da pasta data/grafos/
2. Remove arestas duplicadas (mantém apenas uma aresta entre cada par de nós)
3. Salva os grafos limpos em data/grafos_limpos/ com os mesmos nomes
4. Mantém os grafos originais intactos
"""

import igraph as ig
import os
from pathlib import Path


def limpar_arestas_duplicadas(grafo: ig.Graph) -> ig.Graph:
    """
    Remove arestas duplicadas de um grafo.
    
    Para grafos direcionados, considera duplicadas apenas arestas com mesma
    origem e destino. Para grafos não-direcionados, considera a direção também.
    
    Args:
        grafo: Grafo do igraph
        
    Returns:
        Novo grafo sem arestas duplicadas
    """
    # Cria uma cópia do grafo para não modificar o original
    grafo_limpo = grafo.copy()
    
    # Obtém informações sobre as arestas
    arestas = grafo_limpo.get_edgelist()
    
    # Conjunto para rastrear arestas únicas
    arestas_vistas = set()
    arestas_para_remover = []
    
    # Verifica se o grafo é direcionado
    is_directed = grafo_limpo.is_directed()
    
    for idx, (origem, destino) in enumerate(arestas):
        if is_directed:
            # Para grafos direcionados, (A, B) é diferente de (B, A)
            aresta_tuple = (origem, destino)
        else:
            # Para grafos não-direcionados, (A, B) é igual a (B, A)
            aresta_tuple = tuple(sorted([origem, destino]))
        
        if aresta_tuple in arestas_vistas:
            # Aresta duplicada encontrada
            arestas_para_remover.append(idx)
        else:
            arestas_vistas.add(aresta_tuple)
    
    # Remove arestas duplicadas (em ordem reversa para não afetar índices)
    if arestas_para_remover:
        grafo_limpo.delete_edges(arestas_para_remover)
        print(f"  - Removidas {len(arestas_para_remover)} arestas duplicadas")
    else:
        print(f"  - Nenhuma aresta duplicada encontrada")
    
    return grafo_limpo


def processar_grafos(dir_origem: str, dir_destino: str):
    """
    Processa todos os grafos de uma pasta, removendo arestas duplicadas.
    
    Args:
        dir_origem: Diretório com os grafos originais
        dir_destino: Diretório para salvar os grafos limpos
    """
    # Cria diretório de destino se não existir
    Path(dir_destino).mkdir(parents=True, exist_ok=True)
    
    # Lista todos os arquivos .graphml
    arquivos_graphml = list(Path(dir_origem).glob("*.graphml"))
    
    if not arquivos_graphml:
        print(f"Nenhum arquivo .graphml encontrado em {dir_origem}")
        return
    
    print(f"Encontrados {len(arquivos_graphml)} grafos para processar\n")
    
    # Estatísticas gerais
    total_arestas_originais = 0
    total_arestas_removidas = 0
    
    # Processa cada grafo
    for arquivo in sorted(arquivos_graphml):
        nome_arquivo = arquivo.name
        print(f"Processando: {nome_arquivo}")
        
        try:
            # Carrega o grafo
            grafo_original = ig.read(str(arquivo))
            num_arestas_original = grafo_original.ecount()
            num_vertices = grafo_original.vcount()
            
            print(f"  - Vértices: {num_vertices}")
            print(f"  - Arestas originais: {num_arestas_original}")
            
            # Remove arestas duplicadas
            grafo_limpo = limpar_arestas_duplicadas(grafo_original)
            num_arestas_limpo = grafo_limpo.ecount()
            arestas_removidas = num_arestas_original - num_arestas_limpo
            
            print(f"  - Arestas após limpeza: {num_arestas_limpo}")
            
            # Atualiza estatísticas
            total_arestas_originais += num_arestas_original
            total_arestas_removidas += arestas_removidas
            
            # Salva o grafo limpo
            caminho_destino = Path(dir_destino) / nome_arquivo
            grafo_limpo.write_graphml(str(caminho_destino))
            print(f"  ✓ Salvo em: {caminho_destino}\n")
            
        except Exception as e:
            print(f"  ✗ Erro ao processar {nome_arquivo}: {e}\n")
            continue
    
    # Resumo final
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"Grafos processados: {len(arquivos_graphml)}")
    print(f"Total de arestas originais: {total_arestas_originais}")
    print(f"Total de arestas removidas: {total_arestas_removidas}")
    print(f"Total de arestas finais: {total_arestas_originais - total_arestas_removidas}")
    if total_arestas_originais > 0:
        percentual = (total_arestas_removidas / total_arestas_originais) * 100
        print(f"Percentual de arestas duplicadas: {percentual:.2f}%")
    print("=" * 60)


def main():
    """Função principal do script."""
    # Define diretórios
    dir_base = Path(__file__).parent
    dir_origem = dir_base / "data" / "grafos"
    dir_destino = dir_base / "data" / "grafos_limpos"
    
    print("=" * 60)
    print("LIMPEZA DE ARESTAS DUPLICADAS EM GRAFOS")
    print("=" * 60)
    print(f"Diretório de origem: {dir_origem}")
    print(f"Diretório de destino: {dir_destino}")
    print("=" * 60)
    print()
    
    # Verifica se o diretório de origem existe
    if not dir_origem.exists():
        print(f"ERRO: Diretório de origem não encontrado: {dir_origem}")
        return
    
    # Processa os grafos
    processar_grafos(str(dir_origem), str(dir_destino))
    
    print("\n✓ Processamento concluído!")
    print(f"✓ Grafos limpos salvos em: {dir_destino}")
    print(f"✓ Grafos originais mantidos em: {dir_origem}")


if __name__ == "__main__":
    main()
