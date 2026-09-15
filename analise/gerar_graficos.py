#!/usr/bin/env python3
"""Le resultados.csv (saida do app.Benchmark) e gera os graficos do relatorio."""

import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

CSV = Path(sys.argv[1] if len(sys.argv) > 1 else "dados/resultados.csv")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "analise/figuras")
OUT.mkdir(parents=True, exist_ok=True)

NAO_ORD = "#2a78d6"   # slot categorico 1
ORD = "#eb6834"       # slot categorico 2
TXT = "#0b0b0b"
TXT2 = "#52514e"
GRID = "#d9d8d4"

plt.rcParams.update({
    "font.size": 10,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": GRID,
    "axes.labelcolor": TXT2,
    "text.color": TXT,
    "xtick.color": TXT2,
    "ytick.color": TXT2,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
})


def flt(txt):
    """Aceita tanto 32.45 quanto 32,45 (JVM em locale pt-BR imprime com virgula)."""
    return float(str(txt).strip().replace(",", "."))


def carregar():
    dados = defaultdict(list)
    with CSV.open() as f:
        leitor = csv.DictReader(f, delimiter=";")
        for linha in leitor:
            if not linha.get("n") or not linha["n"].isdigit():
                continue
            chave = (int(linha["n"]), linha["ordenada"] == "true")
            dados[chave].append({
                "montagem": flt(linha["montagem_ms"]),
                "busca_tel": flt(linha["busca_tel_ms"]),
                "busca_nome": flt(linha["busca_nome_ms"]),
                "remocao": flt(linha["remocao_ms"]),
            })
    resumo = {}
    for chave, medicoes in dados.items():
        resumo[chave] = {
            campo: statistics.median(m[campo] for m in medicoes)
            for campo in ("montagem", "busca_tel", "busca_nome", "remocao")
        }
        resumo[chave]["execucoes"] = len(medicoes)
    return resumo


def serie(resumo, ordenada, campo):
    pontos = sorted((n, v[campo]) for (n, o), v in resumo.items() if o == ordenada)
    return [p[0] for p in pontos], [p[1] for p in pontos]


def milhares(x, _):
    return f"{int(x/1000)}k" if x >= 1000 else str(int(x))


def grafico(nome, titulo, ylabel, series, anotar_ultimo=True, logy=False):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for rotulo, (xs, ys), cor in series:
        if not xs:
            continue
        ax.plot(xs, ys, marker="o", markersize=6, linewidth=2,
                color=cor, label=rotulo, markeredgecolor="white",
                markeredgewidth=1.2)
        if anotar_ultimo:
            ax.annotate(f"{ys[-1]:,.1f}".replace(",", "."),
                        (xs[-1], ys[-1]), textcoords="offset points",
                        xytext=(-6, 9), ha="right", fontsize=9, color=TXT2)
    ax.set_title(titulo, fontsize=11.5, color=TXT, pad=10, loc="left")
    ax.set_xlabel("Tamanho da entrada (n contatos)")
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(FuncFormatter(milhares))
    if logy:
        ax.set_yscale("log")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if len(series) > 1:
        ax.legend(frameon=False, labelcolor=TXT2)
    fig.tight_layout()
    fig.savefig(OUT / nome, dpi=200)
    plt.close(fig)


def main():
    r = carregar()

    grafico("fig1_montagem_naoordenada.png",
            "Montagem das listas NÃO-ORDENADAS",
            "Tempo (ms)",
            [("Não-ordenada", serie(r, False, "montagem"), NAO_ORD)])

    grafico("fig2_montagem_ordenada.png",
            "Montagem das listas ORDENADAS",
            "Tempo (ms)",
            [("Ordenada", serie(r, True, "montagem"), ORD)])

    grafico("fig3_montagem_log.png",
            "Montagem: ordenada x não-ordenada (escala log)",
            "Tempo (ms, escala log)",
            [("Não-ordenada", serie(r, False, "montagem"), NAO_ORD),
             ("Ordenada", serie(r, True, "montagem"), ORD)],
            logy=True)

    grafico("fig4_busca_telefone.png",
            "Pesquisa pelo telefone do último contato do arquivo",
            "Tempo (ms)",
            [("Não-ordenada", serie(r, False, "busca_tel"), NAO_ORD),
             ("Ordenada", serie(r, True, "busca_tel"), ORD)])

    grafico("fig5_busca_nome.png",
            "Pesquisa pelo nome do último contato do arquivo",
            "Tempo (ms)",
            [("Não-ordenada", serie(r, False, "busca_nome"), NAO_ORD),
             ("Ordenada", serie(r, True, "busca_nome"), ORD)])

    grafico("fig6_remocao.png",
            "Remoção do último contato do arquivo (por telefone)",
            "Tempo (ms)",
            [("Não-ordenada", serie(r, False, "remocao"), NAO_ORD),
             ("Ordenada", serie(r, True, "remocao"), ORD)])

    print("Figuras geradas em", OUT)
    for chave in sorted(r):
        print(chave, r[chave])


if __name__ == "__main__":
    main()
