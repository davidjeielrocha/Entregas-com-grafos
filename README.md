# Rotas de Entrega — Empresa de Transporte de Carlos

Atividade Ativa de **Teoria dos Grafos e Análise de Algoritmos**. Os pontos de entrega
de Carlos em Brasília são modelados como um grafo não direcionado e ponderado. O
programa resolve os cinco itens da Seção de Resultados:

| Item | O que calcula | Algoritmo |
|------|---------------|-----------|
| 3.1 | Desenho do grafo (vértices, arestas, pesos) e grau de cada ponto | — |
| 3.2 | Menor caminho entre a sede e um destino | Dijkstra |
| 3.3 | Custos entre a sede e todos os pontos | Dijkstra, caminhos simples, Prim (AGM) |
| 3.4 | Rota mais econômica que sai da sede e visita todos os pontos | Força bruta (permutações) |
| 3.5 | Custo em R$ para sair de um ponto, visitar todos e terminar na sede | Força bruta + Dijkstra |

O programa pode ser executado de duas formas, que usam os mesmos dados e os mesmos cálculos:

| Modo | Comando | Indicado para |
|------|---------|---------------|
| **Web (Flask)** | `python app.py` | Consultar os resultados de forma interativa, editar os dados, usar o modo noturno e a cartilha de uso |
| **Console** | `python solucao_transporte_carlos.py` | Ver os resultados em texto e gerar as imagens e o log em `saidas/` |

---

## 1. Instalação

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 2. Execução no modo web

### Iniciar o servidor

Na pasta do projeto, com o ambiente virtual ativo:

```bash
python app.py
```

O terminal mostra `Running on http://127.0.0.1:5000`. Abra esse endereço no navegador.
Para encerrar o servidor, pressione <kbd>Ctrl</kbd>+<kbd>C</kbd> no terminal.

Opções de linha de comando:

| Opção | Efeito | Exemplo |
|-------|--------|---------|
| `--port` | Usa outra porta (padrão 5000) | `python app.py --port 8080` |
| `--host` | Endereço de escuta; `0.0.0.0` libera o acesso por outras máquinas da rede | `python app.py --host 0.0.0.0` |
| `--debug` | Recarrega automaticamente ao editar código ou templates | `python app.py --debug` |

> Sem `--debug`, alterações em arquivos `.py` ou nos templates só aparecem depois de reiniciar o servidor.

### Menu superior

| Elemento | Função |
|----------|--------|
| **Resultados** | Página inicial com os itens 3.1 a 3.5 |
| **Configuração** | Edição dos pontos, ligações, custos e parâmetros |
| Selo **Dados padrão** / **Dados personalizados** | Indica se estão em uso os dados do enunciado ou dados editados (selo laranja) |
| Botão **☾ / ☀** | Alterna entre o modo claro e o **modo noturno** |
| Botão **? Cartilha de uso** | Abre o guia de uso; fica fixo no lado direito do menu |

### Páginas e endereços

| Endereço | Conteúdo |
|----------|----------|
| `/` | Resumo (sede, pontos, ligações, valor por custo) e resultados dos itens 3.1 a 3.5, com imagens do grafo e das rotas |
| `/configuracao` | Formulário para editar os dados, além de exportar, importar e restaurar o padrão (ver seção 5) |
| `/cartilha` | Cartilha com orientações de uso (ver seção 4) |
| `/configuracao/exportar` | Baixa a configuração atual em JSON |
| `/api/resultados` | Configuração e resultados completos em JSON, para integração com outros sistemas |

### Modo noturno

Na primeira visita, a interface segue o tema do sistema operacional ou do navegador. O
botão ☾/☀ alterna manualmente, e a escolha fica salva no navegador para todas as páginas.
As imagens do grafo são geradas nas duas paletas, então os mapas também escurecem. Os
arquivos gravados em `saidas/` pelo modo console continuam no tema claro.

---

## 3. Execução no modo console

### Executar

```bash
python solucao_transporte_carlos.py
```

No Windows, se os acentos aparecerem trocados, execute antes:

```bash
set PYTHONIOENCODING=utf-8          # Prompt de Comando
$env:PYTHONIOENCODING = "utf-8"     # PowerShell
```

### O que é exibido

O programa imprime um bloco para cada item. Trecho da saída com os dados padrão:

```
==============================================================================
ITEM 3.2 - MENOR CAMINHO: LAGO NORTE -> LAGO SUL (Dijkstra)
==============================================================================
  Rota : Lago Norte -(8)-> Esplanada -(5)-> Asa Sul -(5)-> Lago Sul
  Custo: 18
  [imagem salva] ...\saidas\tela2_menor_caminho_ln_ls.png
```

Os números entre `-( )->` são os custos de cada trecho. O item 3.3 lista também todos os
caminhos simples da sede até cada ponto e a Árvore Geradora Mínima.

### Arquivos gerados em `saidas/`

| Arquivo | Conteúdo |
|---------|----------|
| `tela1_grafo_original.png` | Grafo completo (item 3.1) |
| `tela2_menor_caminho_ln_ls.png` | Menor caminho da sede ao destino (item 3.2) |
| `tela3_arvore_dijkstra_sede.png` | Menores caminhos a partir da sede (item 3.3) |
| `tela4_rota_economica_lago_norte.png` | Rota mais econômica visitando todos (item 3.4) |
| `tela5_rota_esplanada_lago_norte.png` | Rota completa até a sede, com valor em R$ (item 3.5) |
| `saida_console.txt` | Cópia de tudo o que foi impresso no console |

Os nomes dos arquivos são fixos, mesmo quando a sede ou os pontos são alterados. Cada
execução sobrescreve os arquivos anteriores.

### Relação com o modo web

Os dois modos leem a mesma configuração (seção 5). Dados salvos pela página
**Configuração** passam a valer também no console na próxima execução de
`solucao_transporte_carlos.py`.

---

## 4. Cartilha de uso

A aplicação web inclui uma **cartilha** voltada a quem vai operar o sistema, sem exigir
conhecimento de programação ou de teoria dos grafos.

**Como acessar:** clique em **? Cartilha de uso**, no lado direito do menu superior de
qualquer página, ou abra <http://127.0.0.1:5000/cartilha>. Um sumário lateral permite
saltar entre as seções. Em telas pequenas, o sumário fica no topo.

| Seção | Orientações |
|-------|-------------|
| 1. O que a aplicação faz | Conceitos de ponto, ligação e custo; o que é calculado |
| 2. Conhecendo a tela | Menu, selo de dados, modo noturno e botão da cartilha |
| 3. Lendo os resultados | Como interpretar cada item de 3.1 a 3.5, as cores e a ordem 1º, 2º… nos mapas |
| 4. Alterando os dados | Passo a passo para editar parâmetros, ligações e posições |
| 5. Casos de uso comuns | Incluir ou remover bairro, atualizar o valor em R$, mudar a sede, reorganizar o desenho |
| 6. Guardar e compartilhar | Exportar e importar cenários em JSON |
| 7. Voltar ao padrão | Como e quando usar **Restaurar padrão** |
| 8. Mensagens de erro | Cada mensagem de validação e como resolvê-la |
| 9. Glossário | Vértice, aresta, peso, grau, Dijkstra, AGM, Caminho Hamiltoniano, passeio |

O conteúdo da cartilha fica em `web/templates/cartilha.html` e pode ser editado
diretamente nesse arquivo.

---

## 5. Configuração dos dados

### Dados padrão

Os dados do enunciado ficam em **`config/dados_padrao.json`** e são usados sempre que
não houver uma configuração personalizada. **Não edite este arquivo**: ele é a
referência para “Restaurar padrão”.

| Parâmetro | Valor padrão |
|-----------|--------------|
| Sede | Lago Norte |
| Destino do menor caminho (3.2) | Lago Sul |
| Origem da rota final (3.5) | Esplanada |
| Valor por unidade de custo | R$ 20,00 |

| Ligação | Custo | Ligação | Custo |
|---------|------:|---------|------:|
| Asa Sul — Lago Sul | 5 | Esplanada — Asa Norte | 6 |
| Asa Sul — Esplanada | 5 | Esplanada — Vila Planalto | 10 |
| Asa Sul — Asa Norte | 12 | Esplanada — Lago Norte | 8 |
| Lago Sul — Esplanada | 11 | Asa Norte — Lago Norte | 12 |
| Lago Sul — Vila Planalto | 14 | Vila Planalto — Lago Norte | 7 |

### Como editar

**Pela página web (recomendado):** acesse **Configuração**, altere os campos e clique
em **Salvar e recalcular**. É possível:

- mudar a sede, o destino do item 3.2, a origem do item 3.5 e o valor em R$;
- adicionar, alterar ou remover ligações (os pontos são criados a partir delas);
- definir a posição (x, y) de cada ponto no desenho — pontos sem posição são
  posicionados automaticamente;
- **Exportar JSON** / **Importar JSON** para guardar ou compartilhar cenários;
- **Restaurar padrão** para descartar as alterações.

O selo no topo da página indica se estão em uso os *Dados padrão* ou *Dados personalizados*.

**Editando o arquivo:** copie `config/dados_padrao.json` para `config/dados.json` e
edite a cópia. O formato é:

```json
{
  "sede": "Lago Norte",
  "valor_por_custo": 20.0,
  "destino_menor_caminho": "Lago Sul",
  "origem_rota_final": "Esplanada",
  "arestas": [
    ["Asa Sul", "Lago Sul", 5],
    ["Asa Sul", "Esplanada", 5]
  ],
  "posicoes": {
    "Asa Sul": [-0.8, 1.8],
    "Lago Sul": [1.0, 1.8]
  }
}
```

| Campo | Descrição |
|-------|-----------|
| `sede` | Ponto de partida dos itens 3.2–3.4 e ponto final do 3.5 |
| `valor_por_custo` | Valor em R$ de cada unidade de custo (item 3.5) |
| `destino_menor_caminho` | Destino do menor caminho do item 3.2 |
| `origem_rota_final` | Ponto de partida do item 3.5 (diferente da sede) |
| `arestas` | Lista `[ponto A, ponto B, custo]`; vias de mão dupla, custo positivo |
| `posicoes` | Opcional. Coordenadas `[x, y]` de cada ponto no desenho |

### Prioridade e restauração

1. Se a variável de ambiente `TRANSPORTE_CONFIG` estiver definida, o arquivo indicado
   nela é usado como configuração personalizada.
2. Senão, se existir `config/dados.json`, ele é usado.
3. Senão, valem os dados de `config/dados_padrao.json`.

Para voltar ao padrão, use **Restaurar padrão** na web ou apague `config/dados.json`.

### Regras de validação

Ao salvar, a configuração é rejeitada (com a lista de problemas) quando:

- não há ligações, uma ligação liga um ponto a ele mesmo ou aparece duplicada;
- algum custo é zero, negativo ou não numérico;
- a sede, o destino do 3.2 ou a origem do 3.5 não aparecem em nenhuma ligação;
- a origem do 3.5 é igual à sede, ou o valor em R$ é negativo;
- o grafo não é conexo (há pontos inalcançáveis);
- há mais de 11 pontos — os itens 3.4 e 3.5 testam todas as ordens de visita
  (com *n* pontos, até (*n*−1)! ordens), o que fica lento acima disso.

Se não existir uma rota que visite todos os pontos sem repetir nenhum (Caminho
Hamiltoniano), os itens 3.4 e 3.5 informam isso e apresentam o passeio ótimo, que
pode repassar por pontos.

---

## 6. Estrutura do projeto

```
AA-Grafos/
├── app.py                          # inicia o servidor web
├── solucao_transporte_carlos.py    # execução em console
├── requirements.txt
├── config/
│   ├── dados_padrao.json           # dados do enunciado (não editar)
│   └── dados.json                  # criado ao salvar dados personalizados
├── transporte/                     # lógica do problema
│   ├── configuracao.py             # Configuracao, RepositorioConfiguracao, ErroConfiguracao
│   ├── grafo_entregas.py           # GrafoEntregas: modelo G = (V, E, w)
│   ├── otimizador_rotas.py         # OtimizadorRotas: Dijkstra, caminhos, Prim, força bruta
│   ├── visualizador.py             # VisualizadorGrafo: imagens do grafo e das rotas
│   ├── analise.py                  # AnaliseTransporte: executa os itens 3.1–3.5
│   ├── relatorio_console.py        # RelatorioConsole: saída de texto e arquivos
│   └── formatacao.py               # brl() e num()
├── web/                            # interface Flask
│   ├── __init__.py                 # criar_app() e rotas
│   ├── templates/                  # base, resultados, configuracao, cartilha, erro
│   └── static/estilo.css           # estilos, com os temas claro e noturno
├── saidas/                         # imagens e log gerados pelo console
└── docs/                           # enunciado e guias
```

Fluxo: `RepositorioConfiguracao` carrega a `Configuracao` → `AnaliseTransporte` monta o
`GrafoEntregas`, usa o `OtimizadorRotas` para calcular os itens e o `VisualizadorGrafo`
para as imagens → o resultado é exibido pelo `RelatorioConsole` ou pelas páginas Flask.

### Uso em outro código Python

```python
from transporte import AnaliseTransporte, RepositorioConfiguracao

config = RepositorioConfiguracao().carregar()
resultados = AnaliseTransporte(config).executar()
print(resultados["3.5"]["valor_passeio"])   # 860.0 com os dados padrão
```

---

## 7. Resultados com os dados padrão

| Item | Resultado |
|------|-----------|
| 3.2 | Lago Norte → Esplanada → Asa Sul → Lago Sul — custo **18** |
| 3.3 | Soma dos menores custos a partir da sede: **58**; custo da AGM: **31** |
| 3.4 | Lago Norte → Vila Planalto → Lago Sul → Asa Sul → Esplanada → Asa Norte — custo **37** |
| 3.5 | Esplanada → Asa Norte → Esplanada → Asa Sul → Lago Sul → Vila Planalto → Lago Norte — custo 43 × R$ 20,00 = **R$ 860,00** (sem repetir pontos: R$ 880,00) |

---

## 8. Problemas comuns

| Sintoma | Solução |
|---------|---------|
| `python` não é reconhecido | Instale o Python marcando “Add to PATH”, ou use `py` no lugar de `python` no Windows |
| `ModuleNotFoundError: flask` / `networkx` | Ative o ambiente virtual e rode `pip install -r requirements.txt` |
| Página “Não foi possível carregar os dados” | `config/dados.json` está inválido: corrija-o, ou clique em **Restaurar padrão** |
| Porta 5000 ocupada | `python app.py --port 8080` |
| Alteração em template ou código não aparece na web | Reinicie o servidor ou execute com `--debug` |
| Imagens em `saidas/` não refletem os dados editados | Execute novamente `python solucao_transporte_carlos.py` |
| Caracteres estranhos no console do Windows | `set PYTHONIOENCODING=utf-8` antes de executar |
| Publicar o servidor fora da máquina local | Defina `FLASK_SECRET_KEY` com um valor secreto e use um servidor WSGI (ex.: `waitress-serve app:app`) |
