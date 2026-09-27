"""Interface web (Flask) para visualizar os resultados e editar os dados do problema."""

import json
import math
import os

from flask import (Flask, Response, flash, jsonify, redirect, render_template, request,
                   url_for)

from transporte import (AnaliseTransporte, Configuracao, ErroConfiguracao,
                        RepositorioConfiguracao, VisualizadorGrafo, brl, num)


class ServicoResultados:
    """Calcula resultados e imagens, reaproveitando o último cálculo se os dados não mudaram."""

    def __init__(self):
        self._chave = None
        self._cache = None

    def obter(self, config):
        chave = json.dumps(config.para_dict(), sort_keys=True)
        if chave != self._chave:
            analise = AnaliseTransporte(config)
            resultados = analise.executar()
            # Uma imagem por tema; a página exibe a que corresponde ao modo claro/noturno
            claras, escuras = (
                [VisualizadorGrafo.para_base64(f) for f in analise.figuras(resultados, tema).values()]
                for tema in ("claro", "escuro"))
            imagens = [{"claro": c, "escuro": e} for c, e in zip(claras, escuras)]
            self._chave, self._cache = chave, (analise, resultados, imagens)
        return self._cache


def _para_json(valor):
    """Converte tuplas/conjuntos em listas e infinito (rota inexistente) em null."""
    if isinstance(valor, float) and not math.isfinite(valor):
        return None
    if isinstance(valor, dict):
        return {k: _para_json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [_para_json(v) for v in valor]
    return valor


def _config_do_formulario(form):
    """Monta um dicionário de configuração a partir dos campos do formulário."""
    arestas = [
        [u, v, p] for u, v, p in zip(form.getlist("origem"), form.getlist("destino"),
                                      form.getlist("peso"))
        if u.strip() or v.strip() or p.strip()
    ]
    posicoes = {
        n.strip(): [x, y] for n, x, y in zip(form.getlist("pos_nome"), form.getlist("pos_x"),
                                             form.getlist("pos_y"))
        if n.strip() and x.strip() and y.strip()
    }
    return {
        "sede": form.get("sede", ""),
        "valor_por_custo": form.get("valor_por_custo", "0") or "0",
        "destino_menor_caminho": form.get("destino_menor_caminho", ""),
        "origem_rota_final": form.get("origem_rota_final", ""),
        "arestas": arestas,
        "posicoes": {n: [x.replace(",", "."), y.replace(",", ".")] for n, (x, y) in posicoes.items()},
    }


def criar_app(repositorio=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave")
    repo = repositorio or RepositorioConfiguracao()
    servico = ServicoResultados()

    app.jinja_env.filters["brl"] = brl
    app.jinja_env.filters["num"] = num

    @app.context_processor
    def contexto_global():
        return {"personalizada": repo.personalizada}

    def carregar_ou_erro():
        try:
            return repo.carregar(), None
        except (ErroConfiguracao, json.JSONDecodeError, OSError) as exc:
            return None, str(exc)

    # ------------------------------------------------------------------ #
    @app.get("/")
    def resultados():
        config, erro = carregar_ou_erro()
        if erro:
            return render_template("erro.html", erro=erro), 500
        analise, r, imagens = servico.obter(config)
        return render_template("resultados.html", c=config, r=r, g=analise.grafo, imagens=imagens)

    @app.get("/cartilha")
    def cartilha():
        return render_template("cartilha.html")

    @app.get("/api/resultados")
    def api_resultados():
        config, erro = carregar_ou_erro()
        if erro:
            return jsonify({"erro": erro}), 500
        _, r, _ = servico.obter(config)
        r = {**r, "3.3": {  # cópia: não altera o cache
            **r["3.3"],
            "arestas_arvore": sorted(r["3.3"]["arestas_arvore"]),
            "todos": {d: [{"rota": c, "custo": w} for c, w in v]
                      for d, v in r["3.3"]["todos"].items()},
        }}
        return Response(json.dumps(_para_json({"configuracao": config.para_dict(), "resultados": r}),
                                   ensure_ascii=False, indent=2),
                        mimetype="application/json")

    @app.route("/configuracao", methods=["GET", "POST"])
    def configuracao():
        erros = []
        if request.method == "POST":
            dados = _config_do_formulario(request.form)
            try:
                repo.salvar(Configuracao.de_dict(dados))
                flash("Configuração salva. Resultados recalculados.", "sucesso")
                return redirect(url_for("resultados"))
            except ErroConfiguracao as exc:
                erros = exc.erros
        else:
            config, erro = carregar_ou_erro()
            if erro:
                erros = [erro]
                config = repo.carregar_padrao()
            dados = config.para_dict()
        return render_template("configuracao.html", d=dados, erros=erros)

    @app.post("/configuracao/restaurar")
    def restaurar():
        repo.restaurar_padrao()
        flash("Dados padrão do enunciado restaurados.", "sucesso")
        return redirect(url_for("resultados"))

    @app.get("/configuracao/exportar")
    def exportar():
        config, erro = carregar_ou_erro()
        if erro:
            config = repo.carregar_padrao()
        return Response(json.dumps(config.para_dict(), ensure_ascii=False, indent=2),
                        mimetype="application/json",
                        headers={"Content-Disposition": "attachment; filename=dados.json"})

    @app.post("/configuracao/importar")
    def importar():
        arquivo = request.files.get("arquivo")
        if not arquivo or not arquivo.filename:
            flash("Selecione um arquivo .json.", "erro")
            return redirect(url_for("configuracao"))
        try:
            repo.salvar(Configuracao.de_dict(json.load(arquivo.stream)))
        except (ErroConfiguracao, json.JSONDecodeError, UnicodeDecodeError, AttributeError) as exc:
            erros = exc.erros if isinstance(exc, ErroConfiguracao) else [f"JSON inválido: {exc}"]
            for e in erros:
                flash(e, "erro")
            return redirect(url_for("configuracao"))
        flash("Configuração importada.", "sucesso")
        return redirect(url_for("resultados"))

    return app
