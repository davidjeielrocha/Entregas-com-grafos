"""Impressão dos resultados no console e gravação das imagens/log em ./saidas."""

import os
import sys

from .formatacao import brl, num


class _Tee:
    """Duplica a saída do console para um arquivo (evidência para o relatório)."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


class RelatorioConsole:
    def __init__(self, analise, pasta_saida):
        self.analise = analise
        self.grafo = analise.grafo
        self.config = analise.config
        self.pasta_saida = pasta_saida

    def executar(self):
        """Imprime todos os itens, salva as imagens e o log saida_console.txt."""
        os.makedirs(self.pasta_saida, exist_ok=True)
        with open(os.path.join(self.pasta_saida, "saida_console.txt"), "w", encoding="utf-8") as log:
            original = sys.stdout
            sys.stdout = _Tee(original, log)
            try:
                self._imprimir()
            finally:
                sys.stdout = original

    # ------------------------------------------------------------------ #
    @staticmethod
    def _cabecalho(texto):
        print("\n" + "=" * 78 + f"\n{texto}\n" + "=" * 78)

    def _salvar(self, figuras, nome):
        caminho = self.analise.visualizador.salvar(figuras[nome], os.path.join(self.pasta_saida, nome))
        print(f"  [imagem salva] {caminho}")

    def _imprimir(self):
        c, g = self.config, self.grafo
        r = self.analise.executar()
        figuras = self.analise.figuras(r)
        nomes = list(figuras)

        # 3.1 ---------------------------------------------------------------
        r1 = r["3.1"]
        self._cabecalho("ITEM 3.1 - GRAFO DOS PONTOS DE ENTREGA")
        print(f"  Vértices: {r1['vertices']} | Arestas: {r1['arestas']} | Conexo: {r1['conexo']}")
        for n, grau in r1["graus"]:
            print(f"  grau({n}) = {grau}")
        self._salvar(figuras, nomes[0])

        # 3.2 ---------------------------------------------------------------
        r2 = r["3.2"]
        self._cabecalho(f"ITEM 3.2 - MENOR CAMINHO: {r2['origem'].upper()} -> "
                        f"{r2['destino'].upper()} (Dijkstra)")
        print(f"  Rota : {g.formatar_rota(r2['rota'])}")
        print(f"  Custo: {num(r2['custo'])}")
        self._salvar(figuras, nomes[1])

        # 3.3 ---------------------------------------------------------------
        r3 = r["3.3"]
        self._cabecalho(f"ITEM 3.3 - CUSTOS ENTRE A SEDE ({c.sede.upper()}) E TODOS OS PONTOS")
        print("\n[A] Menor custo da sede até cada ponto (Dijkstra):")
        for destino, rota, custo in r3["dijkstra"]:
            print(f"  {destino:<14} custo {num(custo):>2} | {g.formatar_rota(rota)}")
        print(f"  Soma dos menores custos: {num(r3['soma_dijkstra'])}")

        print("\n[B] Todos os caminhos simples da sede até cada ponto:")
        for destino, caminhos in r3["todos"].items():
            print(f"\n  -> {destino}: {len(caminhos)} caminhos")
            for i, (cam, w) in enumerate(caminhos, 1):
                print(f"     {i:02d}. custo {num(w):>2} | {' -> '.join(cam)}")
        print(f"\n  Total de caminhos simples: {r3['total_caminhos']} | "
              f"soma de todos os custos: {num(r3['soma_caminhos'])}")

        print("\n[C] Árvore Geradora Mínima (Prim):")
        for u, v, w in r3["agm"]:
            print(f"  {u} - {v} ({num(w)})")
        print(f"  Custo da AGM: {num(r3['custo_agm'])}")
        self._salvar(figuras, nomes[2])

        # 3.4 ---------------------------------------------------------------
        r4 = r["3.4"]
        self._cabecalho(f"ITEM 3.4 - ROTA MAIS ECONÔMICA VISITANDO TODOS (ORIGEM: {c.sede.upper()})")
        (rota4, custo4), (rota4p, custo4p) = r4["estrita"], r4["passeio"]
        print(f"  Ordens de visita avaliadas: {r4['avaliadas']}")
        if rota4:
            print(f"  Rota : {g.formatar_rota(rota4)}")
            print(f"  Custo: {num(custo4)}")
        else:
            print("  Não existe Caminho Hamiltoniano (rota sem repetir pontos).")
        if custo4p < custo4:
            print(f"  Passeio (com repetição) mais barato: custo {num(custo4p)} | "
                  f"{g.formatar_rota(rota4p)}")
        else:
            print(f"  Permitir repetir pontos não reduz o custo (passeio ótimo = {num(custo4p)}).")
        self._salvar(figuras, nomes[3])

        # 3.5 ---------------------------------------------------------------
        r5 = r["3.5"]
        v = r5["valor_por_custo"]
        self._cabecalho(f"ITEM 3.5 - {r5['origem'].upper()} -> TODOS OS PONTOS -> "
                        f"{c.sede.upper()} ({brl(v)}/custo)")
        (rota_e, custo_e), (rota_p, custo_p) = r5["estrita"], r5["passeio"]
        print("  Cenário 1 - Caminho Hamiltoniano (sem repetir pontos):")
        if rota_e:
            print(f"    {g.formatar_rota(rota_e)}")
            print(f"    Custo {num(custo_e)} x {brl(v)} = {brl(r5['valor_estrita'])}")
        else:
            print("    Não existe rota sem repetir pontos.")
        print(f"  Cenário 2 - Passeio ótimo (pode repassar por {r5['origem']}):")
        print(f"    {g.formatar_rota(rota_p)}")
        print(f"    Custo {num(custo_p)} x {brl(v)} = {brl(r5['valor_passeio'])}")
        if r5["economia"] is not None:
            print(f"  Economia do cenário 2: {brl(r5['economia'])}")
        self._salvar(figuras, nomes[4])
