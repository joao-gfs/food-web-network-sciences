import igraph as ig
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import argparse
from cascading_extinction import ExtincaoEmCascata

import sys

class Logger(object):
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

def configurar_argumentos():
    parser = argparse.ArgumentParser(description='Análise de Rede Trófica e Extinções em Cascata')
    parser.add_argument('--arquivo', type=str, default='data/grafos_limpos/Brasil (SP).graphml',
                        help='Caminho para o arquivo .graphml da rede trófica')
    parser.add_argument('--output', type=str, default='resultados_analise',
                        help='Diretório para salvar os resultados')
    return parser.parse_args()

def carregar_grafo(caminho_arquivo):
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    return ig.Graph.Read_GraphML(caminho_arquivo)

def passo_1_caracterizacao(simulacao, output_dir):
    print("\n--- Passo 1: Caracterização da Rede Trófica ---")
    grafo = simulacao.grafo_original
    
    num_nos = len(grafo.vs)
    num_arestas = len(grafo.es)
    num_basais = len(simulacao.especies_basais)
    
    print(f"Número total de espécies (nós): {num_nos}")
    print(f"Número total de interações (arestas): {num_arestas}")
    print(f"Número de espécies basais (produtores primários): {num_basais}")
    
    # Plotar estado inicial
    print("Gerando visualização da rede completa...")
    os.makedirs(output_dir, exist_ok=True)
    fig, ax, _ = simulacao.plotar_passo(
        passo=None, 
        titulo=f"Rede Trófica - Estado Inicial\nNós: {num_nos}, Arestas: {num_arestas}",
        mostrar_legenda=True
    )
    caminho_fig = os.path.join(output_dir, "1_rede_inicial.png")
    fig.savefig(caminho_fig, bbox_inches='tight', dpi=150)
    plt.close(fig)
    print(f"Figura salva em: {caminho_fig}")

def passo_2_vulnerabilidade(simulacao, output_dir):
    print("\n--- Passo 2: Análise de Vulnerabilidade (Ranking de Impacto) ---")
    print("Calculando ranking de vulnerabilidade (isso pode levar alguns segundos)...")
    
    ranking = simulacao.get_vulnerabilidade_ranking()
    grafo = simulacao.grafo_original
    
    # Calcular métricas de centralidade
    print("Calculando métricas de centralidade...")
    graus_entrada = grafo.indegree()
    graus_saida = grafo.outdegree()
    graus_total = grafo.degree()
    betweenness = grafo.betweenness()
    closeness = grafo.closeness()
    pagerank = grafo.pagerank()
    
    # Criar DataFrame para melhor visualização
    dados_ranking = []
    for nome, total_extincoes in ranking:
        # Encontrar vértice original para pegar métricas
        try:
            v = grafo.vs.find(name=nome)
            idx = v.index
        except:
            continue
            
        dados_ranking.append({
            'Espécie': nome,
            'Extinções Totais': total_extincoes,
            'Extinções Secundárias': total_extincoes - 1,
            'Grau Entrada': graus_entrada[idx],
            'Grau Saída': graus_saida[idx],
            'Grau Total': graus_total[idx],
            'Betweenness': round(betweenness[idx], 2),
            'Closeness': round(closeness[idx], 4),
            'PageRank': round(pagerank[idx], 4)
        })
    
    df_ranking = pd.DataFrame(dados_ranking)
    
    print("\nTop 10 Espécies Mais Críticas:")
    top_10 = df_ranking.head(10)
    # Ajustar exibição do pandas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(top_10.to_string(index=False))
    
    # Salvar tabela completa
    caminho_csv = os.path.join(output_dir, "2_ranking_vulnerabilidade.csv")
    df_ranking.to_csv(caminho_csv, index=False)
    print(f"\nRanking completo salvo em: {caminho_csv}")
    
    # Retorna a espécie mais crítica para o próximo passo
    if not df_ranking.empty:
        return df_ranking.iloc[0]['Espécie']
    return None

def passo_3_cascata(simulacao, especie_alvo, output_dir):
    print("\n--- Passo 3: Dinâmica de Extinção em Cascata (Estudo de Caso) ---")
    
    if especie_alvo is None:
        print("Nenhuma espécie alvo identificada. Pulando passo 3.")
        return

    print(f"Simulando cascata para a espécie Keystone: {especie_alvo}")
    
    dir_cascata = os.path.join(output_dir, "3_cascata_detalhada")
    os.makedirs(dir_cascata, exist_ok=True)
    
    # Usar o método plotar_cascata da classe
    caminhos = simulacao.plotar_cascata(
        especie=especie_alvo,
        salvar_dir=dir_cascata,
        mostrar=False, # Não mostrar interativamente, apenas salvar
        dpi=150,
        mostrar_legenda=True
    )
    
    print(f"Snapshots da cascata salvos em: {dir_cascata}")
    print(f"Total de passos gerados: {len(caminhos)}")

def passo_4_robustez(simulacao, output_dir):
    print("\n--- Passo 4: Análise de Robustez (Curvas de Extinção) ---")
    
    # Configurações
    num_simulacoes_aleatorias = 10
    passos_percentuais = np.linspace(0, 1, 21) # 0%, 5%, ..., 100%
    
    print("Gerando curva de remoção ALEATÓRIA...")
    robustez_aleatoria = []
    
    # Para cada percentual de remoção
    for p in passos_percentuais:
        somas_robustez = 0
        num_remover = int(p * len(simulacao.grafo_original.vs))
        
        if num_remover == 0:
            robustez_aleatoria.append(1.0)
            continue
            
        for _ in range(num_simulacoes_aleatorias):
            simulacao.reset()
            # Escolhe N espécies aleatórias para remover
            todos_indices = list(range(len(simulacao.grafo.vs)))
            # Filtrar basais se quisermos ser justos, mas o enunciado diz "espécies ao acaso"
            # Vamos remover qualquer uma, mas o código protege basais de extinção secundária, não primária.
            # Se removermos uma basal primariamente, ela sai.
            
            alvos = np.random.choice(todos_indices, num_remover, replace=False)
            simulacao.remover_grupo_simultaneo(alvos)
            somas_robustez += simulacao.get_robustez()
            
        robustez_aleatoria.append(somas_robustez / num_simulacoes_aleatorias)
        
    print("Gerando curva de remoção DIRECIONADA (por vulnerabilidade)...")
    # Primeiro precisamos do ranking completo para saber a ordem
    # Garantir que o grafo está resetado antes de calcular ranking
    simulacao.reset()
    ranking = simulacao.get_vulnerabilidade_ranking()
    ordem_remocao = [nome for nome, _ in ranking]
    
    robustez_direcionada = []
    
    for p in passos_percentuais:
        num_remover = int(p * len(simulacao.grafo_original.vs))
        
        if num_remover == 0:
            robustez_direcionada.append(1.0)
            continue
            
        simulacao.reset()
        # Remove as top N espécies
        alvos = ordem_remocao[:num_remover]
        simulacao.remover_grupo_simultaneo(alvos)
        robustez_direcionada.append(simulacao.get_robustez())

    # Plotar gráfico
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(passos_percentuais * 100, robustez_aleatoria, 'o-', label='Remoção Aleatória', color='blue')
    ax.plot(passos_percentuais * 100, robustez_direcionada, 's-', label='Remoção Direcionada', color='red')
    
    ax.set_xlabel('% de Espécies Removidas')
    ax.set_ylabel('Robustez (S/S0)')
    ax.set_title('Análise de Robustez da Rede')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    caminho_fig = os.path.join(output_dir, "4_curvas_robustez.png")
    fig.savefig(caminho_fig, dpi=150)
    plt.close(fig)
    print(f"Gráfico de robustez salvo em: {caminho_fig}")

def passo_5_dieta(simulacao, especie_alvo, output_dir):
    print("\n--- Passo 5: Impacto na Dieta dos Sobreviventes ---")
    
    if especie_alvo is None:
        print("Nenhuma espécie alvo para simular impacto. Pulando passo 5.")
        return

    print(f"Analisando perda de dieta após extinção de: {especie_alvo}")
    
    simulacao.reset()
    simulacao.remove_especie(especie_alvo)
    
    perdas = simulacao.calcular_perda_dieta()
    
    if not perdas:
        print("Nenhuma espécie sobrevivente sofreu perda de dieta (ou rede vazia).")
        return
        
    valores_perda = list(perdas.values())
    
    # Histograma
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(valores_perda, bins=10, range=(0, 1), color='orange', edgecolor='black', alpha=0.7)
    
    ax.set_xlabel('Perda de Dieta (0.0 a 1.0)')
    ax.set_ylabel('Número de Espécies')
    ax.set_title(f'Distribuição da Perda de Dieta\nApós extinção de {especie_alvo}')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    caminho_fig = os.path.join(output_dir, "5_perda_dieta.png")
    fig.savefig(caminho_fig, dpi=150)
    plt.close(fig)
    print(f"Histograma de perda de dieta salvo em: {caminho_fig}")
    
    # Estatísticas
    total_afetados = len([p for p in valores_perda if p > 0])
    criticos = len([p for p in valores_perda if p >= 0.5])
    
    print(f"Total de espécies com alguma perda de dieta: {total_afetados}")
    print(f"Espécies com perda crítica (>= 50%): {criticos}")

def main():
    args = configurar_argumentos()
    
    # Extrair nome do arquivo para criar subdiretório
    nome_arquivo = os.path.splitext(os.path.basename(args.arquivo))[0]
    output_dir = os.path.join(args.output, nome_arquivo)
    
    # Configurar Logger
    os.makedirs(output_dir, exist_ok=True)
    log_file = os.path.join(output_dir, "analise_log.txt")
    sys.stdout = Logger(log_file)
    
    print(f"Iniciando análise para: {args.arquivo}")
    print(f"Resultados serão salvos em: {output_dir}")
    print(f"Log de execução salvo em: {log_file}")
    
    try:
        grafo = carregar_grafo(args.arquivo)
        simulacao = ExtincaoEmCascata(grafo)
        
        passo_1_caracterizacao(simulacao, output_dir)
        keystone_species = passo_2_vulnerabilidade(simulacao, output_dir)
        passo_3_cascata(simulacao, keystone_species, output_dir)
        passo_4_robustez(simulacao, output_dir)
        passo_5_dieta(simulacao, keystone_species, output_dir)
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
