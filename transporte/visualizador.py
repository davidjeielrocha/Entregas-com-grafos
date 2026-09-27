"""Desenho do grafo (vértices, arestas, pesos e rotas destacadas) com matplotlib."""

import base64
import io
import os

import networkx as nx
from matplotlib.figure import Figure  # sem pyplot: seguro para uso no servidor web

# Paletas das imagens: "claro" reproduz as figuras do relatório; "escuro" acompanha o modo noturno da web
TEMAS = {
    "claro": {
        "fundo": "#FFFFFF", "texto": "#000000", "subtitulo": "#333333",
        "aresta": "#5B84B1", "destaque": "#D9534F", "no": "#FFFFFF", "borda_no": "#000000",
        "inicio": "#C8E6C9", "fim": "#FFCDD2", "peso": "#2B4C7E", "fundo_peso": "#FFFFFF",
    },
    "escuro": {
        "fundo": "#161B22", "texto": "#E6EDF3", "subtitulo": "#9DA7B3",
        "aresta": "#6E8FBF", "destaque": "#E5635F", "no": "#1F2833", "borda_no": "#9DA7B3",
        "inicio": "#23512C", "fim": "#6B2A2A", "peso": "#9CC2F0", "fundo_peso": "#161B22",
    },
}


class VisualizadorGrafo:
    def __init__(self, grafo, posicoes=None):
        """
        ``grafo`` é um GrafoEntregas. ``posicoes`` mapeia vértice -> (x, y);
        vértices sem posição recebem uma posição automática (spring layout).
        """
        self.grafo = grafo
        self.G = grafo.G
        self.posicoes = self._completar_posicoes(posicoes or {})

    def _completar_posicoes(self, posicoes):
        pos = {n: tuple(p) for n, p in posicoes.items() if n in self.G}
        if len(pos) < self.G.number_of_nodes():
            pos = nx.spring_layout(self.G, pos=pos or None, fixed=list(pos) or None,
                                   weight=None, seed=42)
        return pos

    # ------------------------------------------------------------------ #
    def desenhar(self, titulo, rota=None, arestas=None, subtitulo=None, tema="claro"):
        """
        Retorna uma Figure com o grafo. Se ``rota`` for informada, as arestas
        percorridas ficam em vermelho e cada trecho recebe sua ordem de percurso
        (1º, 2º, ...); o vértice inicial fica verde e o final vermelho.
        ``arestas`` destaca um conjunto de arestas sem ordem.
        ``tema`` escolhe a paleta em TEMAS ("claro" ou "escuro").
        """
        G, pos, t = self.G, self.posicoes, TEMAS[tema]
        fig = Figure(figsize=(10, 6.8), facecolor=t["fundo"])
        ax = fig.subplots()
        ax.set_facecolor(t["fundo"])
        ax.set_title(titulo, fontsize=13, fontweight="bold", pad=14, color=t["texto"])

        nos = list(G.nodes())
        cores = [t["no"]] * len(nos)
        if rota:
            cores[nos.index(rota[0])] = t["inicio"]
            cores[nos.index(rota[-1])] = t["fim"]

        nx.draw_networkx_edges(G, pos, ax=ax, width=1.8, edge_color=t["aresta"])
        if arestas:
            nx.draw_networkx_edges(G, pos, ax=ax, edgelist=list(arestas),
                                   width=4.2, edge_color=t["destaque"])
        if rota:
            self._desenhar_rota(ax, rota, t)

        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=4200, node_color=cores,
                               edgecolors=t["borda_no"], linewidths=1.5)
        rotulos = {n: n.replace(" ", "\n") if len(n) > 10 else n for n in nos}
        nx.draw_networkx_labels(G, pos, ax=ax, labels=rotulos,
                                font_size=9.5, font_weight="bold", font_color=t["texto"])
        nx.draw_networkx_edge_labels(
            G, pos, ax=ax, edge_labels=nx.get_edge_attributes(G, "weight"),
            font_size=11, font_color=t["peso"], font_weight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc=t["fundo_peso"], ec="none", alpha=0.9),
        )
        if subtitulo:
            ax.text(0.5, -0.02, subtitulo, transform=ax.transAxes, ha="center",
                    fontsize=10, style="italic", color=t["subtitulo"])

        ax.margins(x=0.08, y=0.1)
        ax.axis("off")
        fig.tight_layout()
        return fig

    def _desenhar_rota(self, ax, rota, t):
        pos = self.posicoes
        trechos = list(zip(rota[:-1], rota[1:]))
        nx.draw_networkx_edges(self.G, pos, ax=ax, edgelist=trechos,
                               width=4.2, edge_color=t["destaque"])
        # Ordem de percurso (um mesmo trecho pode ser usado duas vezes num passeio)
        ordem = {}
        for i, (u, v) in enumerate(trechos, 1):
            ordem.setdefault(frozenset((u, v)), []).append(str(i))
        for chave, idx in ordem.items():
            u, v = tuple(chave)
            (x1, y1), (x2, y2) = pos[u], pos[v]
            ax.text(x1 + 0.3 * (x2 - x1), y1 + 0.3 * (y2 - y1), "º, ".join(idx) + "º",
                    fontsize=9, color="white", fontweight="bold", ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.3", fc=t["destaque"], ec="none"))

    # ------------------------------------------------------------------ #
    @staticmethod
    def salvar(fig, caminho, dpi=200):
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
        fig.savefig(caminho, dpi=dpi, facecolor=fig.get_facecolor())
        return caminho

    @staticmethod
    def para_base64(fig, dpi=110):
        """PNG codificado em base64, para embutir em <img src="data:image/png;base64,...">."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", dpi=dpi, facecolor=fig.get_facecolor())
        return base64.b64encode(buffer.getvalue()).decode("ascii")
