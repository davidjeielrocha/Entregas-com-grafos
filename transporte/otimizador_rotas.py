"""Algoritmos de caminho mínimo, árvore geradora mínima e rota que visita todos os pontos."""

import itertools

import networkx as nx


class OtimizadorRotas:
    def __init__(self, grafo):
        """``grafo`` é uma instância de GrafoEntregas."""
        self.grafo = grafo
        self.G = grafo.G

    def menor_caminho(self, origem, destino):
        """Item 3.2 - Dijkstra entre dois vértices. Retorna (rota, custo)."""
        custo, rota = nx.single_source_dijkstra(self.G, origem, destino, weight="weight")
        return rota, custo

    def custos_a_partir_da_sede(self, sede):
        """
        Item 3.3 - três visões complementares do custo entre a sede e os pontos:
          A) menor caminho (Dijkstra) da sede até cada ponto;
          B) todos os caminhos simples (sem repetir vértice) da sede até cada ponto;
          C) Árvore Geradora Mínima (Prim), custo mínimo para interligar a rede.
        Retorna (dijkstra, todos, agm).
        """
        custos, rotas = nx.single_source_dijkstra(self.G, sede, weight="weight")
        dijkstra = [(d, rotas[d], custos[d])
                    for d in sorted(custos, key=custos.get) if d != sede]

        todos = {}
        for destino in self.G.nodes():
            if destino == sede:
                continue
            caminhos = [(c, self.grafo.custo_rota(c))
                        for c in nx.all_simple_paths(self.G, sede, destino)]
            todos[destino] = sorted(caminhos, key=lambda x: x[1])

        agm = nx.minimum_spanning_tree(self.G, weight="weight", algorithm="prim")
        return dijkstra, todos, agm

    def otimizar_rota_completa(self, origem, destino_final=None):
        """
        Itens 3.4 e 3.5 - variação do Problema do Caixeiro Viajante resolvida por
        força bruta (itertools.permutations): a busca exaustiva garante o ótimo global.

        Avalia duas modelagens:
          * estrita : Caminho Hamiltoniano (só arestas diretas, cada ponto uma vez);
          * passeio : entre duas paradas usa o menor caminho (Dijkstra), podendo
                      passar de novo por um ponto se isso reduzir o custo.
        Retorna {'estrita': (rota, custo), 'passeio': (rota, custo), 'avaliadas': n}.
        Se não houver Caminho Hamiltoniano, 'estrita' fica (None, inf).
        """
        dist = dict(nx.all_pairs_dijkstra_path_length(self.G, weight="weight"))
        trajeto = dict(nx.all_pairs_dijkstra_path(self.G, weight="weight"))
        intermediarios = [n for n in self.G.nodes() if n not in (origem, destino_final)]

        melhor_estrita, melhor_passeio = (None, float("inf")), (None, float("inf"))
        avaliadas = 0
        for perm in itertools.permutations(intermediarios):
            avaliadas += 1
            seq = [origem, *perm] + ([destino_final] if destino_final else [])
            pares = list(zip(seq[:-1], seq[1:]))

            if all(self.G.has_edge(u, v) for u, v in pares):
                c = self.grafo.custo_rota(seq)
                if c < melhor_estrita[1]:
                    melhor_estrita = (seq, c)

            c = sum(dist[u][v] for u, v in pares)
            if c < melhor_passeio[1]:
                rota = [seq[0]]
                for u, v in pares:
                    rota += trajeto[u][v][1:]
                melhor_passeio = (rota, c)

        return {"estrita": melhor_estrita, "passeio": melhor_passeio, "avaliadas": avaliadas}
