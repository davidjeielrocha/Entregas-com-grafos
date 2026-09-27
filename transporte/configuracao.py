"""
Configuração do problema: pontos de entrega, custos, sede e parâmetros das consultas.

Os dados originais do enunciado ficam em ``config/dados_padrao.json`` (somente
leitura). Quando o usuário edita os dados (pela página web ou manualmente), eles
são gravados em ``config/dados.json``, que passa a ter prioridade. Apagar esse
arquivo — ou usar "Restaurar padrão" na web — volta aos dados originais.
"""

import json
import os
from dataclasses import dataclass, field

RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_CONFIG = os.path.join(RAIZ_PROJETO, "config")
ARQUIVO_PADRAO = os.path.join(PASTA_CONFIG, "dados_padrao.json")
ARQUIVO_USUARIO = os.environ.get("TRANSPORTE_CONFIG", os.path.join(PASTA_CONFIG, "dados.json"))

# Força bruta sobre permutações: 9 pontos intermediários = 9! = 362.880 ordens.
MAX_VERTICES = 11


class ErroConfiguracao(ValueError):
    """Dados inválidos; ``erros`` traz a lista de problemas encontrados."""

    def __init__(self, erros):
        super().__init__("; ".join(erros))
        self.erros = erros


def _numero(valor):
    """Converte para número mantendo inteiros como int (8.0 -> 8)."""
    n = float(str(valor).replace(",", "."))
    return int(n) if n.is_integer() else n


@dataclass
class Configuracao:
    sede: str
    valor_por_custo: float
    destino_menor_caminho: str
    origem_rota_final: str
    arestas: list = field(default_factory=list)   # [(origem, destino, peso), ...]
    posicoes: dict = field(default_factory=dict)  # {vertice: (x, y)}

    # ------------------------------------------------------------------ #
    @classmethod
    def de_dict(cls, dados):
        try:
            return cls(
                sede=str(dados["sede"]).strip(),
                valor_por_custo=float(str(dados["valor_por_custo"]).replace(",", ".")),
                destino_menor_caminho=str(dados["destino_menor_caminho"]).strip(),
                origem_rota_final=str(dados["origem_rota_final"]).strip(),
                arestas=[(str(u).strip(), str(v).strip(), _numero(w))
                         for u, v, w in dados.get("arestas", [])],
                posicoes={str(n).strip(): (float(x), float(y))
                          for n, (x, y) in dados.get("posicoes", {}).items()},
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ErroConfiguracao([f"Formato inválido: {exc}"]) from exc

    def para_dict(self):
        return {
            "sede": self.sede,
            "valor_por_custo": self.valor_por_custo,
            "destino_menor_caminho": self.destino_menor_caminho,
            "origem_rota_final": self.origem_rota_final,
            "arestas": [list(a) for a in self.arestas],
            "posicoes": {n: list(p) for n, p in self.posicoes.items()},
        }

    @property
    def vertices(self):
        vistos = []
        for u, v, _ in self.arestas:
            for n in (u, v):
                if n not in vistos:
                    vistos.append(n)
        return vistos

    # ------------------------------------------------------------------ #
    def validar(self):
        """Retorna a lista de erros (vazia quando a configuração é válida)."""
        erros = []
        if not self.arestas:
            erros.append("Informe ao menos uma ligação (aresta).")
        pares = set()
        for i, (u, v, w) in enumerate(self.arestas, 1):
            if not u or not v:
                erros.append(f"Ligação {i}: origem e destino são obrigatórios.")
            elif u == v:
                erros.append(f"Ligação {i}: origem e destino iguais ({u}).")
            if not isinstance(w, (int, float)) or w <= 0:
                erros.append(f"Ligação {i}: o custo deve ser um número positivo.")
            par = frozenset((u, v))
            if par in pares:
                erros.append(f"Ligação {i}: {u} - {v} está duplicada.")
            pares.add(par)

        vertices = self.vertices
        if len(vertices) > MAX_VERTICES:
            erros.append(f"Máximo de {MAX_VERTICES} pontos (a otimização testa todas as ordens).")
        for rotulo, nome in (("Sede", self.sede),
                             ("Destino do menor caminho", self.destino_menor_caminho),
                             ("Origem da rota final", self.origem_rota_final)):
            if nome not in vertices:
                erros.append(f"{rotulo} '{nome}' não aparece em nenhuma ligação.")
        if self.valor_por_custo < 0:
            erros.append("O valor por unidade de custo não pode ser negativo.")
        if self.origem_rota_final == self.sede:
            erros.append("A origem da rota final deve ser diferente da sede.")
        if not erros and not self._conexo():
            erros.append("O grafo precisa ser conexo: todos os pontos devem estar ligados.")
        return erros

    def _conexo(self):
        vizinhos = {n: set() for n in self.vertices}
        for u, v, _ in self.arestas:
            vizinhos[u].add(v)
            vizinhos[v].add(u)
        visitados, pilha = set(), [self.sede]
        while pilha:
            n = pilha.pop()
            if n not in visitados:
                visitados.add(n)
                pilha.extend(vizinhos[n] - visitados)
        return len(visitados) == len(vizinhos)


class RepositorioConfiguracao:
    """Lê e grava a configuração, com fallback para os dados padrão."""

    def __init__(self, arquivo_padrao=ARQUIVO_PADRAO, arquivo_usuario=ARQUIVO_USUARIO):
        self.arquivo_padrao = arquivo_padrao
        self.arquivo_usuario = arquivo_usuario

    @property
    def personalizada(self):
        return os.path.exists(self.arquivo_usuario)

    def carregar_padrao(self):
        return self._ler(self.arquivo_padrao)

    def carregar(self):
        return self._ler(self.arquivo_usuario if self.personalizada else self.arquivo_padrao)

    def salvar(self, config):
        erros = config.validar()
        if erros:
            raise ErroConfiguracao(erros)
        os.makedirs(os.path.dirname(self.arquivo_usuario), exist_ok=True)
        with open(self.arquivo_usuario, "w", encoding="utf-8") as f:
            json.dump(config.para_dict(), f, ensure_ascii=False, indent=2)

    def restaurar_padrao(self):
        if self.personalizada:
            os.remove(self.arquivo_usuario)

    @staticmethod
    def _ler(caminho):
        with open(caminho, encoding="utf-8") as f:
            config = Configuracao.de_dict(json.load(f))
        erros = config.validar()
        if erros:
            raise ErroConfiguracao([f"{os.path.basename(caminho)}: {e}" for e in erros])
        return config
