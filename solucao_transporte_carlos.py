"""
Atividade Ativa - Teoria dos Grafos e Análise de Algoritmos
Cliente: Empresa de Transporte de Carlos | Desenvolvedora: VOCÊ SA

Execução em modo console: imprime os itens 3.1 a 3.5 e grava as imagens .png e
o log saida_console.txt na pasta ./saidas. Os dados vêm de config/dados.json
(se existir) ou de config/dados_padrao.json.

    python solucao_transporte_carlos.py

A lógica fica no pacote ``transporte``; este módulo também expõe a interface
funcional antiga (construir_grafo, menor_caminho, ...) usada por gerar_relatorio.py.
Para a interface web, execute: python app.py
"""

import os

from transporte import (AnaliseTransporte, GrafoEntregas, OtimizadorRotas, RelatorioConsole,
                        RepositorioConfiguracao, VisualizadorGrafo, brl)  # brl: usado por gerar_relatorio.py

PASTA_SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saidas")

CONFIG = RepositorioConfiguracao().carregar()
SEDE = CONFIG.sede
VALOR_POR_CUSTO = CONFIG.valor_por_custo
ARESTAS = CONFIG.arestas
POSICOES = CONFIG.posicoes


# --------------------------------------------------------------------------- #
# Interface funcional (compatibilidade). G é o networkx.Graph de GrafoEntregas.
# --------------------------------------------------------------------------- #
def _grafo(G):
    g = GrafoEntregas([])
    g.G = G
    return g


def construir_grafo():
    return GrafoEntregas(ARESTAS).G


def custo_rota(G, rota):
    return _grafo(G).custo_rota(rota)


def formatar_rota(G, rota):
    return _grafo(G).formatar_rota(rota)


def menor_caminho(G, origem, destino):
    return OtimizadorRotas(_grafo(G)).menor_caminho(origem, destino)


def custos_a_partir_da_sede(G, sede=SEDE):
    return OtimizadorRotas(_grafo(G)).custos_a_partir_da_sede(sede)


def otimizar_rota_completa(G, origem, destino_final=None):
    return OtimizadorRotas(_grafo(G)).otimizar_rota_completa(origem, destino_final)


def plotar_grafo(G, titulo, nome_arquivo, rota=None, subtitulo=None, arestas=None):
    vis = VisualizadorGrafo(_grafo(G), POSICOES)
    fig = vis.desenhar(titulo, rota=rota, arestas=arestas, subtitulo=subtitulo)
    return vis.salvar(fig, os.path.join(PASTA_SAIDA, nome_arquivo))


def main():
    RelatorioConsole(AnaliseTransporte(CONFIG), PASTA_SAIDA).executar()


if __name__ == "__main__":
    main()
