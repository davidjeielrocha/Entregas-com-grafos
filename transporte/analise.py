"""
Orquestra os cinco itens da Seção de Resultados a partir de uma Configuracao:

  3.1  Grafo (vértices, arestas e pesos)
  3.2  Menor caminho sede -> destino (Dijkstra)
  3.3  Custos entre a sede e todos os pontos
  3.4  Rota mais econômica que, partindo da sede, visita todos os pontos
  3.5  Custo em R$ para sair de um ponto, visitar todos e terminar na sede

O resultado é um dicionário usado tanto pela saída de console quanto pela web.
"""

from .formatacao import brl, num
from .grafo_entregas import GrafoEntregas
from .otimizador_rotas import OtimizadorRotas
from .visualizador import VisualizadorGrafo


class AnaliseTransporte:
    def __init__(self, config):
        self.config = config
        self.grafo = GrafoEntregas.de_configuracao(config)
        self.otimizador = OtimizadorRotas(self.grafo)
        self.visualizador = VisualizadorGrafo(self.grafo, config.posicoes)

    # ------------------------------------------------------------------ #
    def item_3_1(self):
        g = self.grafo
        return {"vertices": g.num_vertices, "arestas": g.num_arestas,
                "conexo": g.conexo, "graus": g.graus()}

    def item_3_2(self):
        c = self.config
        rota, custo = self.otimizador.menor_caminho(c.sede, c.destino_menor_caminho)
        return {"origem": c.sede, "destino": c.destino_menor_caminho,
                "rota": rota, "custo": custo, "trechos": self.grafo.trechos(rota)}

    def item_3_3(self):
        dijkstra, todos, agm = self.otimizador.custos_a_partir_da_sede(self.config.sede)
        return {
            "dijkstra": dijkstra,
            "soma_dijkstra": sum(c for *_, c in dijkstra),
            "todos": todos,
            "total_caminhos": sum(len(v) for v in todos.values()),
            "soma_caminhos": sum(w for v in todos.values() for _, w in v),
            "agm": [(u, v, d["weight"]) for u, v, d in agm.edges(data=True)],
            "custo_agm": agm.size(weight="weight"),
            "arestas_arvore": {tuple(sorted(e)) for _, r, _ in dijkstra
                               for e in zip(r[:-1], r[1:])},
        }

    def item_3_4(self):
        r = self.otimizador.otimizar_rota_completa(origem=self.config.sede)
        return {"avaliadas": r["avaliadas"], "estrita": r["estrita"], "passeio": r["passeio"]}

    def item_3_5(self):
        c = self.config
        r = self.otimizador.otimizar_rota_completa(origem=c.origem_rota_final,
                                                   destino_final=c.sede)
        (_, custo_e), (_, custo_p) = r["estrita"], r["passeio"]
        v = c.valor_por_custo
        return {
            "origem": c.origem_rota_final, "destino": c.sede, "valor_por_custo": v,
            "avaliadas": r["avaliadas"], "estrita": r["estrita"], "passeio": r["passeio"],
            "valor_estrita": custo_e * v if r["estrita"][0] else None,
            "valor_passeio": custo_p * v,
            "economia": (custo_e - custo_p) * v if r["estrita"][0] else None,
        }

    def executar(self):
        return {"3.1": self.item_3_1(), "3.2": self.item_3_2(), "3.3": self.item_3_3(),
                "3.4": self.item_3_4(), "3.5": self.item_3_5()}

    # ------------------------------------------------------------------ #
    def figuras(self, resultados, tema="claro"):
        """Gera as cinco figuras no tema indicado. Retorna {nome_arquivo: Figure}."""
        c = self.config
        desenhar = lambda titulo, **kw: self.visualizador.desenhar(titulo, tema=tema, **kw)
        r2, r3, r4, r5 = (resultados[k] for k in ("3.2", "3.3", "3.4", "3.5"))
        rota4, custo4 = r4["estrita"] if r4["estrita"][0] else r4["passeio"]
        rota5, custo5 = r5["passeio"]
        return {
            "tela1_grafo_original.png": desenhar("Grafo dos pontos de entrega de Carlos"),
            "tela2_menor_caminho_ln_ls.png": desenhar(
                f"Menor caminho {r2['origem']} → {r2['destino']} (custo = {num(r2['custo'])})",
                rota=r2["rota"]),
            "tela3_arvore_dijkstra_sede.png": desenhar(
                f"Menores caminhos a partir da sede {c.sede} (árvore de Dijkstra)",
                arestas=r3["arestas_arvore"],
                subtitulo=f"Arestas em vermelho: união dos menores caminhos {c.sede} → cada ponto"),
            "tela4_rota_economica_lago_norte.png": desenhar(
                f"Rota mais econômica a partir de {c.sede} (custo = {num(custo4)})", rota=rota4),
            "tela5_rota_esplanada_lago_norte.png": desenhar(
                f"{r5['origem']} → todos → {c.sede} (custo = {num(custo5)} | "
                f"{brl(r5['valor_passeio'])})", rota=rota5),
        }
