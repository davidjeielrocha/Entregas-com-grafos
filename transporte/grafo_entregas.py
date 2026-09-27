"""Modelagem dos pontos de entrega como grafo não direcionado e ponderado G = (V, E, w)."""

import networkx as nx


class GrafoEntregas:
    def __init__(self, arestas):
        self.G = nx.Graph()
        self.G.add_weighted_edges_from(arestas)

    @classmethod
    def de_configuracao(cls, config):
        return cls(config.arestas)

    # ------------------------------------------------------------------ #
    @property
    def vertices(self):
        return list(self.G.nodes())

    @property
    def num_vertices(self):
        return self.G.number_of_nodes()

    @property
    def num_arestas(self):
        return self.G.number_of_edges()

    @property
    def conexo(self):
        return nx.is_connected(self.G)

    def graus(self):
        """Lista (vértice, grau) em ordem decrescente de grau."""
        return sorted(self.G.degree(), key=lambda x: -x[1])

    def peso(self, u, v):
        return self.G[u][v]["weight"]

    def custo_rota(self, rota):
        """Soma os pesos das arestas consecutivas de uma rota (lista de vértices)."""
        return sum(self.peso(u, v) for u, v in zip(rota[:-1], rota[1:]))

    def formatar_rota(self, rota):
        """Ex.: 'Lago Norte -(8)-> Esplanada -(5)-> Asa Sul'."""
        partes = [rota[0]]
        for u, v in zip(rota[:-1], rota[1:]):
            partes.append(f"-({self.peso(u, v)})-> {v}")
        return " ".join(partes)

    def trechos(self, rota):
        """Lista de (origem, destino, peso) de cada trecho de uma rota."""
        return [(u, v, self.peso(u, v)) for u, v in zip(rota[:-1], rota[1:])]
