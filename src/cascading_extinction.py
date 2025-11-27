import igraph as ig
from typing import List, Dict, Set, Tuple
import copy
import matplotlib.pyplot as plt
import os


class ExtincaoEmCascata:
    """
    Simula extinção em cascata em redes ecológicas.
    
    Quando uma espécie é removida, outras espécies que dependem dela podem ser extintas
    se perderem todas as suas fontes de alimento (grau de entrada se torna 0). No entanto,
    espécies que naturalmente começam com grau de entrada=0 (produtores primários, espécies basais)
    não são afetadas por este mecanismo.
    """
    
    def __init__(self, grafo: ig.Graph):
        """
        Inicializa a simulação com um grafo de rede trófica.
        
        Args:
            grafo: Um objeto Graph do igraph representando a rede trófica.
                   As arestas devem apontar da presa para o predador (A -> B significa que B come A).
        """
        self.grafo_original = grafo
        self.grafo = grafo.copy()
        
        # Identifica espécies que naturalmente têm grau de entrada=0 (espécies basais)
        # Estes são produtores primários e nunca devem ser extintos devido à cascata
        # Armazena por nome, já que os índices mudam ao longo da execução
        self.especies_basais = set()
        for v in self.grafo.vs:
            if v.indegree() == 0:
                nome_especie = v['name'] if 'name' in v.attributes() else str(v.index)
                self.especies_basais.add(nome_especie)
        
        # Rastreia histórico de extinções
        self.historico_extincoes = []
        self.passo_atual = 0
        
        # Rastreia estados dos nós para visualização
        # Estados: 'vivo', 'extinto_primario', 'extinto_secundario'
        self.estados_nos = {}
        for v in self.grafo.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            self.estados_nos[nome] = 'vivo'
        
        # Histórico de estados para cada passo
        self.historico_estados = []
    
    def reset(self):
        """Reinicia a simulação para o estado original do grafo."""
        self.grafo = self.grafo_original.copy()
        self.historico_extincoes = []
        self.passo_atual = 0
        
        # Recalcula espécies basais
        self.especies_basais = set()
        for v in self.grafo.vs:
            if v.indegree() == 0:
                nome_especie = v['name'] if 'name' in v.attributes() else str(v.index)
                self.especies_basais.add(nome_especie)
        
        # Reseta estados dos nós
        self.estados_nos = {}
        for v in self.grafo.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            self.estados_nos[nome] = 'vivo'
        
        self.historico_estados = []
    
    def remove_especie(self, identificador_especie) -> Dict:
        """
        Remove uma espécie da rede e simula extinção em cascata.
        
        Args:
            species_identifier: Índice do vértice (int) ou nome da espécie (str).
        
        Returns:
            Um dicionário contendo:
                - 'primary_extinction': nome/índice da espécie inicialmente removida
                - 'secondary_extinctions': lista de espécies extintas devido à cascata
                - 'total_extinctions': número total de extinções (primária + secundárias)
                - 'extinct_species': lista de todas as espécies extintas
                - 'step': número do passo da simulação
        """
        # Encontra o vértice a ser removido
        if isinstance(identificador_especie, str):
            try:
                vertex = self.grafo.vs.find(name=identificador_especie)
            except ValueError:
                raise ValueError(f"Espécie '{identificador_especie}' não encontrada no grafo")
        else:
            if identificador_especie < 0 or identificador_especie >= len(self.grafo.vs):
                raise ValueError(f"Índice de vértice inválido: {identificador_especie}")
            vertex = self.grafo.vs[identificador_especie]
        
        extincao_primaria = vertex['name'] if 'name' in vertex.attributes() else vertex.index
        
        # Identifica vizinhos da espécie a ser removida (nós que perderão arestas)
        vizinhos_afetados = set()
        for neighbor in self.grafo.neighbors(vertex.index, mode='all'):
            nome_vizinho = self.grafo.vs[neighbor]['name'] if 'name' in self.grafo.vs[neighbor].attributes() else str(neighbor)
            vizinhos_afetados.add(nome_vizinho)
        
        # Atualiza estado do nó para extinção primária
        self.estados_nos[extincao_primaria] = 'extinto_primario'
        
        # Remove a espécie primária
        especies_a_remover = [vertex.index]
        extintos_secundarios = []
        
        # Verifica iterativamente extinções em cascata
        while especies_a_remover:
            remocoes_atuais = especies_a_remover.copy()
            especies_a_remover = []  # Reset para a próxima iteração
            
            # Antes de remover, identifica vizinhos que serão afetados
            for idx in remocoes_atuais:
                for neighbor in self.grafo.neighbors(idx, mode='all'):
                    nome_vizinho = self.grafo.vs[neighbor]['name'] if 'name' in self.grafo.vs[neighbor].attributes() else str(neighbor)
                    vizinhos_afetados.add(nome_vizinho)
            
            # Remove todas as espécies do lote atual
            for idx in sorted(remocoes_atuais, reverse=True):
                self.grafo.delete_vertices(idx)
            
            # Verifica novas extinções
            # Após a deleção, os índices dos vértices mudam, então precisamos verificar todos os vértices restantes
            for v in self.grafo.vs:
                # Considera apenas espécies que NÃO são espécies basais
                # Verifica pelo nome, já que os índices mudam ao longo da execução
                nome_especie = v['name'] if 'name' in v.attributes() else str(v.index)
                if nome_especie not in self.especies_basais:
                    # Se o grau de entrada se torna 0, esta espécie é extinta
                    if v.indegree() == 0:
                        extintos_secundarios.append(nome_especie)
                        especies_a_remover.append(v.index)
                        # Atualiza estado do nó para extinção secundária
                        self.estados_nos[nome_especie] = 'extinto_secundario'
        
        # Marca nós afetados (perderam arestas mas não foram extintos)
        for nome in vizinhos_afetados:
            # Só marca como afetado se ainda estiver vivo
            if self.estados_nos.get(nome) == 'vivo':
                self.estados_nos[nome] = 'afetado'
        
        # Salva snapshot dos estados atuais
        self.historico_estados.append(copy.deepcopy(self.estados_nos))
        
        # Registra este evento de extinção
        self.passo_atual += 1
        evento_extincao = {
            'passo': self.passo_atual,
            'extincao_primaria': extincao_primaria,
            'extincoes_secundarias': extintos_secundarios,
            'extincoes_totais': 1 + len(extintos_secundarios),
            'extintos': [extincao_primaria] + extintos_secundarios,
            'restantes': len(self.grafo.vs)
        }
        
        self.historico_extincoes.append(evento_extincao)
        
        return evento_extincao
    
    def simular_sequencia(self, sequencia_especies: List) -> List[Dict]:
        """
        Simula uma sequência de remoções de espécies.
        
        Args:
            sequencia_especies: Lista de identificadores de espécies (nomes ou índices) para remover em ordem.
        
        Returns:
            Lista de dicionários de eventos de extinção, um para cada remoção.
        """
        resultados = []
        for especie in sequencia_especies:
            try:
                resultado = self.remove_especie(especie)
                resultados.append(resultado)
            except ValueError as e:
                # A espécie pode já ter sido removida em uma cascata
                print(f"Warning: {e}")
                continue
        
        return resultados
    
    def remover_grupo_simultaneo(self, lista_especies: List) -> Dict:
        """
        Remove um grupo de espécies simultaneamente (todas como extinção primária).
        
        Args:
            lista_especies: Lista de identificadores de espécies (nomes ou índices).
            
        Returns:
            Dicionário com resumo do evento de extinção em massa.
        """
        # Identifica todos os vértices a serem removidos
        vertices_a_remover = []
        nomes_primarios = []
        
        for identificador in lista_especies:
            if isinstance(identificador, str):
                try:
                    vertex = self.grafo.vs.find(name=identificador)
                    vertices_a_remover.append(vertex)
                    nomes_primarios.append(identificador)
                except ValueError:
                    print(f"Aviso: Espécie '{identificador}' não encontrada ou já removida.")
            else:
                if 0 <= identificador < len(self.grafo.vs):
                    vertex = self.grafo.vs[identificador]
                    vertices_a_remover.append(vertex)
                    nome = vertex['name'] if 'name' in vertex.attributes() else str(vertex.index)
                    nomes_primarios.append(nome)
        
        if not vertices_a_remover:
            return {'erro': 'Nenhuma espécie válida para remover'}
            
        # Identifica vizinhos afetados inicialmente
        vizinhos_afetados = set()
        indices_a_remover = []
        
        for vertex in vertices_a_remover:
            # Marca como extinto primário
            nome = vertex['name'] if 'name' in vertex.attributes() else str(vertex.index)
            self.estados_nos[nome] = 'extinto_primario'
            indices_a_remover.append(vertex.index)
            
            # Vizinhos que perderão conexões
            for neighbor in self.grafo.neighbors(vertex.index, mode='all'):
                nome_vizinho = self.grafo.vs[neighbor]['name'] if 'name' in self.grafo.vs[neighbor].attributes() else str(neighbor)
                vizinhos_afetados.add(nome_vizinho)
        
        # Remove todas as espécies primárias de uma vez
        # Importante: remover do maior índice para o menor para não invalidar índices
        for idx in sorted(indices_a_remover, reverse=True):
            self.grafo.delete_vertices(idx)
            
        # Inicia verificação de cascata (similar ao remove_especie, mas já começou com grupo)
        extintos_secundarios = []
        especies_a_remover = [] # Para a próxima rodada (secundários)
        
        # Primeira verificação pós-remoção em massa
        for v in self.grafo.vs:
            nome_especie = v['name'] if 'name' in v.attributes() else str(v.index)
            if nome_especie not in self.especies_basais:
                if v.indegree() == 0:
                    extintos_secundarios.append(nome_especie)
                    especies_a_remover.append(v.index)
                    self.estados_nos[nome_especie] = 'extinto_secundario'
        
        # Loop de cascata padrão
        while especies_a_remover:
            remocoes_atuais = especies_a_remover.copy()
            especies_a_remover = []
            
            for idx in remocoes_atuais:
                for neighbor in self.grafo.neighbors(idx, mode='all'):
                    nome_vizinho = self.grafo.vs[neighbor]['name'] if 'name' in self.grafo.vs[neighbor].attributes() else str(neighbor)
                    vizinhos_afetados.add(nome_vizinho)
            
            for idx in sorted(remocoes_atuais, reverse=True):
                self.grafo.delete_vertices(idx)
            
            for v in self.grafo.vs:
                nome_especie = v['name'] if 'name' in v.attributes() else str(v.index)
                if nome_especie not in self.especies_basais and self.estados_nos.get(nome_especie) == 'vivo':
                    if v.indegree() == 0:
                        extintos_secundarios.append(nome_especie)
                        especies_a_remover.append(v.index)
                        self.estados_nos[nome_especie] = 'extinto_secundario'

        # Marca afetados
        for nome in vizinhos_afetados:
            if self.estados_nos.get(nome) == 'vivo':
                self.estados_nos[nome] = 'afetado'
        
        self.historico_estados.append(copy.deepcopy(self.estados_nos))
        self.passo_atual += 1
        
        evento_extincao = {
            'passo': self.passo_atual,
            'extincao_primaria': nomes_primarios, # Lista agora
            'extincoes_secundarias': extintos_secundarios,
            'extincoes_totais': len(nomes_primarios) + len(extintos_secundarios),
            'extintos': nomes_primarios + extintos_secundarios,
            'restantes': len(self.grafo.vs)
        }
        
        self.historico_extincoes.append(evento_extincao)
        return evento_extincao

    def calcular_perda_dieta(self) -> Dict[str, float]:
        """
        Calcula a porcentagem de perda de dieta para as espécies sobreviventes.
        
        Returns:
            Dicionário {nome_especie: porcentagem_perda} (0.0 a 1.0).
            Apenas para espécies vivas que não são basais.
        """
        perdas = {}
        
        # Cria mapa de graus originais para acesso rápido
        graus_originais = {}
        for v in self.grafo_original.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            graus_originais[nome] = v.indegree()
            
        # Calcula perda para os sobreviventes
        for v in self.grafo.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            
            # Ignora basais (não comem ninguém)
            if nome in self.especies_basais:
                continue
                
            grau_atual = v.indegree()
            grau_original = graus_originais.get(nome, 0)
            
            if grau_original > 0:
                perda = 1.0 - (grau_atual / grau_original)
                perdas[nome] = round(perda, 3)
            else:
                perdas[nome] = 0.0
                
        return perdas
    
    def get_robustez(self) -> float:
        """
        Calcula a robustez da rede como a fração de espécies restantes.
        
        Returns:
            Float entre 0 e 1, onde 1 significa que nenhuma extinção ocorreu.
        """
        tamanho_original = len(self.grafo_original.vs)
        tamanho_atual = len(self.grafo.vs)
        return tamanho_atual / tamanho_original if tamanho_original > 0 else 0.0
    
    def get_resumo(self) -> Dict:
        """
        Obtém um resumo do estado da simulação.
        
        Returns:
            Dicionário com estatísticas da simulação.
        """
        total_primaria = len(self.historico_extincoes)
        total_secundaria = sum(len(event['secondary_extinctions']) 
                            for event in self.historico_extincoes)
        
        return {
            'total_steps': self.passo_atual,
            'total_primary_extinctions': total_primaria,
            'total_secondary_extinctions': total_secundaria,
            'total_extinctions': total_primaria + total_secundaria,
            'original_species_count': len(self.grafo_original.vs),
            'remaining_species_count': len(self.grafo.vs),
            'robustness': self.get_robustez(),
            'basal_species_count': len(self.especies_basais),
            'extinction_history': self.historico_extincoes
        }
    
    def get_vulnerabilidade_ranking(self) -> List[Tuple[str, int]]:
        """
        Classifica espécies por seu potencial de causar extinções em cascata.
        Usa uma abordagem de simulação em cópias do grafo.
        
        Returns:
            Lista de tuplas (nome_espécie, tamanho_cascata) ordenada por tamanho de cascata (decrescente).
        """
        pontuacoes_vulnerabilidade = []
        
        for v in self.grafo.vs:
            # Cria uma simulação temporária
            sim_temp = ExtincaoEmCascata(self.grafo)
            resultado = sim_temp.remove_especie(v.index)
            
            nome_especie = v['name'] if 'name' in v.attributes() else v.index
            tamanho_cascata = resultado['extincoes_totais']
            
            pontuacoes_vulnerabilidade.append((nome_especie, tamanho_cascata))
        
        # Ordena por tamanho de cascata (decrescente)
        pontuacoes_vulnerabilidade.sort(key=lambda x: x[1], reverse=True)
        
        return pontuacoes_vulnerabilidade
    
    def plotar_passo(self, passo: int = None, estados: Dict = None, titulo: str = None, 
                     layout=None, ax=None, mostrar_legenda: bool = True):
        """
        Plota o grafo em um passo específico da cascata.
        
        Args:
            passo: Número do passo a visualizar (None = estado atual)
            estados: Dicionário de estados customizado (sobrescreve passo)
            titulo: Título do gráfico
            layout: Layout do grafo (None = calcula automaticamente)
            ax: Eixo matplotlib para plotar (None = cria novo)
            mostrar_legenda: Se True, mostra legenda com cores
        
        Returns:
            Tupla (fig, ax, layout) para reutilização
        """
        # Determina quais estados usar
        if estados is not None:
            estados_plot = estados
        elif passo is not None and 0 <= passo < len(self.historico_estados):
            estados_plot = self.historico_estados[passo]
        else:
            estados_plot = self.estados_nos
        
        # Cria figura se necessário
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 10))
        else:
            fig = ax.figure
        
        # Calcula layout se não fornecido
        if layout is None:
            layout = self.grafo_original.layout(ig.Graph.layout_sugiyama)         
        # Define cores para cada estado
        cores_estados = {
            'vivo': '#2ecc71',           # Verde
            'extinto_primario': '#e74c3c',  # Vermelho
            'extinto_secundario': "#f36412", # Laranja
            'afetado': '#9b59b6',        # Roxo
        }
        
        # Mapeia cores e labels para cada vértice
        cores_vertices = []
        tamanhos_vertices = []
        labels_vertices = []

        indices_fundo = []   # Vivos
        indices_frente = []  # Extintos
        for v in self.grafo_original.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            estado = estados_plot.get(nome, 'vivo')
            
            # Lógica de Cores (igual ao original)
            if estado == 'vivo' and nome in self.especies_basais:
                cores_vertices.append('#3498db') 
            else:
                cores_vertices.append(cores_estados.get(estado, '#95a5a6'))

            if estado == 'vivo':
                tamanhos_vertices.append(15)
                indices_fundo.append(v.index)
                labels_vertices.append('')  # Sem label para nós vivos
            else:
                tamanhos_vertices.append(13)
                indices_frente.append(v.index)
                # Mostra o índice do nó para nós não-vivos
                labels_vertices.append(str(v.index))
        
        ordem_desenho = indices_fundo + indices_frente
        
        # Identifica arestas removidas (conectadas a nós extintos)
        cores_arestas = []
        larguras_arestas = []
        nos_extintos = set()
        
        for v in self.grafo_original.vs:
            nome = v['name'] if 'name' in v.attributes() else str(v.index)
            estado = estados_plot.get(nome, 'vivo')
            if estado in ['extinto_primario', 'extinto_secundario']:
                nos_extintos.add(v.index)
        
        for edge in self.grafo_original.es:
            # Se qualquer extremidade da aresta está extinta, a aresta é removida
            if edge.source in nos_extintos or edge.target in nos_extintos:
                cores_arestas.append('#e74c3c')  # Vermelho para arestas removidas
                larguras_arestas.append(1.0)
            else:
                cores_arestas.append('#b8c6c7')  # Cinza para arestas normais
                larguras_arestas.append(0.5)
        
        # Plota o grafo
        ig.plot(
            self.grafo_original,
            target=ax,
            layout=layout,
            vertex_color=cores_vertices,
            vertex_size=tamanhos_vertices,
            vertex_label=labels_vertices,
            vertex_label_size=7,
            vertex_frame_width=0.5,
            vertex_frame_color='white',
            vertex_order=ordem_desenho,
            edge_width=larguras_arestas,
            edge_color=cores_arestas,
            edge_arrow_size=1,
            edge_arrow_width=1,
        )
        
        # Configura título
        if titulo:
            ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
        elif passo is not None:
            ax.set_title(f'Passo {passo + 1}', fontsize=14, fontweight='bold', pad=20)
        
        # Adiciona legenda
        if mostrar_legenda:
            from matplotlib.patches import Patch
            from matplotlib.lines import Line2D
            elementos_legenda = [
                Patch(facecolor='#2ecc71', label='Vivo'),
                Patch(facecolor='#3498db', label='Basal (vivo)'),
                Patch(facecolor='#9b59b6', label='Afetado (perdeu arestas)'),
                Patch(facecolor='#e74c3c', label='Extinção primária'),
                Patch(facecolor='#f39c12', label='Extinção secundária'),
                Line2D([0], [0], color='#e74c3c', linewidth=2, label='Aresta removida'),
                Line2D([0], [0], color='#b8c6c7', linewidth=1, label='Aresta ativa'),
            ]
            ax.legend(handles=elementos_legenda, loc='upper right', 
                     framealpha=0.9, fontsize=10)
        
        ax.axis('off')
        
        return fig, ax, layout
    
    def plotar_cascata(self, especie: str, salvar_dir: str = None, 
                       mostrar: bool = True, dpi: int = 150, mostrar_legenda: bool = False):
        """
        Plota toda a sequência de uma cascata de extinção.
        
        Args:
            especie: Nome da espécie a remover
            salvar_dir: Diretório para salvar imagens (None = não salva)
            mostrar: Se True, mostra os gráficos
            dpi: Resolução das imagens salvas
            mostrar_legenda: Se True, mostra legenda com cores
        
        Returns:
            Lista de caminhos das imagens salvas (se salvar_dir fornecido)
        """
        # Salva estado atual
        estado_anterior = {
            'grafo': self.grafo.copy(),
            'estados': copy.deepcopy(self.estados_nos),
            'historico_estados': copy.deepcopy(self.historico_estados),
            'historico_extincoes': copy.deepcopy(self.historico_extincoes),
            'passo_atual': self.passo_atual
        }
        
        # Reseta e executa a cascata
        self.reset()
        resultado = self.remove_especie(especie)
        
        # Calcula layout uma vez para consistência
        layout = self.grafo_original.layout(ig.Graph.layout_sugiyama)
        
        # Plota estado inicial
        num_passos = len(self.historico_estados)
        caminhos_salvos = []
        
        # Estado inicial (antes da extinção)
        fig, ax, _ = self.plotar_passo(
            estados={nome: 'vivo' for nome in self.estados_nos.keys()},
            titulo=f'Estado Inicial - Removendo: {especie}',
            layout=layout,
            mostrar_legenda=mostrar_legenda,
        )
        
        if salvar_dir:
            os.makedirs(salvar_dir, exist_ok=True)
            caminho = os.path.join(salvar_dir, f'passo_00_inicial.png')
            fig.savefig(caminho, dpi=dpi, bbox_inches='tight')
            caminhos_salvos.append(caminho)
        
        if mostrar:
            plt.show()
        else:
            plt.close(fig)
        
        # Plota cada passo da cascata
        for i in range(num_passos):
            fig, ax, _ = self.plotar_passo(
                passo=i,
                titulo=f'Passo {i + 1} - {resultado["extincoes_totais"]} extinções totais',
                layout=layout,
                mostrar_legenda=mostrar_legenda,
            )
            
            if salvar_dir:
                caminho = os.path.join(salvar_dir, f'passo_{i+1:02d}.png')
                fig.savefig(caminho, dpi=dpi, bbox_inches='tight')
                caminhos_salvos.append(caminho)
            
            if mostrar:
                plt.show()
            else:
                plt.close(fig)
        
        # Restaura estado anterior
        self.grafo = estado_anterior['grafo']
        self.estados_nos = estado_anterior['estados']
        self.historico_estados = estado_anterior['historico_estados']
        self.historico_extincoes = estado_anterior['historico_extincoes']
        self.passo_atual = estado_anterior['passo_atual']
        
        return caminhos_salvos if salvar_dir else None
    
    def plotar_comparacao(self, especies: List[str], salvar_path: str = None, 
                         dpi: int = 150):
        """
        Plota comparação lado a lado de múltiplas cascatas.
        
        Args:
            especies: Lista de nomes de espécies para comparar
            salvar_path: Caminho para salvar imagem (None = não salva)
            dpi: Resolução da imagem salva
        """
        num_especies = len(especies)
        fig, axes = plt.subplots(1, num_especies, figsize=(6 * num_especies, 6))
        
        if num_especies == 1:
            axes = [axes]
        
        # Layout consistente
        layout = self.grafo_original.layout(ig.Graph.layout_sugiyama)
        
        # Salva estado
        estado_original = {
            'grafo': self.grafo.copy(),
            'estados': copy.deepcopy(self.estados_nos),
            'historico_estados': copy.deepcopy(self.historico_estados),
            'historico_extincoes': copy.deepcopy(self.historico_extincoes),
            'passo_atual': self.passo_atual
        }
        
        for i, especie in enumerate(especies):
            self.reset()
            resultado = self.remove_especie(especie)
            
            # Plota estado final
            self.plotar_passo(
                estados=self.estados_nos,
                titulo=f'{especie}\n{resultado["extincoes_totais"]} extinções',
                layout=layout,
                ax=axes[i],
                mostrar_legenda=(i == num_especies - 1)
            )
        
        # Restaura estado
        self.grafo = estado_original['grafo']
        self.estados_nos = estado_original['estados']
        self.historico_estados = estado_original['historico_estados']
        self.historico_extincoes = estado_original['historico_extincoes']
        self.passo_atual = estado_original['passo_atual']
        
        plt.tight_layout()
        
        if salvar_path:
            fig.savefig(salvar_path, dpi=dpi, bbox_inches='tight')
        
        plt.show()
        
        return fig
