#!/usr/bin/env python3
"""Gera o PDF do relatorio PARCIAL do Trabalho 2 (secoes 1 a 3)."""

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "dados" / "resultados.csv"
CSV_CONT = RAIZ / "dados" / "contagens.csv"
FIG = RAIZ / "analise" / "figuras"
SAIDA = RAIZ / "relatorio" / "Relatorio_Trabalho2.pdf"
SAIDA.parent.mkdir(parents=True, exist_ok=True)

REPO = "https://github.com/ryanlimap/trabalho_tpa"
AMBIENTE = ("AMD Ryzen 5 5600G (6 núcleos, 16 MB de cache L3), 32 GB de RAM DDR4 "
            "3200 MHz, Windows 11, OpenJDK 21 (64 bits). Todas as medições "
            "apresentadas nas seções 3 e 5 foram coletadas nessa mesma máquina, sem "
            "outros programas concorrendo pela CPU.")

AZUL = colors.HexColor("#12356b")
CINZA = colors.HexColor("#52514e")

ss = getSampleStyleSheet()
S = {
    "titulo": ParagraphStyle("titulo", parent=ss["Title"], fontSize=19, leading=24),
    "sub": ParagraphStyle("sub", parent=ss["Normal"], fontSize=12, leading=17,
                          alignment=TA_CENTER, textColor=CINZA),
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15, leading=19,
                         spaceBefore=16, spaceAfter=8, textColor=AZUL),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, leading=16,
                         spaceBefore=12, spaceAfter=5, textColor=colors.black),
    "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10.5, leading=14,
                         spaceBefore=9, spaceAfter=3, textColor=CINZA),
    "p": ParagraphStyle("p", parent=ss["BodyText"], fontSize=10, leading=14.5,
                        alignment=TA_JUSTIFY, spaceAfter=7),
    "cod": ParagraphStyle("cod", parent=ss["Code"], fontSize=7.2, leading=8.6,
                          backColor=colors.HexColor("#f6f6f4"), borderPadding=5,
                          leftIndent=0, textColor=colors.HexColor("#1a1a19")),
    "mono": ParagraphStyle("mono", parent=ss["Code"], fontSize=7.6, leading=9.6,
                           backColor=colors.HexColor("#eef3fa"), borderPadding=6,
                           leftIndent=0, textColor=colors.HexColor("#16233a")),
    "leg": ParagraphStyle("leg", parent=ss["Normal"], fontSize=8.5, leading=11,
                          alignment=TA_CENTER, textColor=CINZA, spaceAfter=10),
    "cel": ParagraphStyle("cel", parent=ss["Normal"], fontSize=8.5, leading=11),
    # Alinhado à esquerda: a justificação abre espaços enormes em linhas que
    # terminam com URLs longas, como na lista de fontes.
    "pl": ParagraphStyle("pl", parent=ss["BodyText"], fontSize=10, leading=14.5,
                         alignment=TA_LEFT, spaceAfter=7),
}

AB = "src/arvorebinaria/ArvoreBinaria.java"
AVL = "src/arvorebinaria/ArvoreAVL.java"
n2 = "n<super>2</super>"
logn = "log n"


def P(txt, estilo="p"):
    return Paragraph(txt, S[estilo])


def C(txt):
    return f"<font face='Courier'>{txt}</font>"


def codigo(arquivo, ini, fim, titulo):
    linhas = (RAIZ / arquivo).read_text(encoding="utf-8").splitlines()
    corpo = []
    for i in range(ini, fim + 1):
        t = linhas[i - 1].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        corpo.append(f"{i:>3}  {t}")
    bloco = "<br/>".join(l.replace(" ", "&nbsp;") for l in corpo)
    return KeepTogether([
        P(f"<b>{titulo}</b> &mdash; <font color='#52514e'>{arquivo}, linhas {ini}-{fim}</font>",
          "h3"),
        Paragraph(bloco, S["cod"]),
        Spacer(1, 9),
    ])


def mono(titulo, texto):
    linhas = [l.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
              for l in texto.strip("\n").split("\n")]
    bloco = "<br/>".join(l.replace(" ", "&nbsp;") for l in linhas)
    itens = []
    if titulo:
        itens.append(P(f"<b>{titulo}</b>", "h3"))
    itens += [Paragraph(bloco, S["mono"]), Spacer(1, 8)]
    return KeepTogether(itens)


def figura(nome, legenda, largura=15.0 * cm):
    from reportlab.lib.utils import ImageReader
    leitor = ImageReader(str(FIG / nome))
    lp, ap = leitor.getSize()
    img = Image(str(FIG / nome), width=largura, height=largura * ap / lp)
    return KeepTogether([img, Spacer(1, 3), P(legenda, "leg")])


def tabela(dados, larguras, destacar_col0=True):
    est_cab = ParagraphStyle("cab", parent=S["cel"], fontName="Helvetica-Bold",
                             textColor=colors.white, alignment=TA_CENTER)
    est_col0 = ParagraphStyle("col0", parent=S["cel"], fontName="Helvetica-Bold")
    est_cen = ParagraphStyle("cen", parent=S["cel"], alignment=TA_CENTER)
    corpo = []
    for i, linha in enumerate(dados):
        nova = []
        for j, cel in enumerate(linha):
            txt = str(cel).replace("\n", "<br/>")
            if i == 0:
                nova.append(Paragraph(txt, est_cab))
            elif j == 0 and destacar_col0:
                nova.append(Paragraph(txt, est_col0))
            else:
                nova.append(Paragraph(txt, est_cen if len(str(cel)) <= 26 else S["cel"]))
        corpo.append(nova)
    t = Table(corpo, colWidths=larguras, hAlign="CENTER", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9c8c4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f4")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


# ----------------------------------------------------------------------
# dados
# ----------------------------------------------------------------------
CAMPOS = ("montagem", "busca_tel", "busca_nome", "remocao")


def flt(txt):
    return float(str(txt).strip().replace(",", "."))


def num(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


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
    r = {}
    for chave, med in bruto.items():
        r[chave] = {c: statistics.median(m[c] for m in med) for c in CAMPOS}
        r[chave]["execucoes"] = len(med)
        r[chave]["altura"] = alturas[chave]
    return r


def carregar_contagens():
    d = {}
    if not CSV_CONT.exists():
        return d
    with CSV_CONT.open() as f:
        for linha in csv.DictReader(f, delimiter=";"):
            if not linha.get("n") or not str(linha["n"]).isdigit():
                continue
            d[(linha["rotulo"], int(linha["n"]))] = {
                "montagem": int(linha["comp_montagem"]),
                "busca": int(linha["comp_busca_tel"]),
                "altura": int(linha["altura_tel"]),
            }
    return d


def razoes_txt(r, estrutura, campo):
    """Descreve as razoes medidas entre tamanhos consecutivos, em texto."""
    pts = sorted((n, v[campo]) for (e, n), v in r.items() if e == estrutura)
    razoes = [pts[i][1] / pts[i - 1][1] for i in range(1, len(pts))]
    if not razoes:
        return "—"
    fmt = [f"{x:.2f}×".replace(".", ",") for x in razoes]
    if len(fmt) == 1:
        return fmt[0]
    return ", ".join(fmt[:-1]) + " e " + fmt[-1]


def tam(r, est):
    return sorted(n for (e, n) in r if e == est)


def tabela_metrica(r, campo, rotulo, casas=2):
    tamanhos = sorted({n for (_, n) in r})
    linhas = [["n", f"{rotulo}\nárvore balanceada", "razão",
               f"{rotulo}\nárvore degenerada", "razão"]]
    ant_b = ant_d = None
    for n in tamanhos:
        vb = r.get(("arvore_balanceada", n), {}).get(campo)
        vd = r.get(("arvore_degenerada", n), {}).get(campo)
        rb = f"{vb/ant_b:.2f}×".replace(".", ",") if (vb and ant_b) else "—"
        rd = f"{vd/ant_d:.2f}×".replace(".", ",") if (vd and ant_d) else "—"
        linhas.append([num(n, 0),
                       num(vb, casas) if vb is not None else "não medido", rb,
                       num(vd, casas) if vd is not None else "não medido", rd])
        if vb:
            ant_b = vb
        if vd:
            ant_d = vd
    return tabela(linhas, [2.1 * cm, 4.3 * cm, 1.8 * cm, 4.3 * cm, 1.8 * cm])


def construir():
    r = carregar()
    cont = carregar_contagens()
    hist = []

    # ---------------- capa ----------------
    hist += [
        Spacer(1, 3.0 * cm),
        Paragraph("Trabalho 2 — Árvores Binárias", S["titulo"]),
        Paragraph("Árvores binárias de busca, árvores AVL e análise de complexidade",
                  S["sub"]),
        Spacer(1, 1.2 * cm),
        Paragraph("Instituto Federal do Espírito Santo &mdash; Campus Serra<br/>"
                  "Técnicas de Programação Avançada<br/>"
                  "Prof. Victorio Albani de Carvalho", S["sub"]),
        Spacer(1, 1.6 * cm),
        Paragraph("<b>Integrantes do grupo</b>", S["sub"]),
        Spacer(1, 0.25 * cm),
        Paragraph("Lucas Ramos Pianissola<br/>Ryan Lima Peçanha<br/>Davi Alvarenga",
                  S["sub"]),
        Spacer(1, 1.2 * cm),
        Paragraph("<b>Repositório do projeto</b><br/>" + REPO, S["sub"]),
        Spacer(1, 1.2 * cm),
        Paragraph("Relatório completo: seção 1 (desenvolvimento), 2 (análise matemática da "
                  "árvore binária), 3 (análise empírica da árvore binária), 4 (análise da "
                  "árvore AVL), 5 (desempenho da AVL comparado ao da árvore binária comum) e "
                  "6 (árvores binárias na biblioteca padrão de Java).", S["sub"]),
        PageBreak(),
    ]

    # ---------------- seção 1 ----------------
    hist += [
        P("1. Desenvolvimento da biblioteca de árvores e do programa de teste", "h1"),
        P("1.1 Atuação de cada componente do grupo", "h2"),
        P("O quadro abaixo descreve a participação de cada integrante nas <b>oito etapas</b> "
          "da especificação. Como no trabalho anterior, o trabalho foi dividido por módulo, "
          "mas as decisões de projeto, a revisão do código e a revisão final do relatório "
          "foram discutidas pelos três — e qualquer integrante pode responder por qualquer "
          "seção. A numeração das etapas segue a da especificação: 1 e 2 são a biblioteca de "
          "árvores e a adaptação do aplicativo; 3 é a descrição do desenvolvimento; 4 e 5 "
          "são a análise matemática e a análise empírica da árvore binária; 6 é a "
          "implementação da AVL; 7 é a avaliação da AVL; e 8 é a pesquisa sobre a biblioteca "
          "padrão de Java."),
        tabela([
            ["Integrante", "Etapas", "Atuação"],
            ["Lucas Ramos Pianissola", "1, 4 e 6",
             "<b>Etapa 1</b> — a biblioteca de árvores: classes "
             + C("NoArvore") + " e " + C("ArvoreBinaria") + " (especializando "
             + C("ArvoreBinariaBase") + "), com os métodos " + C("adicionar") + ", "
             + C("pesquisar") + ", " + C("remover") + ", " + C("quantidadeNos") + ", "
             + C("altura") + ", " + C("caminharEmNivel") + " e " + C("caminharEmOrdem") +
             ". <b>Etapa 6</b> — classe " + C("ArvoreAVL") + ", com as quatro rotações e o "
             "rebalanceamento da inserção e da remoção. Suítes de testes "
             + C("app.TesteArvore") + " e " + C("app.TesteAVL") + ". <b>Etapa 4</b> — análise "
             "matemática da árvore binária e da AVL (<b>redação das seções 2 e 4</b>), que "
             "decorre diretamente do código que implementou."],
            ["Ryan Lima Peçanha", "2, 3 e 8",
             "<b>Etapa 2</b> — adaptação do aplicativo: o menu inicial passou a oferecer "
             "lista não-ordenada, lista ordenada, árvore binária de busca ou AVL, mantendo o "
             "restante do programa inalterado graças à interface " + C("IColecao") + "; "
             "correção da alteração de contato para impedir telefones duplicados. "
             "<b>Etapa 8</b> — pesquisa sobre árvores binárias na biblioteca padrão de Java "
             "e <b>redação da seção 6</b>. <b>Etapa 3</b> — <b>redação da seção 1</b> deste "
             "relatório (descrição do desenvolvimento, uso de ferramentas de IA e "
             "repositório) e organização do repositório no GitHub."],
            ["Davi Alvarenga", "5 e 7",
             "Infraestrutura das medições: adaptação do " + C("GeradorArquivo") +
             " para os três modos de geração, " + C("Benchmark") + " e "
             + C("ContagemOperacoes") + " (incluindo o " + C("ComparadorContador") + "). "
             "<b>Etapa 5</b> — execução de todas as rodadas de medição da árvore binária, "
             "gráficos e tabelas, e <b>redação da seção 3</b>. <b>Etapa 7</b> — as mesmas "
             "medições com a AVL e <b>redação da seção 5</b> (comparação AVL × árvore "
             "comum)."],
        ], [3.1 * cm, 2.3 * cm, 9.1 * cm]),
        Spacer(1, 10),

        P("1.2 Como as ferramentas de IA foram utilizadas", "h2"),
        P("Seguimos a mesma prática do trabalho anterior, usando uma ferramenta de IA "
          "generativa (Claude, da Anthropic) como apoio em frentes bem delimitadas."),
        P("<b>a) Aproveitamento do material da disciplina.</b> Fornecemos à ferramenta os "
          "slides de árvores da disciplina, os exemplos em C disponibilizados pelo professor "
          "(" + C("arvBin.c") + ") e a classe " + C("ArvoreBinariaBase") + " do repositório "
          "da disciplina. A ferramenta nos ajudou a transpor para Java, com <i>Generics</i> e "
          + C("Comparator") + ", a lógica de inserção, busca e remoção vista em aula — "
          "inclusive a estratégia de remoção de nó com dois filhos por <b>predecessor</b> "
          "(o maior elemento da subárvore esquerda), que é a mesma usada no exemplo em C."),
        P("<b>b) Discussão das decisões de implementação.</b> A principal delas foi "
          "<b>escrever todos os percursos de forma iterativa</b>, e não recursiva. Os "
          "exemplos em C são recursivos, o que é natural em árvores; mas como este trabalho "
          "exige inserir centenas de milhares de elementos em uma árvore <b>degenerada</b> "
          "(altura n−1), a recursão estouraria a pilha da JVM com "
          + C("StackOverflowError") + ". Discutimos a alternativa com a ferramenta, "
          "implementamos a versão iterativa e confirmamos com um teste que monta uma árvore "
          "degenerada de 100.000 nós e a percorre inteira sem estourar a pilha."),
        P("<b>A AVL, por outro lado, é recursiva</b> — e essa diferença é deliberada. A "
          "inserção e a remoção da AVL precisam executar, <i>na volta</i> de cada nível, a "
          "atualização da altura e o rebalanceamento, o que a recursão oferece de graça: cada "
          "chamada devolve a nova raiz da sua subárvore, no estilo das funções "
          + C("inserirV2") + " e " + C("removerV2") + " vistas em aula. Fazer isso de forma "
          "iterativa exigiria manter uma pilha explícita do caminho percorrido. O risco de "
          "estouro de pilha que nos obrigou a ser iterativos na árvore comum simplesmente não "
          "existe aqui: a AVL <b>garante</b> altura O(log n), que para 200.000 elementos são "
          "cerca de 25 níveis de recursão no limite teórico (e 17 medidos), contra os 199.999 "
          "da árvore degenerada."),
        P("<b>c) Infraestrutura de medição e relatório.</b> Os programas geradores de "
          "arquivos, as classes de medição e os scripts Python que produzem os gráficos e "
          "este PDF foram escritos com apoio da ferramenta, a partir dos dados das nossas "
          "execuções. Todos os números apresentados são medições nossas."),
        P("<b>d) Revisão de texto.</b> A redação final foi revisada com apoio da ferramenta, "
          "para clareza e correção da linguagem."),

        P("1.3 Repositório e organização do código", "h2"),
        P(f"Todo o código está disponível em <b>{REPO}</b>, com um "
          + C("README.md") + " descrevendo a organização das pastas e como compilar e "
          "executar o projeto."),
        tabela([
            ["Pasta / arquivo", "Conteúdo"],
            ["src/colecao/IColecao.java", "Interface comum a listas e árvores (do professor)."],
            ["src/colecao/ListaEncadeada.java",
             "A biblioteca de listas do Trabalho 1, reaproveitada sem alterações."],
            ["src/arvorebinaria/ArvoreBinariaBase.java",
             "Classe abstrata fornecida pelo professor, preservada como recebida."],
            ["src/arvorebinaria/NoArvore.java",
             "Nó da árvore: valor do tipo T e as referências esquerda e direita."],
            ["src/arvorebinaria/ArvoreBinaria.java",
             "<b>A biblioteca de árvores</b>: especializa " + C("ArvoreBinariaBase") +
             ". Não imprime nada."],
            ["src/arvorebinaria/ArvoreAVL.java",
             "<b>A árvore AVL</b>: herda de " + C("ArvoreBinaria") + " e sobrescreve "
             + C("adicionar") + " e " + C("remover") + " para rebalancear."],
            ["src/app/Programa.java",
             "A agenda: pergunta qual estrutura usar (lista não-ordenada, lista ordenada, "
             "árvore binária ou árvore AVL)."],
            ["src/app/GeradorArquivo.java",
             "Gera os arquivos de entrada em ordem crescente, balanceada ou aleatória."],
            ["src/app/Benchmark.java", "Uma rodada de medição de tempo; imprime uma linha CSV."],
            ["src/app/ContagemOperacoes.java", "Conta comparações em vez de medir tempo."],
            ["src/app/TesteArvore.java", "Testes automatizados da árvore binária (30 verificações)."],
            ["src/app/TesteAVL.java",
             "Testes da AVL: as quatro rotações, entrada crescente, remoções e 20.000 "
             "operações aleatórias verificando a propriedade AVL."],
            ["analise/ e dados/", "Scripts dos gráficos e deste PDF; CSVs com as medições."],
        ], [5.4 * cm, 9.2 * cm]),
        Spacer(1, 8),
        P("<b>O que mudou no aplicativo.</b> Como a "
          + C("ArvoreBinariaBase") + " implementa " + C("IColecao") + ", a única alteração "
          "necessária no programa do Trabalho 1 foi a pergunta inicial e a criação do objeto "
          "correspondente. Todo o resto — menu, carga de arquivo, buscas, remoção, alteração "
          "e medição de tempos — continua funcionando sem modificação, porque conversa apenas "
          "com a interface. Esse é exatamente o ganho de projeto que a interface oferece."),
        codigo("src/app/Programa.java", 33, 55, "Listagem 1 — a única mudança estrutural no app"),
        PageBreak(),
    ]

    # ---------------- seção 2 ----------------
    hist += [
        P("2. Análise matemática de complexidade", "h1"),
        P("Nesta seção analisamos os métodos " + C("adicionar") + ", " + C("pesquisar")
          + ", " + C("remover") + " e " + C("quantidadeNos") + " da classe "
          + C("ArvoreBinaria") + ". A numeração das linhas é a numeração real do arquivo "
          + C(AB) + "."),
        P("<b>Premissas.</b> (i) <i>n</i> é a quantidade de nós da árvore e <i>h</i> a sua "
          "altura; (ii) atribuições, comparações, criação de um nó e desvios são operações de "
          "custo constante; (iii) a chamada " + C("comparador.compare(...)") + " é O(1); "
          "(iv) analisamos o <b>pior caso</b>."),

        P("2.1 O ponto central: a topologia manda na complexidade", "h2"),
        P("Diferentemente da lista encadeada, em uma árvore binária o custo dos quatro métodos "
          "analisados nesta seção não depende diretamente de <i>n</i>, e sim da <b>altura</b> "
          "da árvore — porque " + C("adicionar") + ", " + C("pesquisar") + " e "
          + C("remover") + " seguem um <b>único caminho da raiz até um nó</b>, e nunca "
          "visitam a árvore inteira. (Os caminhamentos e o método " + C("altura") + ", esses "
          "sim, visitam todos os nós e são O(n) em qualquer topologia.) E a altura, para um mesmo <i>n</i>, depende da <b>ordem em que os "
          "elementos foram inseridos</b>. Como visto em aula, vale a relação:"),
        mono("", """
                          n - 1  >=  h  >=  piso(log2 n)

   h = n - 1          arvore COMPLETAMENTE DEGENERADA: cada no tem um unico
                      filho; a arvore vira uma lista encadeada.
                      Ocorre quando os elementos sao inseridos em ordem
                      crescente (ou decrescente).

   h = piso(log2 n)   arvore PERFEITAMENTE BALANCEADA: todos os niveis
                      completos, exceto possivelmente o ultimo (um nivel d
                      comporta ate 2^d nos). Para n = 2^k - 1 todos os niveis
                      ficam cheios; para os demais n, o ultimo nivel fica
                      parcialmente preenchido e a altura ainda e piso(log2 n).
                      Ocorre quando se insere sempre o elemento central do
                      intervalo restante.
"""),
        P("Portanto, <b>toda operação que custa O(h) tem dois piores casos a declarar</b>: "
          "O(log n) se a árvore estiver perfeitamente balanceada e O(n) se estiver "
          "degenerada. É essa diferença que a seção 3 mede."),

        P("2.2 Método adicionar", "h2"),
        codigo(AB, 39, 68, "Listagem 2 — adicionar"),
        P("As linhas 41-43 rejeitam " + C("null") + " e a linha 44 cria o nó: custo constante. "
          "As linhas 45-49 tratam a árvore vazia, em que o novo elemento vira a raiz: também "
          "constante. O que define a complexidade é o laço das linhas 51-65: partindo da raiz, "
          "cada iteração faz <b>uma comparação</b> (linha 52) e desce um nível — para a "
          "esquerda, se o valor do nó atual for maior que o novo (linhas 53-57), ou para a "
          "direita, caso contrário (linhas 58-64). O laço termina quando encontra a posição "
          "livre onde o novo nó é pendurado."),
        P("Note que elementos de chave <b>igual</b> caem no " + C("else") + " e são inseridos "
          "à direita — a mesma convenção do exemplo em C visto em aula."),
        P("O laço desce no máximo <i>h</i> níveis, então <b>T(n) = c<sub>1</sub>·h + c<sub>2</sub></b>, ou seja, "
          "<b>O(h)</b>. Traduzindo para <i>n</i>:"),
        tabela([
            ["Topologia", "Altura", "Custo de adicionar", "Quando ocorre"],
            ["Perfeitamente balanceada", "piso(log<sub>2</sub> n)", "<b>O(log n)</b>",
             "Inserção na ordem “do meio para fora”, como no nosso arquivo balanceado."],
            ["Degenerada", "n − 1", "<b>O(n)</b>",
             "Inserção em ordem crescente ou decrescente das chaves — o caso do nosso "
             "arquivo em ordem crescente."],
        ], [3.6 * cm, 2.1 * cm, 2.6 * cm, 6.3 * cm]),
        Spacer(1, 8),
        P("<b>Consequência: custo de montar a árvore com n elementos.</b> Inserindo os "
          "<i>n</i> contatos um a um:"),
        mono("", """
  Arvore balanceada:  cada insercao custa O(log i) para i elementos ja
                      inseridos. Somando:  log1 + log2 + ... + logn  =
                      log(n!), que e  O(n log n).

  Arvore degenerada:  a i-esima insercao percorre os i-1 nos ja inseridos
                      (todos estao em uma unica "espinha"). Somando:
                      0 + 1 + ... + (n-1) = n(n-1)/2  ->  O(n^2).
                      E EXATAMENTE a mesma soma da lista ordenada do
                      Trabalho 1 - porque a estrutura e, de fato, a mesma.
"""),

        P("2.3 Método pesquisar", "h2"),
        codigo(AB, 74, 85, "Listagem 3 — pesquisar"),
        P("O método segue um único caminho a partir da raiz: a cada nó faz uma comparação "
          "(linha 78) e, pelo sinal, decide se devolve o valor (linhas 79-81), desce à "
          "esquerda ou desce à direita (linha 82). Se chega a " + C("null") + ", o elemento "
          "não existe (linha 84)."),
        P("É aqui que está a vantagem potencial da árvore sobre a lista: cada comparação "
          "<b>descarta uma subárvore inteira</b> — a busca binária que a lista encadeada não "
          "permitia, porque agora existe acesso direto aos dois filhos de cada nó. Note, "
          "porém, que o tamanho do que se descarta depende da topologia: na árvore "
          "<b>balanceada</b> cada comparação elimina cerca de metade dos nós restantes, "
          "enquanto na <b>degenerada</b> a subárvore descartada está sempre vazia e a "
          "comparação elimina apenas o próprio nó — exatamente como em uma lista."),
        P("<b>Pior caso: O(h)</b>, que ocorre quando o elemento procurado está em uma "
          "<b>folha de profundidade máxima</b> (ou quando não existe e a busca só termina ao "
          "chegar a " + C("null") + " no nível mais profundo). Em números: <b>O(log n)</b> na "
          "árvore perfeitamente balanceada e <b>O(n)</b> na degenerada — nesta última a "
          "árvore é uma lista, e a busca volta a ser linear."),
        P("Vale registrar o número exato de comparações desse pior caso, porque ele será "
          "conferido na seção 3.2.3: buscar uma folha que está no nível <i>h</i> exige "
          "visitar os <i>h</i> nós do caminho mais a própria folha, ou seja, <b>h + 1 "
          "comparações</b>. Em uma árvore degenerada construída a partir de chaves "
          "crescentes, h = n − 1 e a busca faz exatamente <b>n comparações</b>."),

        P("2.4 Método remover", "h2"),
        codigo(AB, 91, 132, "Listagem 4 — remover"),
        P("A remoção tem duas fases. A <b>primeira</b> (linhas 93-105) é uma busca igual à do "
          + C("pesquisar") + ", guardando também o nó <b>pai</b>, necessário para refazer a "
          "ligação: custo <b>O(h)</b>."),
        P("A <b>segunda</b> fase trata os três casos clássicos:"),
        tabela([
            ["Caso", "Linhas", "O que acontece", "Custo"],
            ["Nó com dois filhos", "110-120",
             "O nó recebe o valor do seu <b>predecessor</b> (o maior da subárvore esquerda, "
             "encontrado descendo sempre à direita) e passa-se a remover o nó do predecessor, "
             "que tem no máximo um filho.", "O(h)"],
            ["Nó folha", "122-129",
             C("filho") + " fica " + C("null") + " e o pai passa a apontar para "
             + C("null") + ".", "O(1)"],
            ["Nó com um filho", "122-129",
             "O pai passa a apontar diretamente para o único filho do nó removido.", "O(1)"],
        ], [2.9 * cm, 1.6 * cm, 7.6 * cm, 1.5 * cm]),
        Spacer(1, 8),
        P("A busca pelo predecessor (laço das linhas 113-116) desce sempre pela direita a "
          "partir do filho esquerdo do nó removido. É importante notar que ela <b>não</b> "
          "acrescenta outros <i>h</i> níveis ao custo: a descida até o nó e a descida até o "
          "predecessor formam um <b>único caminho que parte da raiz</b>, de modo que o total "
          "de nós visitados é no máximo <b>h + 1</b>. Somando as duas fases, "
          "<b>T(n) = c·h + c'</b>, ou seja, <b>O(h)</b> — novamente <b>O(log n)</b> em árvore "
          "balanceada e <b>O(n)</b> em árvore degenerada."),
        P("<b>Quando o pior caso ocorre.</b> Na árvore <b>balanceada</b>, ao remover um nó "
          "cujo predecessor está no último nível — ou a própria folha de profundidade máxima "
          "—, percorrendo os h+1 nós do caminho. Na árvore <b>degenerada</b> gerada por "
          "chaves crescentes há uma particularidade que vale mencionar na entrevista: como "
          "todo nó tem apenas filho direito, <b>nenhum nó tem dois filhos</b> e o caso 3 "
          "nunca chega a ser executado; o pior caso é simplesmente remover o último nó da "
          "espinha, que custa a varredura completa — O(n)."),
        P("Vale observar o contraste com a lista do Trabalho 1: lá, a religação em si era "
          "O(1) e o custo todo estava em <b>encontrar</b> o nó. Aqui vale o mesmo princípio, "
          "só que encontrar passou a custar O(h) em vez de O(n) — quando a árvore é "
          "balanceada."),

        P("2.5 Método quantidadeNos", "h2"),
        codigo(AB, 138, 141, "Listagem 5 — quantidadeNos"),
        P("Como na lista, mantemos um contador atualizado na inserção (linhas 47 e 66) e na remoção "
          "(linha 130). O método apenas o devolve: <b>T(n) = 1</b>, portanto <b>O(1)</b>, "
          "<b>independentemente da topologia</b>. Se o contador não existisse, seria preciso "
          "percorrer toda a árvore e o método seria O(n)."),

        P("2.6 Resumo e comparação com as listas do Trabalho 1", "h2"),
        tabela([
            ["Método", "Árvore\nbalanceada", "Árvore\ndegenerada", "Lista\nordenada",
             "Lista não-\nordenada"],
            ["adicionar", "O(log n)", "O(n)", "O(n)", "O(1)"],
            ["pesquisar", "O(log n)", "O(n)", "O(n)", "O(n)"],
            ["remover", "O(log n)", "O(n)", "O(n)", "O(n)"],
            ["quantidadeNos", "O(1)", "O(1)", "O(1)", "O(1)"],
            ["montar n elementos", "O(n log n)", f"O({n2})", f"O({n2})", "O(n)"],
        ], [3.2 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm]),
        Spacer(1, 8),
        P("A leitura da tabela é o resumo do trabalho: <b>a árvore binária só é melhor que a "
          "lista enquanto a sua topologia for favorável</b>. Perfeitamente balanceada, ela "
          "transforma O(n) em O(log n) nas três operações principais. Degenerada, ela "
          "<b>é</b> uma lista encadeada — com o agravante de gastar um ponteiro a mais por "
          "nó, já que o campo da esquerda fica sempre nulo."),
        P("É por isso que existem as árvores balanceadas (AVL), objeto das próximas seções "
          "deste trabalho: elas garantem h = O(log n) <b>independentemente da ordem de "
          "inserção</b>, eliminando o pior caso que medimos aqui."),
        PageBreak(),
    ]

    # ---------------- seção 3 ----------------
    tamanhos = sorted({n for (_, n) in r})
    tam_deg = tam(r, "arvore_degenerada")
    execs = max(v["execucoes"] for v in r.values())

    hist += [
        P("3. Análise empírica de complexidade", "h1"),
        P("3.1 Implementação: geração dos arquivos e definição do pior caso", "h2"),
        P("<b>Como geramos os arquivos de entrada.</b> Adaptamos o gerador do Trabalho 1 "
          "(classe " + C("app.GeradorArquivo") + ") para produzir os contatos em três ordens "
          "diferentes, controlando a topologia da árvore resultante. Cada contato tem um "
          "identificador <i>i</i>; o telefone é a <b>concatenação</b> do prefixo "
          + C("\"27\"") + " com o número " + C("900000000 + i") + " e o nome é "
          + C("\"Contato \"") + " seguido de <i>i</i> com zeros à esquerda. Para "
          "<i>i</i> = 5, por exemplo, o registro gerado é "
          + C("Contato 0000005;27900000005") + " — o nome é derivado do mesmo "
          "identificador <b>para que a ordem alfabética dos nomes seja idêntica à ordem "
          "numérica dos telefones</b>, de modo que as duas árvores (a indexada por nome e a "
          "indexada por telefone) tenham a mesma topologia controlada."),
        mono("Os dois modos de geração usados nos testes", """
  CRESCENTE  (arquivo cres_N.txt)  ->  arvore DEGENERADA
     Emite os identificadores 0, 1, 2, 3, ... em ordem.
     Cada novo elemento e maior que todos os ja inseridos, entao desce
     sempre para a direita e vira filho direito do ultimo. A arvore nao
     tem nenhum filho a esquerda: altura = n - 1.

  BALANCEADO (arquivo bal_N.txt)   ->  arvore PERFEITAMENTE BALANCEADA
     Emite o elemento do MEIO do intervalo [0, n-1]; depois o meio de cada
     metade; depois o meio de cada quarto, e assim por diante (percurso em
     largura sobre os intervalos).
     Exemplo com n = 15:  7 | 3 11 | 1 5 9 13 | 0 2 4 6 8 10 12 14
     Inserindo nessa ordem, cada elemento cai exatamente no lugar que
     completa o nivel: altura = piso(log2 n).
"""),
        P("<b>Como definimos o pior caso de busca.</b> A especificação pede uma busca pela "
          "folha mais distante da raiz, considerando a indexação por telefone. Em vez de "
          "deduzir qual elemento seria esse em cada arquivo, a própria biblioteca responde: "
          "implementamos na " + C("ArvoreBinaria") + " o método "
          + C("valorDaFolhaMaisProfunda()") + ", que faz um "
          "percurso em largura e devolve o valor do <b>último nó visitado</b> — que está "
          "necessariamente no nível mais profundo, e portanto é uma folha de profundidade "
          "máxima. Essa é, por definição, a busca com sucesso mais cara da árvore."),
        codigo(AB, 238, 256, "Listagem 6 — identificação do pior caso de busca"),
        P("O método é chamado sobre a <b>árvore indexada por telefone</b>, como a "
          "especificação determina, e o contato devolvido por ele é o <b>mesmo</b> usado nas "
          "três medições seguintes: a busca por telefone, a busca por nome e a remoção por "
          "telefone."),
        P("<b>Sobre usar uma classe de medição separada.</b> As medições são feitas pela "
          "classe " + C("app.Benchmark") + ", e não digitando as opções no menu do "
          + C("app.Programa") + ". Ela executa exatamente a mesma sequência de operações que "
          "o menu executaria, sobre <b>as mesmas bibliotecas</b> e através da <b>mesma "
          "interface</b> " + C("IColecao") + " — a única diferença é que ela dispensa a "
          "digitação e imprime os tempos já em formato CSV, o que torna viável repetir "
          "dezenas de execuções de forma automatizada e reprodutível."),
        P("<b>Metodologia das medições.</b> Para cada arquivo, a classe "
          + C("app.Benchmark") + " (i) lê o arquivo e monta as duas árvores, cronometrando o "
          "tempo total; (ii) identifica a folha mais profunda; (iii) pesquisa esse contato "
          "pelo telefone; (iv) pesquisa o mesmo contato pelo nome; (v) remove-o pelo "
          "telefone. Os tempos são medidos com " + C("System.nanoTime()") + " e cada medição "
          f"roda em uma <b>JVM nova</b>. O tempo de <b>montagem</b> é a mediana de {execs} "
          f"execuções completas. Já as três <b>operações</b> (busca por telefone, busca por "
          f"nome e remoção) são repetidas <b>5 vezes dentro de cada execução</b>, e "
          f"reportamos a mediana dessas repetições — o contato removido é reinserido após "
          f"cada medição, de modo que todas partem do mesmo estado. Isso foi necessário "
          f"porque essas operações duram de microssegundos a poucos milissegundos, faixa em "
          f"que uma medida isolada é dominada por ruído do sistema operacional e do coletor "
          f"de lixo. Ao todo, cada ponto das tabelas de operação resume 15 medições."),
        P("<b>Uma exceção a registrar.</b> A <b>lista ordenada</b>, usada apenas como termo "
          "de comparação na seção 3.2.4, foi executada <b>uma única vez</b> por tamanho, e não "
          f"{execs}, porque a montagem dessa estrutura leva vários minutos nos tamanhos "
          "maiores. Por isso os seus tempos devem ser lidos como indicativos: o valor de "
          "8,62 ms na busca com 200.000 elementos, por exemplo, é alto demais para a "
          "tendência da própria série e provavelmente reflete ruído de uma medida isolada. "
          "Isso não afeta nenhuma conclusão do trabalho, que se apoia nas árvores e na "
          "contagem de comparações."),
        P("Além do tempo, a classe " + C("app.ContagemOperacoes") + " conta o <b>número de "
          "comparações</b> executadas. Como no Trabalho 1, essa medida independe de máquina, "
          "JIT e cache, e é a evidência mais limpa da ordem de crescimento."),
        P(f"<b>Ambiente de execução:</b> {AMBIENTE}"),
        P("<b>Tamanhos usados:</b> " + ", ".join(num(n, 0) for n in tamanhos)
          + " contatos, os mesmos do Trabalho 1, em dois arquivos cada (crescente e "
          "balanceado)."),
        PageBreak(),

        P("3.2 Análise de complexidade", "h2"),
        P("<b>Altura das árvores geradas.</b> Antes dos tempos, a medida que explica todo o "
          "resto:"),
        tabela(
            [["n", "Altura — balanceada", "piso(log<sub>2</sub> n)", "Altura — degenerada", "n − 1"]] +
            [[num(n, 0),
              str(r[("arvore_balanceada", n)]["altura"]) if ("arvore_balanceada", n) in r else "—",
              str(math.floor(math.log2(n))),
              num(r[("arvore_degenerada", n)]["altura"], 0) if ("arvore_degenerada", n) in r else "—",
              num(n - 1, 0)] for n in tamanhos],
            [2.1 * cm, 3.3 * cm, 2.4 * cm, 3.4 * cm, 2.4 * cm]),
        Spacer(1, 6),
        P("Os geradores fizeram exatamente o que deveriam: a árvore do arquivo balanceado "
          "atingiu a <b>altura mínima teórica</b> piso(log<sub>2</sub> n) em todos os tamanhos, e a do "
          "arquivo crescente atingiu a <b>altura máxima</b> n−1. Com 200.000 contatos, uma "
          "árvore tem altura 17 e a outra 199.999: é essa diferença de quatro ordens de "
          "grandeza que aparece em todos os gráficos a seguir."),
        figura("fig2_altura.png",
               "Figura 1 — Altura das árvores (escala logarítmica). A curva da árvore "
               "balanceada coincide com o mínimo teórico piso(log<sub>2</sub> n)."),

        P("3.2.1 Tempo de leitura do arquivo e montagem das árvores", "h3"),
        tabela_metrica(r, "montagem", "Montagem (ms)"),
        Spacer(1, 8),
        figura("fig1_montagem_arvores.png",
               "Figura 2 — Montagem das árvores (escala logarítmica)."),
    ]

    m_bal = {n: r[("arvore_balanceada", n)]["montagem"] for n in tam(r, "arvore_balanceada")}
    m_deg = {n: r[("arvore_degenerada", n)]["montagem"] for n in tam_deg}
    maior = max(tam_deg)
    fator = m_deg[maior] / m_bal[maior]

    hist += [
        P("<b>Interpretação.</b> Na árvore <b>balanceada</b>, dobrar <i>n</i> multiplica o "
          f"tempo por valores entre {razoes_txt(r, 'arvore_balanceada', 'montagem')} — "
          "compatível com o O(n log n) previsto na seção 2.2. O fator teórico ao dobrar "
          "<i>n</i> é 2·log(2n)/log(n), que para esses tamanhos vale cerca de 2,1; as razões "
          "medidas ficam abaixo disso porque parte do tempo não cresce com <i>n</i> da mesma "
          "forma: a compilação JIT dos métodos acontece nas primeiras milhares de inserções e "
          "a abertura do arquivo tem custo próprio. Note que a inicialização da JVM <b>não</b> "
          "entra nessa conta — o cronômetro " + C("System.nanoTime()") + " só começa dentro "
          "do programa, depois que a máquina virtual já subiu."),
        P("Na árvore <b>degenerada</b>, as razões são "
          f"{razoes_txt(r, 'arvore_degenerada', 'montagem')} a cada duplicação de <i>n</i> — "
          f"a assinatura de <b>O({n2})</b>, exatamente o previsto na seção 2.2. "
          f"Com {num(maior,0)} contatos a montagem degenerada levou "
          f"<b>{num(m_deg[maior]/1000/60,1)} minutos</b>, contra "
          f"<b>{num(m_bal[maior],0)} ms</b> da balanceada: cerca de "
          f"<b>{num(fator,0)} vezes mais</b>, com o <b>mesmo número de elementos e o mesmo "
          f"código</b>. A única diferença entre as duas execuções é a ordem em que os dados "
          f"chegaram."),
        P("As razões medidas no relógio oscilam em torno de 4, ora acima, ora abaixo. Essa "
          "dispersão vem do <b>custo de cada operação</b>, não da quantidade delas: percorrer "
          "uma estrutura encadeada de centenas de milhares de nós espalhados pelo heap gera "
          "um número de faltas de cache que varia com o tamanho da estrutura e com o estado "
          "da máquina — o mesmo efeito de hierarquia de memória discutido no Trabalho 1. A "
          "medida que decide a questão é a <b>contagem de comparações</b> da seção 3.2.3, que "
          "cresce exatamente 4,00× a cada duplicação, sem exceção."),

        P("3.2.2 Tempo de pesquisa e de remoção no pior caso", "h3"),
        tabela_metrica(r, "busca_tel", "Pesquisa por telefone (ms)", casas=4),
        Spacer(1, 6),
        figura("fig3_busca_telefone.png",
               "Figura 3 — Pesquisa pelo telefone da folha mais distante da raiz."),
        tabela_metrica(r, "busca_nome", "Pesquisa por nome (ms)", casas=4),
        Spacer(1, 6),
        tabela_metrica(r, "remocao", "Remoção (ms)", casas=4),
        Spacer(1, 6),
        figura("fig5_remocao.png",
               "Figura 4 — Remoção do mesmo contato, pesquisado pelo telefone."),
        P("<b>Interpretação.</b> As três tabelas contam a mesma história, e é a prevista na "
          "seção 2. Na árvore <b>balanceada</b>, as duas buscas e a remoção custam cerca de "
          "<b>um microssegundo</b> (0,001 ms) e praticamente não crescem: entre 25.000 e "
          "200.000 contatos — oito vezes mais dados — a altura sobe apenas de 14 para 17, e é "
          "a altura que determina o custo. É o comportamento <b>O(log n)</b>: multiplicar <i>n</i> por 8 "
          "acrescenta 3 níveis à árvore, e portanto 3 comparações à busca."),
        P("Na árvore <b>degenerada</b>, as mesmas operações custam <b>milissegundos</b> — duas "
          "a três ordens de grandeza a mais — e crescem com <i>n</i>, o comportamento "
          "<b>O(n)</b>, porque percorrer a árvore degenerada é percorrer uma lista. A "
          "confirmação exata vem da contagem de operações (seção 3.2.3): a busca de pior caso "
          "faz <b>exatamente n comparações</b> na árvore degenerada e <b>h + 1</b> na "
          "balanceada."),
        P("<b>Por que as razões de tempo oscilam.</b> Em termos absolutos, essas operações "
          "duram de microssegundos (balanceada) a poucos milissegundos (degenerada) — faixa "
          "em que o relógio sofre interferência do escalonador do sistema operacional, do "
          "coletor de lixo e do estado dos caches. Mesmo com a mediana de 15 medições por "
          "ponto, algumas razões ficam abaixo de 1, ou seja, o tempo medido <b>caiu</b> ao "
          "dobrar <i>n</i>. Isso não contradiz a análise: significa apenas que, nessa escala, "
          "a variação do ruído é maior que a diferença real entre dois pontos vizinhos. A "
          "tendência entre os extremos (25.000 e 200.000) e a contagem de comparações são as "
          "evidências confiáveis, e ambas confirmam O(log n) e O(n)."),
        P("<b>Dois pontos específicos que merecem comentário.</b> Primeiro, a "
          "<b>remoção na árvore degenerada</b> é consistentemente próxima do tempo da busca "
          "pelo mesmo elemento. Isso é esperado: a remoção é uma busca seguida de um número "
          "fixo de religações de ponteiros, e nesta topologia o nó removido é o último da "
          "espinha — uma folha, portanto o caso mais barato da segunda fase, sem predecessor "
          "a procurar. Segundo, nos tamanhos menores a <b>busca por nome</b> chega a ser mais "
          "rápida que a busca por telefone na degenerada, embora as duas árvores tenham a "
          "mesma topologia e a mesma altura. O motivo é que a busca por nome roda logo depois "
          "da busca por telefone dentro de cada repetição, aproveitando o aquecimento do JIT; "
          "nos tamanhos maiores, em que o trabalho real domina o ruído, as duas praticamente "
          "se igualam, como deveria ser. É um ganho de fator constante, não de ordem."),
    ]

    if cont:
        tamanhos_c = sorted({n for (_, n) in cont})
        linhas = [["n", "Montagem —\nABB balanceada\n(soma das 2 árvores)", "razão",
                   "Montagem —\nABB degenerada\n(soma das 2 árvores)", "razão",
                   "Busca —\nABB balanceada\n(1 árvore)",
                   "Busca —\nABB degenerada\n(1 árvore)"]]
        ant_b = ant_d = None
        for n in tamanhos_c:
            cb = cont.get(("arvore_balanceada", n), {})
            cd = cont.get(("arvore_degenerada", n), {})
            rb = f"{cb['montagem']/ant_b:.2f}×".replace(".", ",") if (cb and ant_b) else "—"
            rd = f"{cd['montagem']/ant_d:.2f}×".replace(".", ",") if (cd and ant_d) else "—"
            linhas.append([
                num(n, 0),
                num(cb["montagem"], 0) if cb else "—", rb,
                num(cd["montagem"], 0) if cd else "não medido", rd,
                num(cb["busca"], 0) if cb else "—",
                num(cd["busca"], 0) if cd else "—",
            ])
            if cb:
                ant_b = cb["montagem"]
            if cd:
                ant_d = cd["montagem"]
        hist += [
            P("3.2.3 Contagem de operações", "h3"),
            P("A tabela mostra quantas <b>comparações entre contatos</b> foram efetivamente "
              "executadas para montar as duas árvores (soma das duas) e para fazer a busca "
              "de pior caso."),
            KeepTogether([tabela(linhas, [1.6 * cm, 3.0 * cm, 1.4 * cm, 3.0 * cm, 1.4 * cm,
                                          2.1 * cm, 2.1 * cm])]),
            Spacer(1, 8),
            P("Os números confirmam a análise matemática com precisão. Na árvore "
              "<b>degenerada</b> a contagem é multiplicada por <b>4,00</b> a cada duplicação "
              f"de <i>n</i> — a assinatura de {n2} —, e mais do que isso: ela bate "
              "<b>exatamente</b> com a fórmula deduzida na seção 2.2. Lá chegamos a "
              "n(n−1)/2 comparações por árvore; como montamos duas árvores, o total previsto "
              "é n(n−1). Para n = 25.000 isso dá 624.975.000, e foi exatamente esse o valor "
              "medido — até a última unidade. O mesmo vale para os demais tamanhos."),
            P("Na árvore <b>balanceada</b> a contagem cresce por pouco mais de <b>2</b> a "
              "cada duplicação: é o comportamento n·log n, em que dobrar <i>n</i> dobra o "
              "número de inserções e ainda acrescenta um nível a cada uma. E a busca de pior "
              "caso confirma a previsão da seção 2.3 nos dois extremos: na balanceada ela faz "
              "<b>h + 1</b> comparações (15, 16, 17 e 18 para alturas 14, 15, 16 e 17), e na "
              "degenerada faz <b>exatamente n</b> comparações — o pior caso linear "
              "acontecendo literalmente."),
        ]

    # comparação com listas
    estruturas_lista = [e for e in ("lista_nao_ordenada", "lista_ordenada")
                        if any(k[0] == e for k in r)]
    if estruturas_lista:
        tamanhos_l = sorted({n for (e, n) in r if e in estruturas_lista})
        linhas = [["n", "Árvore\nbalanceada", "Árvore\ndegenerada", "Lista\nnão-ordenada",
                   "Lista\nordenada"]]
        for n in tamanhos:
            def v(est, campo="montagem"):
                return num(r[(est, n)][campo], 1) if (est, n) in r else "—"
            linhas.append([num(n, 0), v("arvore_balanceada"), v("arvore_degenerada"),
                           v("lista_nao_ordenada"), v("lista_ordenada")])
        linhas_busca = [["n", "Árvore\nbalanceada", "Árvore\ndegenerada", "Lista\nnão-ordenada",
                         "Lista\nordenada"]]
        for n in tamanhos:
            def vb(est):
                return num(r[(est, n)]["busca_tel"], 4) if (est, n) in r else "—"
            linhas_busca.append([num(n, 0), vb("arvore_balanceada"), vb("arvore_degenerada"),
                                 vb("lista_nao_ordenada"), vb("lista_ordenada")])
        hist += [
            P("3.2.4 Comparação com as listas do Trabalho 1", "h3"),
            P("Para que a comparação fosse justa, rodamos também as listas encadeadas do "
              "Trabalho 1 <b>na mesma máquina e com os mesmos arquivos</b>. Tempos de "
              "montagem, em milissegundos:"),
            KeepTogether([tabela(linhas, [2.0 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm])]),
            Spacer(1, 8),
            P("Tempos de pesquisa no pior caso, em milissegundos:"),
            KeepTogether([tabela(linhas_busca, [2.0 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm,
                                                3.1 * cm])]),
            Spacer(1, 8),
            figura("fig7_busca_comparacao.png",
                   "Figura 5 — Pesquisa no pior caso: as quatro estruturas (escala "
                   "logarítmica)."),
            P("<b>O que a comparação mostra.</b> Para a <b>busca</b>, a árvore balanceada é "
              "disparadamente a melhor estrutura: ela resolve em microssegundos o que as "
              "listas resolvem em milissegundos, e a vantagem <b>aumenta</b> com <i>n</i>, "
              "porque O(log n) e O(n) divergem. A árvore degenerada, por sua vez, tem "
              "desempenho equivalente ao da lista — o que era de se esperar, já que ela "
              "<b>é</b> uma lista encadeada com um ponteiro desperdiçado por nó."),
            P("Para a <b>montagem</b>, a lista não-ordenada continua imbatível (O(n), com "
              "inserção O(1) no fim graças à referência " + C("ult") + "), mas ela paga esse "
              "preço em toda busca posterior. A árvore balanceada monta em O(n log n) — mais "
              "caro que a lista não-ordenada e muito mais barato que a lista ordenada ou que "
              "a árvore degenerada, ambas quadráticas."),
            P("Duas observações sobre a leitura dessas tabelas. A primeira é que as medidas da "
              "<b>lista não-ordenada</b> na busca também oscilam entre tamanhos vizinhos, pelo "
              "mesmo motivo já discutido na seção 3.2.2 — são poucos milissegundos, e o ruído "
              "de medição é da mesma ordem da diferença entre dois pontos. A tendência entre "
              "os extremos, no entanto, é claramente linear, como manda o O(n) da busca pelo "
              "último nó. A segunda é que a <b>lista ordenada</b> foi medida com o arquivo "
              "balanceado, e não com o crescente: montar uma lista ordenada a partir de "
              "chaves em ordem crescente é o pior caso absoluto dessa estrutura (cada "
              "inserção percorre a lista inteira), e o tempo seria ainda maior que o já "
              "medido — o que não acrescentaria nada à comparação, já que o ponto é o mesmo "
              "da árvore degenerada."),
            P("A conclusão prática é que <b>a escolha da estrutura depende do perfil de uso</b>: "
              "se os dados são inseridos uma vez e consultados muitas, a árvore balanceada "
              "compensa largamente o custo de montagem. Mas essa conclusão tem uma condição "
              "embutida — que a árvore <b>esteja</b> balanceada —, e nada no código garante "
              "isso: basta o arquivo chegar ordenado para cairmos no pior caso."),
        ]

    hist += [
        P("3.3 Conclusão da análise da árvore binária", "h2"),
        P("Os dados coletados <b>atendem ao esperado</b> pela análise matemática da seção 2:"),
        P("• as alturas medidas bateram exatamente com os limites teóricos — piso(log<sub>2</sub> n) na "
          "árvore gerada pelo arquivo balanceado e n−1 na gerada pelo arquivo crescente;<br/>"
          "• a <b>montagem</b> da árvore balanceada cresceu como O(n log n) e a da degenerada "
          f"como O({n2}), com a contagem de comparações quadruplicando a cada duplicação de "
          "<i>n</i>;<br/>"
          "• <b>pesquisa</b> e <b>remoção</b> no pior caso ficaram em microssegundos na "
          "árvore balanceada e em milissegundos na degenerada — diferença de duas a três "
          "ordens de grandeza —, e a contagem de comparações confirmou O(log n) e O(n) com "
          "exatidão (h+1 e n comparações, respectivamente), ainda que os tempos de relógio "
          "oscilem entre tamanhos vizinhos por serem medidas muito curtas;<br/>"
          "• " + C("quantidadeNos") + " é O(1) nas duas topologias e seu tempo é "
          "indistinguível de zero, por isso não foi incluído nos gráficos."),
        P("A lição central desta etapa é que, em uma árvore binária de busca <b>sem "
          "balanceamento</b>, a complexidade não é uma propriedade do algoritmo isoladamente: "
          "ela depende da <b>ordem em que os dados chegam</b>. O mesmo código, com os mesmos "
          "200.000 contatos, foi de 17 níveis para 199.999 e de milissegundos para minutos. "
          "Em um sistema real, dados costumam chegar ordenados (por data de cadastro, por "
          "matrícula, por código sequencial), que é justamente o pior caso."),
        P("É exatamente esse problema que as <b>árvores AVL</b> resolvem, reequilibrando a "
          "árvore após cada inserção e remoção para garantir h = O(log n) em qualquer ordem "
          "de entrada. É o que analisamos na seção 4 e medimos na seção 5."),
        PageBreak(),
    ]


    # ================================================================
    # SEÇÃO 4 — ÁRVORE AVL
    # ================================================================
    hist += [
        P("4. Árvore AVL: implementação e análise de complexidade", "h1"),
        P("A seção anterior terminou com um problema concreto: a árvore binária de busca só "
          "entrega O(log n) <b>se</b> a ordem de chegada dos dados colaborar, e a ordem mais "
          "comum em sistemas reais — chaves sequenciais — é justamente a pior possível. A "
          "árvore <b>AVL</b> (de Adelson-Velsky e Landis) resolve isso verificando o "
          "equilíbrio após cada inserção e cada remoção e corrigindo-o imediatamente, de modo "
          "que a altura permaneça O(log n) <b>para qualquer ordem de entrada</b>."),

        P("4.1 O critério de equilíbrio", "h2"),
        P("Para cada nó define-se o <b>fator de balanceamento</b>:"),
        mono("", """
        fb(no) = altura(subarvore esquerda) - altura(subarvore direita)

   Uma arvore e AVL quando |fb| <= 1 em TODOS os nos, ou seja, as duas
   subarvores de qualquer no diferem em no maximo um nivel de altura.

   Consequencia (limite classico da AVL):

        h  <  1,4404 * log2(n + 2) - 0,3277

   isto e, a altura de uma AVL nunca passa de cerca de 44% A MAIS que a
   altura minima teorica piso(log2 n). Ela nao e perfeitamente balanceada, mas e
   garantidamente O(log n) - que e o que importa para a complexidade.
"""),
        P("Na nossa implementação, cada nó guarda a sua própria altura (campo "
          + C("altura") + " de " + C("NoArvore") + ", folha = 0) e o fator de balanceamento é "
          "derivado dela. É a mesma informação do campo " + C("fb") + " dos exemplos em C "
          "vistos em aula, apenas armazenada de outra forma: guardar a altura torna a "
          "atualização trivial tanto na inserção quanto na remoção, enquanto manter o "
          + C("fb") + " diretamente exige propagar sinalizadores de “cresceu/diminuiu” "
          "subindo pela recursão."),
        codigo(AVL, 127, 142, "Listagem 7 — altura do nó e fator de balanceamento"),

        P("4.2 As quatro rotações", "h2"),
        P("Quando um nó fica com |fb| = 2, o equilíbrio é restaurado por uma ou duas "
          "<b>rotações</b> — operações que reorganizam três nós e no máximo quatro "
          "subárvores, preservando a propriedade de árvore de busca. Cada rotação mexe em um "
          "número <b>fixo</b> de ponteiros: é O(1)."),
        mono("Os quatro casos", r"""
  CASO ESQUERDA-ESQUERDA (fb do no = +2, fb do filho esquerdo >= 0)
     rotacao simples a DIREITA

          30                        20
         /                         /  \
        20          ==>           10    30
       /
      10

  CASO DIREITA-DIREITA (fb do no = -2, fb do filho direito <= 0)
     rotacao simples a ESQUERDA  -- e o caso da nossa entrada crescente

      10                            20
        \                          /  \
         20        ==>            10    30
           \
            30

  CASO ESQUERDA-DIREITA (fb do no = +2, fb do filho esquerdo < 0)
     rotacao dupla: primeiro a ESQUERDA no filho, depois a DIREITA no no

          30            30             20
         /             /              /  \
        10    ==>     20     ==>    10    30
          \          /
           20       10

  CASO DIREITA-ESQUERDA (fb do no = -2, fb do filho direito > 0)
     rotacao dupla: primeiro a DIREITA no filho, depois a ESQUERDA no no

      10              10                  20
        \               \                /  \
         30    ==>        20     ==>    10    30
        /                   \
      20                      30
"""),
        codigo(AVL, 144, 165, "Listagem 8 — escolha da rotação"),
        P("O método " + C("balancear") + " é chamado em <b>todo</b> nó do caminho de volta da "
          "recursão, tanto na inserção quanto na remoção. Ele olha o fator de balanceamento e, "
          "se |fb| ≤ 1, devolve o nó sem tocar em nada (linha 164); caso contrário aplica a "
          "rotação simples ou a dupla, conforme o sinal do fb do filho."),
        codigo(AVL, 177, 184, "Listagem 9 — rotação simples à direita"),
        P("A rotação é apenas um religamento de ponteiros seguido da atualização das duas "
          "alturas afetadas: cinco operações, nenhuma delas dependente de <i>n</i>. <b>Toda "
          "rotação é O(1)</b> — esse é o ponto que sustenta a análise a seguir."),

        P("4.3 Método adicionar", "h2"),
        codigo(AVL, 43, 64, "Listagem 10 — adicionar na AVL"),
        P("A inserção tem duas fases. A <b>descida</b> (linhas 57-61) é idêntica à da árvore "
          "binária comum: compara e desce para um dos lados até encontrar o lugar do novo nó. "
          "A <b>volta da recursão</b> (linhas 62-63) é a novidade: ao retornar de cada nível, "
          "a altura do nó é atualizada e o nó é rebalanceado."),
        P("<b>Custo.</b> A descida percorre <i>h</i> níveis. Na volta, cada um dos <i>h</i> "
          "níveis executa " + C("atualizarAltura") + " e " + C("balancear") + ", ambos O(1). "
          "Logo <b>T(n) = c·h</b>, ou seja, <b>O(h)</b>. Como a AVL garante h = O(log n), a "
          "inserção é <b>O(log n) no pior caso</b> — e, diferentemente da árvore binária "
          "comum, <b>não existe ordem de entrada capaz de piorar isso</b>."),
        P("<b>Quantas rotações a inserção faz?</b> No máximo <b>uma</b> rotação simples ou "
          "<b>uma</b> dupla, e depois dela nenhum ancestral precisa de correção. O motivo é "
          "que a rotação devolve à subárvore a mesma altura que ela tinha antes da inserção, "
          "de modo que os nós acima deixam de enxergar qualquer mudança. Por isso o "
          "rebalanceamento acrescenta apenas uma constante ao custo: O(log n) para descer, "
          "O(1) para corrigir."),
        P("<b>Comparando com a árvore binária comum:</b> no melhor caso (entrada balanceada) "
          "as duas são O(log n) e a AVL é um pouco mais lenta, porque paga a atualização de "
          "altura em cada nível. No <b>pior caso</b>, porém, a árvore comum vai a O(n) e a "
          "AVL permanece em O(log n). Montar <i>n</i> elementos custa <b>O(n log n)</b> na "
          f"AVL contra <b>O({n2})</b> na árvore comum degenerada."),

        P("4.4 Método remover", "h2"),
        codigo(AVL, 70, 111, "Listagem 11 — remover na AVL"),
        P("A remoção segue a mesma estrutura da árvore binária comum — busca o nó (linhas "
          "84-88) e trata os três casos: folha ou nó com um único filho (linhas 91-96) e nó "
          "com dois filhos, resolvido pelo <b>predecessor</b>, o maior elemento da subárvore "
          "esquerda (linhas 98-107) — e acrescenta, na volta da recursão, a mesma dupla "
          + C("atualizarAltura") + " + " + C("balancear") + " (linhas 109-110)."),
        P("Note o método auxiliar " + C("removerPredecessor") + ": ele desce pela direita até "
          "o último nó e também rebalanceia na volta. Isso é necessário porque a remoção do "
          "predecessor pode desequilibrar os nós daquele caminho."),
        P("<b>Custo.</b> Busca O(h), remoção propriamente dita O(1), rebalanceamento O(1) por "
          "nível em um caminho de <i>h</i> níveis: <b>O(h) = O(log n)</b> no pior caso."),
        P("<b>Uma diferença importante em relação à inserção:</b> enquanto a inserção precisa "
          "de no máximo uma rotação, a remoção pode precisar de <b>até h rotações</b> — uma "
          "em cada nível do caminho de volta. Isso acontece porque uma rotação que reequilibra "
          "uma subárvore pode <b>reduzir</b> a altura dela, e essa redução propaga o "
          "desequilíbrio para o pai, e assim por diante até a raiz. Mesmo no pior caso, "
          "porém, são O(log n) rotações de O(1) cada, e o custo total da remoção continua "
          "<b>O(log n)</b>."),
        P("Esse detalhe costuma ser cobrado em prova: <b>inserção = no máximo 1 rotação; "
          "remoção = até O(log n) rotações</b>; as duas operações, ainda assim, O(log n)."),

        P("4.5 Resumo da seção", "h2"),
        tabela([
            ["Método", "Árvore binária\n(pior caso)", "AVL\n(pior caso)", "Comentário"],
            ["adicionar", "O(n)", "<b>O(log n)</b>",
             "A AVL paga O(1) de rebalanceamento por nível e, em troca, elimina o pior caso."],
            ["pesquisar", "O(n)", "<b>O(log n)</b>",
             "Herdado sem alteração: a AVL continua sendo uma árvore de busca; o que muda é a "
             "altura garantida."],
            ["remover", "O(n)", "<b>O(log n)</b>",
             "Até O(log n) rotações, cada uma O(1)."],
            ["quantidadeNos", "O(1)", "O(1)", "Contador mantido nas duas classes."],
            ["montar n elementos", f"O({n2})", "<b>O(n log n)</b>",
             "Independentemente da ordem de chegada dos dados."],
        ], [2.7 * cm, 2.7 * cm, 2.4 * cm, 6.8 * cm]),
        Spacer(1, 8),
        P("O preço do equilíbrio é um campo a mais por nó (a altura) e algumas operações "
          "constantes por nível. O benefício é eliminar completamente a dependência da ordem "
          "de entrada — que, como a seção 3 mostrou, pode custar minutos em vez de "
          "milissegundos."),
        PageBreak(),
    ]


    # ================================================================
    # SEÇÃO 5 — DESEMPENHO DA AVL
    # ================================================================
    tem_avl = any(k[0] == "avl_crescente" for k in r)
    if tem_avl:
        tam_avl = tam(r, "avl_crescente")
        m_avl = {n: r[("avl_crescente", n)]["montagem"] for n in tam_avl}
        maior_avl = max(tam_avl)
        ganho = m_deg[maior_avl] / m_avl[maior_avl] if maior_avl in m_deg else None

        linhas_mont = [["n", "AVL\n(entrada crescente)", "razão",
                        "Árvore binária\n(entrada crescente)", "razão", "ganho"]]
        ant_a = ant_d = None
        for n in tam_avl:
            va = m_avl.get(n)
            vd = m_deg.get(n)
            ra = f"{va/ant_a:.2f}×".replace(".", ",") if (va and ant_a) else "—"
            rd = f"{vd/ant_d:.2f}×".replace(".", ",") if (vd and ant_d) else "—"
            g = f"{vd/va:,.0f}×".replace(",", ".") if (va and vd) else "—"
            linhas_mont.append([num(n, 0), num(va, 2), ra, num(vd, 2), rd, g])
            ant_a, ant_d = va or ant_a, vd or ant_d

        linhas_alt = [["n", "Altura — AVL", "Altura — árvore binária",
                       "piso(log<sub>2</sub> n)", "n − 1"]]
        for n in tam_avl:
            linhas_alt.append([
                num(n, 0),
                str(r[("avl_crescente", n)]["altura"]),
                num(r[("arvore_degenerada", n)]["altura"], 0)
                if ("arvore_degenerada", n) in r else "—",
                str(math.floor(math.log2(n))),
                num(n - 1, 0)])

        linhas_op = [["n", "AVL — pesquisa\npor telefone (ms)",
                      "AVL — pesquisa\npor nome (ms)", "AVL — remoção (ms)",
                      "Árvore binária —\npesquisa (ms)",
                      "Árvore binária —\nremoção (ms)"]]
        for n in tam_avl:
            def va(campo, est="avl_crescente"):
                return num(r[(est, n)][campo], 4) if (est, n) in r else "—"
            linhas_op.append([num(n, 0), va("busca_tel"), va("busca_nome"), va("remocao"),
                              va("busca_tel", "arvore_degenerada"),
                              va("remocao", "arvore_degenerada")])

        linhas_cont_avl = [["n", "Comparações — AVL\n(soma das 2 árvores)", "razão",
                            "Comparações — ABB\n(soma das 2 árvores)", "razão",
                            "Busca — AVL\n(1 árvore)"]]
        ant_a = ant_d = None
        for n in sorted({x for (e, x) in cont if e == "avl_crescente"}):
            ca = cont.get(("avl_crescente", n), {})
            cd = cont.get(("arvore_degenerada", n), {})
            ra = f"{ca['montagem']/ant_a:.2f}×".replace(".", ",") if (ca and ant_a) else "—"
            rd = f"{cd['montagem']/ant_d:.2f}×".replace(".", ",") if (cd and ant_d) else "—"
            linhas_cont_avl.append([
                num(n, 0),
                num(ca["montagem"], 0) if ca else "—", ra,
                num(cd["montagem"], 0) if cd else "não medido", rd,
                num(ca["busca"], 0) if ca else "—"])
            if ca:
                ant_a = ca["montagem"]
            if cd:
                ant_d = cd["montagem"]

        hist += [
            P("5. Desempenho da AVL comparado ao da árvore binária comum", "h1"),
            P("Esta seção repete exatamente as medições da seção 3, porém instanciando "
              "<b>árvores AVL</b> e usando <b>os mesmos arquivos em ordem crescente</b> — "
              "aqueles que, na árvore binária comum, produzem a árvore completamente "
              "degenerada. A metodologia, a máquina e o critério de pior caso são os mesmos "
              "descritos na seção 3.1: a busca é feita pela folha mais distante da raiz na "
              "árvore indexada por telefone, e o mesmo contato é usado nas três operações."),

            P("5.1 Altura: o efeito do balanceamento", "h2"),
            P("A medida que explica todo o resto. Com a <b>mesma entrada</b>:"),
            tabela(linhas_alt, [2.2 * cm, 2.7 * cm, 3.7 * cm, 3.0 * cm, 2.9 * cm]),
            Spacer(1, 6),
            figura("fig10_avl_altura.png",
                   "Figura 6 — Altura com a mesma entrada crescente (escala logarítmica). "
                   "A AVL coincide com o mínimo teórico; a árvore binária comum vai a n−1."),
            P("O rebalanceamento funcionou exatamente como a teoria prevê. Com 200.000 "
              "contatos em ordem crescente, a árvore binária comum chega a <b>199.999</b> "
              "níveis e a AVL fica em <b>17</b> — que é o próprio piso(log<sub>2</sub> n), o "
              "mínimo teórico possível para essa quantidade de nós. Vale notar que a AVL não "
              "<i>garante</i> atingir o mínimo (o limite da seção 4.1 permite até cerca de "
              "44% a mais), mas para uma entrada crescente ela acaba produzindo exatamente a "
              "árvore mais rasa possível."),

            P("5.2 Tempo de montagem", "h2"),
            tabela(linhas_mont, [1.8 * cm, 2.9 * cm, 1.5 * cm, 3.0 * cm, 1.5 * cm, 1.9 * cm]),
            Spacer(1, 6),
            figura("fig8_avl_montagem.png",
                   "Figura 7 — Montagem com a mesma entrada crescente (escala logarítmica)."),
            P("As razões da AVL são "
              f"{razoes_txt(r, 'avl_crescente', 'montagem')} a cada duplicação de <i>n</i> — "
              "próximas do fator teórico de O(n log n), que para esses tamanhos é pouco "
              "acima de 2, e abaixo dele pelos mesmos custos fixos discutidos na seção 3.2.1 "
              "(compilação JIT e leitura do arquivo pesam proporcionalmente mais nas entradas "
              "menores). Já a árvore binária comum, com a <b>mesma</b> entrada, apresenta "
              f"razões {razoes_txt(r, 'arvore_degenerada', 'montagem')} — oscilando em torno "
              f"de 4, o <b>O({n2})</b> da seção 3."),
        ]
        if ganho:
            hist += [
                P(f"Em números absolutos: com {num(maior_avl,0)} contatos em ordem crescente, "
                  f"a AVL montou as duas árvores em <b>{num(m_avl[maior_avl],0)} ms</b>, "
                  f"contra <b>{num(m_deg[maior_avl]/1000/60,1)} minutos</b> da árvore binária "
                  f"comum: um ganho de cerca de <b>{num(ganho,0)} vezes</b>. E, como a "
                  f"diferença entre O(n log n) e O({n2}) cresce com <i>n</i>, esse fator "
                  f"<b>aumenta</b> conforme a base de dados cresce."),
            ]
        hist += [
            P("5.3 Contagem de operações", "h2"),
            P("Como nas seções anteriores, a contagem de comparações é a evidência livre de "
              "ruído. Aqui ela permite comparar, com a <b>mesma entrada crescente</b>, "
              "quantas comparações cada estrutura executa:"),
            KeepTogether([tabela(linhas_cont_avl,
                                 [1.9 * cm, 3.5 * cm, 1.5 * cm, 3.6 * cm, 1.5 * cm,
                                  2.6 * cm])]),
            Spacer(1, 8),
            P("A leitura é direta: com 200.000 contatos em ordem crescente, a AVL executa "
              "cerca de <b>6,7 milhões</b> de comparações para montar as duas árvores, contra "
              "<b>40 bilhões</b> da árvore binária comum — uma diferença de quase quatro "
              "ordens de grandeza, e que cresce com <i>n</i>. As razões confirmam as ordens "
              "previstas: a AVL pouco mais que dobra a cada duplicação de <i>n</i> "
              "(n·log n) e a árvore comum quadruplica (n<super>2</super>)."),
            P("Vale notar também a comparação entre a AVL montada a partir da entrada "
              "<b>crescente</b> e a árvore binária <b>balanceada</b> da seção 3: para "
              "200.000 elementos, 6.675.714 comparações contra 6.275.750, ou seja, a AVL faz "
              "de <b>6% a 8% mais comparações</b> (7,9% em 25.000 e 6,4% em 200.000). A "
              "diferença não é o custo das rotações em si — uma rotação religa ponteiros e "
              "<b>não chama o comparador</b> — mas o fato de a árvore produzida pelas "
              "rotações não ser exatamente a mesma árvore perfeitamente balanceada: alguns "
              "elementos acabam um nível mais abaixo, e cada nível extra é uma comparação a "
              "mais na inserção dos elementos seguintes."),
            P("A contraprova está em contar as comparações da AVL com o arquivo <b>já "
              "balanceado</b>: 634.496, 1.368.962, 2.937.892 e 6.275.750 — valores "
              "<b>idênticos</b>, dígito a dígito, aos da árvore binária comum com o mesmo "
              "arquivo. Quando a entrada já chega equilibrada, nenhuma rotação é disparada e "
              "a AVL executa exatamente a mesma sequência de comparações. Isso isola o custo "
              "do balanceamento: em número de comparações ele é <b>zero</b>; em tempo, como "
              "se verá na seção 5.5, ele é de 12% a 16%, e vem inteiramente das atualizações "
              "de altura e das verificações de fator de balanceamento, que não são "
              "comparações."),
            P("5.4 Tempo de pesquisa e de remoção no pior caso", "h2"),
            tabela(linhas_op, [1.6 * cm, 2.6 * cm, 2.4 * cm, 2.4 * cm, 2.7 * cm,
                               2.8 * cm]),
            Spacer(1, 6),
            figura("fig9_avl_busca.png",
                   "Figura 8 — Pesquisa no pior caso (escala logarítmica). A AVL construída a "
                   "partir da entrada crescente acompanha a árvore binária balanceada."),
            P("Na AVL, as três operações — busca pelo telefone da folha mais distante da "
              "raiz, busca do <b>mesmo contato pelo nome</b> na segunda árvore e remoção "
              "desse contato — custam <b>cerca de um microssegundo</b> e praticamente não "
              "crescem com <i>n</i>: o mesmo patamar da árvore binária <b>balanceada</b> "
              "medida na seção 3, e o esperado para O(log n). A busca por nome é a mais "
              "barata das três (de 0,0012 a 0,0015 ms) porque percorre a árvore indexada por "
              "nome, que com esta entrada tem a mesma altura da outra, sem nenhum "
              "religamento de ponteiros a fazer. Na árvore binária comum com a mesma "
              "entrada, as mesmas operações custam <b>milissegundos</b> e crescem "
              "proporcionalmente a <i>n</i>."),
            P("<b>A conclusão da comparação</b> é que a AVL entrega, para a entrada "
              "<i>pior possível</i> da árvore binária comum, exatamente o desempenho que a "
              "árvore comum só alcança na entrada <i>melhor possível</i>. Em outras palavras: "
              "a AVL troca uma dependência perigosa — a sorte na ordem de chegada dos dados — "
              "por um custo fixo e pequeno de manutenção."),

            P("5.5 Os dados atendem ao previsto na seção 4?", "h2"),
            P("Confrontando cada previsão da análise matemática com o que foi medido:"),
            tabela([
                ["Previsão da seção 4", "O que foi medido", "Confere?"],
                ["A AVL mantém h = O(log n) para <b>qualquer</b> ordem de entrada (4.1)",
                 "Com a entrada crescente — a pior para a árvore comum — a AVL ficou em 14, "
                 "15, 16 e 17 níveis, exatamente piso(log<sub>2</sub> n).", "<b>Sim</b>"],
                ["<b>adicionar</b> é O(log n), logo montar n elementos é O(n log n) (4.3)",
                 "As razões de tempo da montagem ficaram entre 1,35× e 1,75× por duplicação "
                 "de n, e a contagem de comparações cresceu cerca de 2,14× — compatível com "
                 "n·log n, e muito distante do 4,00× quadrático da árvore comum.",
                 "<b>Sim</b>"],
                ["<b>pesquisar</b> é O(log n), fazendo h + 1 comparações no pior caso (4.3 e 2.3)",
                 "A contagem deu exatamente 15, 16, 17 e 18 comparações para alturas 14, 15, "
                 "16 e 17, e o tempo ficou em torno de 1,5 microssegundo, praticamente "
                 "constante.", "<b>Sim</b>"],
                ["<b>remover</b> é O(log n), ainda que possa exigir até O(log n) rotações (4.4)",
                 "A remoção custou de 2,2 a 2,7 microssegundos, cerca do dobro da busca — "
                 "coerente com busca mais rebalanceamento na volta — e praticamente não "
                 "cresceu com n.", "<b>Sim</b>"],
                ["O preço do equilíbrio é um custo constante por nível (4.5)",
                 "Com o arquivo já balanceado, em que nenhuma rotação é disparada, a AVL fez "
                 "<b>exatamente o mesmo número de comparações</b> da árvore comum (634.496 a "
                 "6.275.750) e custou de 12% a 16% a mais de <b>tempo</b> — ou seja, o "
                 "sobrecusto é só o das atualizações de altura, constante por nível.",
                 "<b>Sim</b>"],
            ], [5.0 * cm, 7.6 * cm, 1.9 * cm]),
            Spacer(1, 8),
            P("Nenhuma previsão da seção 4 foi contrariada pelos dados. A única observação "
              "que vale registrar é sobre a <b>precisão das medidas de tempo</b> das operações "
              "individuais: elas duram poucos microssegundos na AVL, faixa em que o relógio "
              "sofre interferência do sistema operacional e do coletor de lixo. Por isso a "
              "contagem de comparações da seção 5.3 é a evidência mais forte do O(log n) — e "
              "ela é exata."),
            P("<b>E qual é esse custo?</b> Ele aparece quando comparamos a AVL com a árvore "
              "binária na entrada <b>balanceada</b>, em que o rebalanceamento não é "
              "necessário e portanto só acrescenta trabalho:"),
        ]
        if any(k[0] == "avl_balanceada" for k in r):
            linhas_custo = [["n", "Montagem — árvore binária (ms)", "Montagem — AVL (ms)",
                             "Sobrecusto"]]
            for n in tam(r, "avl_balanceada"):
                vb = r[("arvore_balanceada", n)]["montagem"] if ("arvore_balanceada", n) in r else None
                va_ = r[("avl_balanceada", n)]["montagem"]
                sob = f"{(va_/vb - 1)*100:+.0f}%".replace(".", ",") if vb else "—"
                linhas_custo.append([num(n, 0), num(vb, 2) if vb else "—", num(va_, 2), sob])
            hist += [
                KeepTogether([tabela(linhas_custo,
                                     [2.4 * cm, 4.6 * cm, 3.6 * cm, 3.0 * cm])]),
                Spacer(1, 8),
                P("Com a entrada já balanceada, as duas estruturas chegam à mesma altura e a "
                  "AVL faz trabalho que não era necessário: atualizar a altura de cada nó no "
                  "caminho de volta e verificar o fator de balanceamento em cada um. O "
                  "sobrecusto medido fica em <b>12% a 16% no tempo de montagem</b>. "
                  "Esse sobrecusto é <b>inteiramente</b> composto por essas operações de "
                  "altura: como mostrado na seção 5.3, a contagem de comparações da AVL com "
                  "esse mesmo arquivo é idêntica à da árvore comum, porque nenhuma rotação "
                  "chega a ser disparada. É um preço pago uma única vez, na montagem, e um "
                  "seguro barato contra um pior caso que custa minutos."),
            ]
        hist += [PageBreak()]

    # ================================================================
    # SEÇÃO 6 — ÁRVORES NA BIBLIOTECA PADRÃO DE JAVA
    # ================================================================
    hist += [
        P("6. Árvores binárias na biblioteca padrão de Java", "h1"),
        P("A biblioteca padrão de Java não expõe uma classe “árvore binária de busca” de uso "
          "geral, nem uma AVL. O que ela oferece são <b>coleções ordenadas implementadas "
          "sobre uma árvore binária balanceada</b> — e a escolha de qual árvore usar é, por si "
          "só, uma resposta interessante à pergunta desta seção."),

        P("6.1 TreeMap e TreeSet: árvores rubro-negras", "h2"),
        P("A classe " + C("java.util.TreeMap") + " é descrita na própria documentação oficial "
          "como “<i>A Red-Black tree based NavigableMap implementation</i>”, e acrescenta que "
          "os algoritmos são adaptados do livro <i>Introduction to Algorithms</i>, de Cormen, "
          "Leiserson e Rivest. Já " + C("java.util.TreeSet") + " não implementa árvore "
          "nenhuma: é “<i>a NavigableSet implementation based on a TreeMap</i>”, ou seja, um "
          "conjunto construído sobre um " + C("TreeMap") + " em que só as chaves importam."),
        P("<b>Garantias de desempenho.</b> A documentação do " + C("TreeMap") + " afirma: "
          "“<i>This implementation provides guaranteed log(n) time cost for the "
          "containsKey, get, put and remove operations</i>”. A do " + C("TreeSet") + " "
          "declara o mesmo para " + C("add") + ", " + C("remove") + " e " + C("contains") +
          ". Note a palavra <b>guaranteed</b>: é a mesma promessa da nossa AVL e justamente "
          "aquela que a árvore binária comum <b>não</b> pode fazer."),

        P("6.2 O que é uma árvore rubro-negra", "h2"),
        P("É uma árvore binária de busca em que cada nó carrega uma cor (vermelho ou preto) e "
          "em que valem as seguintes regras:"),
        mono("", """
  1. Todo no e vermelho ou preto.
  2. A raiz e preta.
  3. Toda folha (no nulo) e considerada preta.
  4. Um no vermelho nao pode ter filho vermelho (nao ha dois vermelhos
     seguidos em um caminho).
  5. Todo caminho de um no ate qualquer folha descendente contem o MESMO
     numero de nos pretos.

  Consequencia: o caminho mais longo da raiz ate uma folha tem no maximo o
  DOBRO do comprimento do mais curto, o que limita a altura a

                      h <= 2 * log2(n + 1)

  ou seja, O(log n) - como na AVL, porem com uma folga maior.
"""),
        P("O equilíbrio é mantido por <b>recolorações</b> e <b>rotações</b> — as mesmas "
          "rotações simples e duplas que implementamos na AVL (seção 4.2). A diferença é "
          "quando elas são acionadas: a rubro-negra tolera desequilíbrios maiores e, por isso, "
          "precisa reorganizar a estrutura com menos frequência."),

        P("6.3 Como os elementos são comparados", "h2"),
        P("Exatamente como na nossa biblioteca. A documentação do " + C("TreeMap") + " diz que "
          "“<i>The map is sorted according to the natural ordering of its keys, or by a "
          "Comparator provided at map creation time, depending on which constructor is "
          "used</i>”. São os dois caminhos vistos em aula:"),
        tabela([
            ["Construtor", "Critério de comparação", "Exige do tipo armazenado"],
            [C("new TreeMap&lt;&gt;()"), "Ordem natural da chave",
             "Que a chave implemente " + C("Comparable") + " (senão, "
             + C("ClassCastException") + " na inserção)"],
            [C("new TreeMap&lt;&gt;(cmp)"), "O " + C("Comparator") + " informado",
             "Nada — é o comparador que sabe comparar, como na nossa " + C("ArvoreBinaria")],
        ], [4.3 * cm, 4.2 * cm, 6.1 * cm]),
        Spacer(1, 8),
        P("Há ainda uma exigência sutil que vale conhecer: a documentação alerta que a ordem "
          "“<i>must be consistent with equals</i>”, porque “<i>a sorted map performs all key "
          "comparisons using its compareTo (or compare) method, so two keys that are deemed "
          "equal by this method are, from the standpoint of the sorted map, equal</i>”. Em "
          "outras palavras: se o comparador disser que dois objetos diferentes são iguais, o "
          + C("TreeMap") + " os tratará como a mesma chave. É o mesmo cuidado que tivemos ao "
          "escolher o telefone — um valor único — como chave de uma das nossas árvores."),

        P("6.4 Por que o Java escolheu rubro-negra em vez de AVL", "h2"),
        P("As duas garantem O(log n), então a escolha é uma troca entre dois custos:"),
        tabela([
            ["Critério", "AVL", "Rubro-negra"],
            ["Critério de equilíbrio", "|fb| ≤ 1 em todo nó", "Regras de cor; caminho mais "
             "longo ≤ 2× o mais curto"],
            ["Altura máxima", "≈ 1,44 · log<sub>2</sub> n", "≈ 2 · log<sub>2</sub> n"],
            ["Busca", "Mais rápida (árvore mais rasa)", "Ligeiramente mais lenta"],
            ["Rotações na inserção", "No máximo 1", "No máximo 2"],
            ["Rotações na remoção", "Até O(log n)", "No máximo 3"],
            ["Melhor para", "Cargas dominadas por <b>leitura</b>",
             "Cargas com muita <b>escrita</b>"],
        ], [3.4 * cm, 4.6 * cm, 6.6 * cm]),
        Spacer(1, 8),
        P("Uma coleção de uso geral, como as do " + C("java.util") + ", não sabe de antemão "
          "qual será o perfil de uso. A rubro-negra é a escolha mais equilibrada: paga um "
          "pouco a mais em cada busca (a árvore pode ser até 40% mais alta que a AVL) para "
          "garantir um número <b>constante</b> de rotações também na remoção, em vez dos "
          "O(log n) rebalanceamentos que a AVL pode precisar. Se a aplicação faz muito mais "
          "buscas que modificações, a AVL seria a melhor escolha — e é por isso que ela ainda "
          "é ensinada e usada em índices e estruturas especializadas."),

        P("6.5 Outras árvores binárias na biblioteca padrão", "h2"),
        P("Além do " + C("TreeMap") + "/" + C("TreeSet") + ", vale registrar mais duas "
          "ocorrências:"),
        P("<b>" + C("java.util.PriorityQueue") + " — heap binário.</b> A documentação a "
          "descreve como “<i>an unbounded priority queue based on a priority heap</i>”. Um "
          "heap binário é uma árvore binária <b>completa</b>, representada em um vetor em vez "
          "de nós encadeados (os filhos do índice <i>i</i> ficam em 2i+1 e 2i+2). Não é uma "
          "árvore de <b>busca</b>: ela só garante que cada nó é menor que seus filhos, o que "
          "basta para achar o mínimo, mas não para localizar um elemento qualquer. Por isso a "
          "própria documentação registra custos diferentes: O(log n) para "
          + C("offer") + ", " + C("add") + ", " + C("poll") + " e " + C("remove()") + "; "
          "<b>tempo linear</b> para " + C("contains(Object)") + " e "
          + C("remove(Object)") + "; e tempo constante para " + C("peek") + " e "
          + C("size") + "."),
        P("<b>" + C("java.util.HashMap") + " — árvores rubro-negras dentro das listas de "
          "colisão.</b> Desde o Java 8, quando muitas chaves caem no mesmo <i>bucket</i>, a "
          "lista encadeada daquele bucket é convertida em uma árvore rubro-negra. A "
          "documentação pública registra apenas o efeito — “<i>when keys are Comparable, this "
          "class may use comparison order among keys to help break ties</i>” —, mas os "
          "comentários de implementação do OpenJDK são explícitos: a conversão ocorre a partir "
          "de " + C("TREEIFY_THRESHOLD = 8") + " nós no bucket (desde que a tabela já tenha "
          "ao menos " + C("MIN_TREEIFY_CAPACITY = 64") + " posições; caso contrário a tabela é "
          "redimensionada), e a árvore volta a ser uma lista simples quando o bucket encolhe "
          "para " + C("UNTREEIFY_THRESHOLD = 6") + " nós."),
        P("Esse detalhe é uma ilustração perfeita do que medimos neste trabalho: o "
          + C("HashMap") + " é O(1) no caso médio, mas no pior caso — muitas colisões — "
          "degenerava para O(n), porque o bucket era uma <b>lista encadeada</b>. A solução "
          "adotada foi exatamente trocar a lista por uma <b>árvore balanceada</b>, "
          "transformando o pior caso de O(n) em O(log n). É a mesma passagem que fizemos do "
          "Trabalho 1 para este."),

        P("6.6 Comparando com a nossa biblioteca", "h2"),
        tabela([
            ["", "Nossa " + C("ArvoreBinaria"), "Nossa " + C("ArvoreAVL"),
             C("TreeMap") + " / " + C("TreeSet")],
            ["Estrutura", "ABB sem balanceamento", "ABB com balanceamento AVL",
             "ABB com balanceamento rubro-negro"],
            ["Altura garantida", "Nenhuma (até n−1)", "≈ 1,44 · log<sub>2</sub> n",
             "≈ 2 · log<sub>2</sub> n"],
            ["Busca / inserção / remoção", "O(n) no pior caso", "O(log n) garantido",
             "O(log n) garantido"],
            ["Comparação", C("Comparator") + " no construtor",
             C("Comparator") + " no construtor",
             C("Comparable") + " ou " + C("Comparator")],
        ], [3.5 * cm, 3.6 * cm, 3.6 * cm, 3.9 * cm]),
        Spacer(1, 8),
        P("Ou seja: a estrutura que a biblioteca padrão de Java oferece para dados ordenados é "
          "conceitualmente a mesma que implementamos na seção 4, com um critério de equilíbrio "
          "diferente e uma troca explícita entre custo de busca e custo de modificação."),

        P("Fontes", "h2"),
        P("Documentação oficial do Java 21 (Oracle):"),
        P("• " + C("java.util.TreeMap") + " — <font color='#52514e'>"
          "docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeMap.html</font>",
          "pl"),
        P("• " + C("java.util.TreeSet") + " — <font color='#52514e'>"
          "docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/TreeSet.html</font>",
          "pl"),
        P("• " + C("java.util.PriorityQueue") + " — <font color='#52514e'>"
          "docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/PriorityQueue.html"
          "</font>", "pl"),
        P("• " + C("java.util.HashMap") + " — <font color='#52514e'>"
          "docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/HashMap.html</font>",
          "pl"),
        P("Os detalhes da <i>treeification</i> do " + C("HashMap") + " estão nos comentários "
          "de implementação do código-fonte do OpenJDK, em "
          + C("src/java.base/share/classes/java/util/HashMap.java") + "."),
        P("Material da disciplina: slides de árvores binárias e de árvores AVL (APNP) e os "
          "exemplos em C disponibilizados pelo professor (" + C("arvBin.c") + "); classe "
          + C("ArvoreBinariaBase") + " e interface " + C("IColecao") + " do repositório da "
          "disciplina."),
        P("Código e relatório deste trabalho: <font color='#52514e'>"
          "github.com/ryanlimap/trabalho_tpa</font>", "pl"),
    ]

    doc = SimpleDocTemplate(
        str(SAIDA), pagesize=A4,
        leftMargin=2.4 * cm, rightMargin=2.4 * cm,
        topMargin=2.2 * cm, bottomMargin=2.0 * cm,
        title="Trabalho 2 - Arvores Binarias - Relatorio parcial",
        author="Lucas Ramos Pianissola, Ryan Lima Pecanha, Davi Alvarenga",
    )

    def rodape(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(CINZA)
        if doc_.page > 1:
            canvas.drawRightString(A4[0] - 2.4 * cm, 1.3 * cm, str(doc_.page))
            canvas.drawString(2.4 * cm, 1.3 * cm,
                              "Trabalho 2 — Árvores Binárias e Análise de Complexidade")
        canvas.restoreState()

    doc.build(hist, onFirstPage=rodape, onLaterPages=rodape)
    print("PDF gerado:", SAIDA)


if __name__ == "__main__":
    construir()
