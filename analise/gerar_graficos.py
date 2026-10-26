#!/usr/bin/env python3
"""Le dados/resultados.csv (saida do app.Benchmark) e gera os graficos do relatorio."""

import csv
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

RAIZ = Path(__file__).resolve().parent.parent
CSV = Path(sys.argv[1]) if len(sys.argv) > 1 else RAIZ / "dados" / "resultados.csv"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else RAIZ / "analise" / "figuras"
OUT.mkdir(parents=True, exist_ok=True)

# paleta categorica validada (slots 1 a 4)
COR = {
    "arvore_balanceada": "#2a78d6",
    "arvore_degenerada": "#eb6834",
    "avl_crescente": "#1baf7a",
    "avl_balanceada": "#eda100",
    "lista_nao_ordenada": "#e87ba4",
    "lista_ordenada": "#008300",
}
ROTULO = {
    "arvore_balanceada": "Árvore binária (balanceada)",
    "arvore_degenerada": "Árvore binária (degenerada)",
    "avl_crescente": "AVL (entrada crescente)",
    "avl_balanceada": "AVL (entrada balanceada)",
    "lista_nao_ordenada": "Lista não-ordenada",
    "lista_ordenada": "Lista ordenada",
}
TXT, TXT2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"

plt.rcParams.update({
    "font.size": 10, "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.edgecolor": GRID, "axes.labelcolor": TXT2, "text.color": TXT,
    "xtick.color": TXT2, "ytick.color": TXT2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6,
})

CAMPOS = ("montagem", "busca_tel", "busca_nome", "remocao")


def flt(txt):
    return float(str(txt).strip().replace(",", "."))


def carregar():
    bruto = defaultdict(list)
    alturas = {}
    with CSV.open() as f:
        for linha in csv.DictReader(f, delimiter=";"):
            if not linha.get("n") or not str(linha["n"]).isdigit():
                continue
            chave = (linha["estrutura"], int(linha["n"]))
            bruto[chave].append({c: flt(linha[f"{c}_ms"]) for c in CAMPOS})
            alturas[chave] = int(linha["altura_tel"])
    resumo = {}
    for chave, med in bruto.items():
        resumo[chave] = {c: statistics.median(m[c] for m in med) for c in CAMPOS}
        resumo[chave]["execucoes"] = len(med)
        resumo[chave]["altura"] = alturas[chave]
    return resumo


def serie(r, estrutura, campo):
    pts = sorted((n, v[campo]) for (e, n), v in r.items() if e == estrutura)
    return [p[0] for p in pts], [p[1] for p in pts]


def milhares(x, _):
    return f"{int(x/1000)}k" if x >= 1000 else str(int(x))


def grafico(nome, titulo, ylabel, series, logy=False, anotar=True):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for est, (xs, ys) in series:
        if not xs:
            continue
        ax.plot(xs, ys, marker="o", markersize=6, linewidth=2, color=COR[est],
                label=ROTULO[est], markeredgecolor="white", markeredgewidth=1.2)
        if anotar:
            v = ys[-1]
            if v < 0.01:
                txt = f"{v:,.4f}".replace(".", ",")
            elif v < 100:
                txt = f"{v:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
            else:
                txt = f"{v:,.0f}".replace(",", ".")
            ax.annotate(txt, (xs[-1], v), textcoords="offset points",
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
        ax.legend(frameon=False, labelcolor=TXT2, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / nome, dpi=200)
    plt.close(fig)


def grafico_altura(r, nome):
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    for est in ("arvore_degenerada", "arvore_balanceada"):
        pts = sorted((n, v["altura"]) for (e, n), v in r.items() if e == est)
        if not pts:
            continue
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, marker="o", markersize=6, linewidth=2, color=COR[est],
                label=ROTULO[est], markeredgecolor="white", markeredgewidth=1.2)
        ax.annotate(f"{ys[-1]:,.0f}".replace(",", "."), (xs[-1], ys[-1]),
                    textcoords="offset points", xytext=(-6, 9), ha="right",
                    fontsize=9, color=TXT2)
    # referencia teorica piso(log2 n)
    xs = sorted({n for (_, n) in r})
    ax.plot(xs, [math.floor(math.log2(n)) for n in xs], linestyle="--", linewidth=1.4,
            color="#52514e", label="piso(log₂ n) — mínimo teórico")
    ax.set_title("Altura da árvore indexada por telefone", fontsize=11.5,
                 color=TXT, pad=10, loc="left")
    ax.set_xlabel("Tamanho da entrada (n contatos)")
    ax.set_ylabel("Altura (escala log)")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(milhares))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, labelcolor=TXT2, fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / nome, dpi=200)
    plt.close(fig)


def main():
    r = carregar()
    arv = ["arvore_balanceada", "arvore_degenerada"]
    todas = [e for e in ("arvore_balanceada", "arvore_degenerada",
                         "lista_nao_ordenada", "lista_ordenada")
             if any(k[0] == e for k in r)]

    grafico("fig1_montagem_arvores.png",
            "Leitura do arquivo e montagem das árvores (escala log)",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "montagem")) for e in arv], logy=True)

    grafico_altura(r, "fig2_altura.png")

    grafico("fig3_busca_telefone.png",
            "Pesquisa pelo telefone da folha mais distante da raiz",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "busca_tel")) for e in arv], logy=True)

    grafico("fig4_busca_nome.png",
            "Pesquisa pelo nome do mesmo contato",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "busca_nome")) for e in arv], logy=True)

    grafico("fig5_remocao.png",
            "Remoção do mesmo contato, pelo telefone",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "remocao")) for e in arv], logy=True)

    grafico("fig6_montagem_comparacao.png",
            "Montagem: árvores x listas (escala log)",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "montagem")) for e in todas], logy=True, anotar=False)

    grafico("fig7_busca_comparacao.png",
            "Pesquisa no pior caso: árvores x listas (escala log)",
            "Tempo (ms, escala log)",
            [(e, serie(r, e, "busca_tel")) for e in todas], logy=True, anotar=False)

    avl = [e for e in ("avl_crescente", "avl_balanceada") if any(k[0] == e for k in r)]
    if avl:
        grafico("fig8_avl_montagem.png",
                "Montagem com a mesma entrada crescente (escala log)",
                "Tempo (ms, escala log)",
                [(e, serie(r, e, "montagem")) for e in ["avl_crescente", "arvore_degenerada"]],
                logy=True)

        grafico("fig9_avl_busca.png",
                "Pesquisa no pior caso: AVL x árvore binária (escala log)",
                "Tempo (ms, escala log)",
                [(e, serie(r, e, "busca_tel")) for e in
                 ["avl_crescente", "arvore_degenerada", "arvore_balanceada"]],
                logy=True, anotar=False)

        # altura: AVL x degenerada x minimo teorico
        fig, ax = plt.subplots(figsize=(6.4, 3.6))
        for est in ("arvore_degenerada", "avl_crescente"):
            pts = sorted((n, v["altura"]) for (e, n), v in r.items() if e == est)
            if not pts:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            ax.plot(xs, ys, marker="o", markersize=6, linewidth=2, color=COR[est],
                    label=ROTULO[est], markeredgecolor="white", markeredgewidth=1.2)
            ax.annotate(f"{ys[-1]:,.0f}".replace(",", "."), (xs[-1], ys[-1]),
                        textcoords="offset points", xytext=(-6, 9), ha="right",
                        fontsize=9, color=TXT2)
        xs = sorted({n for (_, n) in r})
        ax.plot(xs, [math.floor(math.log2(n)) for n in xs], linestyle="--", linewidth=1.4,
                color="#52514e", label="piso(log₂ n) — mínimo teórico")
        ax.set_title("Altura com a MESMA entrada crescente", fontsize=11.5, color=TXT,
                     pad=10, loc="left")
        ax.set_xlabel("Tamanho da entrada (n contatos)")
        ax.set_ylabel("Altura (escala log)")
        ax.set_yscale("log")
        ax.xaxis.set_major_formatter(FuncFormatter(milhares))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, labelcolor=TXT2, fontsize=9)
        fig.tight_layout()
        fig.savefig(OUT / "fig10_avl_altura.png", dpi=200)
        plt.close(fig)

    print("Figuras geradas em", OUT)
    for chave in sorted(r):
        print(chave, {k: (round(v, 4) if isinstance(v, float) else v)
                      for k, v in r[chave].items()})


if __name__ == "__main__":
    main()
