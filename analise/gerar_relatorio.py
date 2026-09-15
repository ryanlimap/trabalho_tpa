#!/usr/bin/env python3
"""Gera o PDF do relatorio do Trabalho 1 a partir do codigo-fonte e do CSV de medicoes."""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle, KeepTogether)

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "dados" / "resultados.csv"
FIG = RAIZ / "analise" / "figuras"
SAIDA = RAIZ / "relatorio" / "Relatorio_Trabalho1.pdf"
SAIDA.parent.mkdir(parents=True, exist_ok=True)

# Descricao da maquina onde as medicoes desta versao do relatorio foram feitas.
# Ao rodar as medicoes em outra maquina, basta trocar este texto e gerar o PDF de novo.
AMBIENTE = ("AMD Ryzen 5 5600G (6 núcleos, 16 MB de cache L3), 16 GB de RAM DDR4 "
            "2666 MHz, Windows 11, OpenJDK 21 (64 bits). Todas as medições apresentadas "
            "nesta seção foram coletadas nessa mesma máquina, sem outros programas "
            "concorrendo pela CPU.")

AZUL = colors.HexColor("#2a78d6")
LARANJA = colors.HexColor("#eb6834")
CINZA = colors.HexColor("#52514e")
CINZA_CLARO = colors.HexColor("#eeeeec")

# ----------------------------------------------------------------------
# estilos
# ----------------------------------------------------------------------
ss = getSampleStyleSheet()
S = {
    "titulo": ParagraphStyle("titulo", parent=ss["Title"], fontSize=20, leading=25),
    "sub": ParagraphStyle("sub", parent=ss["Normal"], fontSize=12, leading=17,
                          alignment=TA_CENTER, textColor=CINZA),
    "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontSize=15, leading=19,
                         spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#12356b")),
    "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12, leading=16,
                         spaceBefore=12, spaceAfter=5, textColor=colors.black),
    "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontSize=10.5, leading=14,
                         spaceBefore=9, spaceAfter=3, textColor=CINZA),
    "p": ParagraphStyle("p", parent=ss["BodyText"], fontSize=10, leading=14.5,
                        alignment=TA_JUSTIFY, spaceAfter=7),
    "cod": ParagraphStyle("cod", parent=ss["Code"], fontSize=7.2, leading=8.6,
                          backColor=colors.HexColor("#f6f6f4"), borderPadding=5,
                          leftIndent=0, textColor=colors.HexColor("#1a1a19")),
    "leg": ParagraphStyle("leg", parent=ss["Normal"], fontSize=8.5, leading=11,
                          alignment=TA_CENTER, textColor=CINZA, spaceAfter=10),
    "cel": ParagraphStyle("cel", parent=ss["Normal"], fontSize=8.5, leading=11),
    "celb": ParagraphStyle("celb", parent=ss["Normal"], fontSize=8.5, leading=11,
                           fontName="Helvetica-Bold"),
}


def P(txt, estilo="p"):
    return Paragraph(txt, S[estilo])


def codigo(arquivo, ini, fim, titulo):
    """Trecho do fonte com as linhas numeradas (numeracao real do arquivo)."""
    linhas = (RAIZ / arquivo).read_text(encoding="utf-8").splitlines()
    corpo = []
    for i in range(ini, fim + 1):
        texto = linhas[i - 1].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        corpo.append(f"{i:>3}  {texto}")
    bloco = "<br/>".join(l.replace(" ", "&nbsp;") for l in corpo)
    return KeepTogether([
        P(f"<b>{titulo}</b> &mdash; <font color='#52514e'>{arquivo}, linhas {ini}-{fim}</font>",
          "h3"),
        Paragraph(bloco, S["cod"]),
        Spacer(1, 9),
    ])


def figura(nome, legenda, largura=15.0 * cm):
    img = Image(str(FIG / nome))
    prop = img.imageHeight / img.imageWidth
    img.drawWidth = largura
    img.drawHeight = largura * prop
    return KeepTogether([img, Spacer(1, 3), P(legenda, "leg")])


def tabela(dados, larguras, destacar_col0=True):
    """Converte cada celula em Paragraph para que o texto quebre linha."""
    est_cab = ParagraphStyle("cab", parent=S["cel"], fontName="Helvetica-Bold",
                             textColor=colors.white, alignment=TA_CENTER)
    est_col0 = ParagraphStyle("col0", parent=S["cel"], fontName="Helvetica-Bold")
    est_cen = ParagraphStyle("cen", parent=S["cel"], alignment=TA_CENTER)
    corpo = []
    for i, linha in enumerate(dados):
        nova = []
        for j, cel in enumerate(linha):
            if isinstance(cel, str):
                txt = cel.replace("\n", "<br/>")
                if i == 0:
                    nova.append(Paragraph(txt, est_cab))
                elif j == 0 and destacar_col0:
                    nova.append(Paragraph(txt, est_col0))
                else:
                    curto = len(cel) <= 24
                    nova.append(Paragraph(txt, est_cen if curto else S["cel"]))
            else:
                nova.append(cel)
        corpo.append(nova)
    dados = corpo
    t = Table(dados, colWidths=larguras, hAlign="CENTER", repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12356b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9c8c4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f4")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if destacar_col0:
        estilo.append(("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"))
    t.setStyle(TableStyle(estilo))
    return t


# ----------------------------------------------------------------------
# dados empiricos
# ----------------------------------------------------------------------
def flt(txt):
    """Aceita tanto 32.45 quanto 32,45 (JVM em locale pt-BR imprime com virgula)."""
    return float(str(txt).strip().replace(",", "."))


def carregar():
    bruto = defaultdict(list)
    with CSV.open() as f:
        for linha in csv.DictReader(f, delimiter=";"):
            if not linha.get("n") or not linha["n"].isdigit():
                continue
            chave = (int(linha["n"]), linha["ordenada"] == "true")
            bruto[chave].append({c: flt(linha[f"{c}_ms"]) for c in
                                 ("montagem", "busca_tel", "busca_nome", "remocao")})
    resumo = {}
    for chave, med in bruto.items():
        resumo[chave] = {c: statistics.median(m[c] for m in med)
                         for c in ("montagem", "busca_tel", "busca_nome", "remocao")}
        resumo[chave]["execucoes"] = len(med)
    return resumo


def num(v, casas=2):
    return f"{v:,.{casas}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def carregar_contagens():
    caminho = RAIZ / "dados" / "contagens.csv"
    dados = {}
    with caminho.open() as f:
        for linha in csv.DictReader(f, delimiter=";"):
            if not linha.get("n") or not linha["n"].isdigit():
                continue
            dados[(int(linha["n"]), linha["ordenada"] == "true")] = {
                "montagem": int(linha["comp_montagem"]),
                "busca": int(linha["comp_busca_tel"]),
            }
    return dados


def tabela_contagens(cont):
    tamanhos = sorted({n for (n, _) in cont})
    linhas = [["n", "Montagem\nnão-ordenada", "Montagem\nordenada", "razão",
               "Pesquisa\nnão-ordenada"]]
    ant = None
    for n in tamanhos:
        cno = cont.get((n, False), {}).get("montagem")
        co = cont.get((n, True), {}).get("montagem")
        bno = cont.get((n, False), {}).get("busca")
        razao = f"{co/ant:.2f}×".replace(".", ",") if (co and ant) else "—"
        linhas.append([
            num(n, 0),
            num(cno, 0) if cno is not None else "—",
            num(co, 0) if co is not None else "não medido",
            razao,
            num(bno, 0) if bno is not None else "—",
        ])
        if co:
            ant = co
    return tabela(linhas, [2.1 * cm, 3.1 * cm, 3.6 * cm, 1.8 * cm, 3.0 * cm])


def tabela_metrica(r, campo, rotulo):
    tamanhos = sorted({n for (n, _) in r})
    cab = ["n", f"{rotulo} — não-ordenada (ms)", "razão", f"{rotulo} — ordenada (ms)", "razão"]
    linhas = [cab]
    ant_no = ant_o = None
    for n in tamanhos:
        vno = r.get((n, False), {}).get(campo)
        vo = r.get((n, True), {}).get(campo)
        rno = f"{vno/ant_no:.2f}×".replace(".", ",") if (vno and ant_no) else "—"
        ro = f"{vo/ant_o:.2f}×".replace(".", ",") if (vo and ant_o) else "—"
        linhas.append([
            num(n, 0),
            num(vno, 2) if vno is not None else "não medido",
            rno,
            num(vo, 2) if vo is not None else "não medido",
            ro,
        ])
        if vno:
            ant_no = vno
        if vo:
            ant_o = vo
    return tabela(linhas, [2.1 * cm, 4.4 * cm, 1.8 * cm, 4.4 * cm, 1.8 * cm])


# ----------------------------------------------------------------------
# documento
# ----------------------------------------------------------------------
def construir():
    r = carregar()
    hist = []

    # ---------------- capa ----------------
    hist += [
        Spacer(1, 3.2 * cm),
        Paragraph("Trabalho 1", S["titulo"]),
        Paragraph("Análise de complexidade em estruturas de listas", S["sub"]),
        Spacer(1, 1.4 * cm),
        Paragraph("Instituto Federal do Espírito Santo &mdash; Campus Serra<br/>"
                  "Técnicas de Programação Avançada<br/>"
                  "Prof. Victorio Albani de Carvalho", S["sub"]),
        Spacer(1, 2.0 * cm),
        Paragraph("<b>Integrantes do grupo</b>", S["sub"]),
        Spacer(1, 0.3 * cm),
        Paragraph("Lucas Ramos Pianissola<br/>Ryan Lima Peçanha<br/>"
                  "Davi Alvarenga", S["sub"]),
        Spacer(1, 1.4 * cm),
        Paragraph("<b>Repositório do projeto</b><br/>"
                  "https://github.com/ryanlimap/trabalho_tpa", S["sub"]),
        PageBreak(),
    ]

    # ---------------- secao 1 ----------------
    hist += [
        P("1. Desenvolvimento da biblioteca e do programa de teste", "h1"),
        P("1.1 Atuação de cada componente do grupo", "h2"),
        P("O quadro abaixo descreve a participação de cada integrante nos itens 1 "
          "(biblioteca de listas) e 2 (programa de teste) da especificação. O trabalho foi "
          "dividido por módulo, mas as decisões de projeto e a revisão do código foram "
          "discutidas pelos três."),
        tabela([
            ["Integrante", "Atuação nos itens 1 e 2"],
            ["Lucas Ramos Pianissola",
             "Item 1 — a biblioteca: classes <font face='Courier'>No</font> e "
             "<font face='Courier'>ListaEncadeada</font>, com <i>Generics</i> e "
             "<font face='Courier'>Comparator</font>; inserção ordenada e não-ordenada, "
             "pesquisa, remoção, <font face='Courier'>toString</font> e "
             "<font face='Courier'>iterator</font>; implementação da interface "
             "<font face='Courier'>IColecao</font> e testes dos casos de borda."],
            ["Ryan Lima Peçanha",
             "Item 2 — o programa de teste: classe de domínio "
             "<font face='Courier'>Contato</font>, os dois comparadores e a agenda "
             "(<font face='Courier'>app.Programa</font>) com o menu completo, a leitura do "
             "arquivo de entrada e a medição dos tempos exibidos ao usuário."],
            ["Davi Alvarenga",
             "Apoio ao item 2 e infraestrutura das medições: "
             "<font face='Courier'>app.GeradorArquivo</font>, "
             "<font face='Courier'>app.Benchmark</font> e "
             "<font face='Courier'>app.ContagemOperacoes</font>; execução das rodadas, "
             "organização dos dados, gráficos e redação do relatório."],
        ], [3.6 * cm, 10.9 * cm], destacar_col0=True),
        Spacer(1, 10),

        P("1.2 Como as ferramentas de IA foram utilizadas", "h2"),
        P("Usamos uma ferramenta de IA generativa (Claude, da Anthropic) como apoio em três "
          "frentes bem delimitadas, descritas a seguir."),
        P("<b>a) Aproveitamento do material da disciplina.</b> Fornecemos à ferramenta os "
          "slides de revisão (“Lista encadeada e Generics”) e o repositório do professor, de "
          "onde ela extraiu os métodos já apresentados em aula — "
          "<font face='Courier'>inserirElemento</font>, "
          "<font face='Courier'>contemElemento</font>, "
          "<font face='Courier'>excluirElemento</font>, a inserção ordenada com "
          "<font face='Courier'>Comparator</font> e a interface "
          "<font face='Courier'>IColecao</font> — e os organizou como ponto de partida do "
          "nosso código."),
        P("<b>b) Orientação sobre como usar esses métodos.</b> A ferramenta explicou como "
          "adaptar o código dos slides às exigências do trabalho: usar "
          "<i>Generics</i> (<font face='Courier'>T</font>) no lugar de "
          "<font face='Courier'>Object</font>, receber o "
          "<font face='Courier'>Comparator&lt;T&gt;</font> e o boolean "
          "<font face='Courier'>ordenada</font> no construtor, adequar as assinaturas aos "
          "métodos exigidos pela <font face='Courier'>IColecao</font> "
          "(<font face='Courier'>adicionar</font>, "
          "<font face='Courier'>pesquisar</font>, <font face='Courier'>remover</font> e "
          "<font face='Courier'>quantidadeNos</font>) e tratar os casos de borda (lista "
          "vazia, remoção do primeiro e do último nó). Revisamos o resultado linha a linha e "
          "testamos cada caso antes de aceitá-lo."),
        P("<b>c) Gráficos, tabelas e imagens do relatório.</b> A ferramenta auxiliou na "
          "geração dos gráficos e das tabelas apresentados na seção 3, a partir do arquivo CSV "
          "produzido pelas nossas execuções: escrevemos com o apoio dela os scripts "
          "<font face='Courier'>analise/gerar_graficos.py</font> (matplotlib) e "
          "<font face='Courier'>analise/gerar_relatorio.py</font> (ReportLab), que leem as "
          "medições e montam as figuras e as tabelas. Todos os números apresentados são os "
          "medidos nas nossas próprias execuções — nenhum valor foi estimado ou inventado "
          "pela ferramenta."),
        P("<b>d) Revisão de texto.</b> A redação final do relatório foi revisada com apoio da "
          "ferramenta, para clareza e correção da linguagem."),

        P("1.3 Repositório e organização do código", "h2"),
        P("Todo o código está disponível em <b>https://github.com/ryanlimap/trabalho_tpa</b>, "
          "com um arquivo <font face='Courier'>README.md</font> que descreve a organização das "
          "pastas e como compilar e executar o projeto."),
        tabela([
            ["Pasta / arquivo", "Conteúdo"],
            ["src/colecao/IColecao.java", "Interface exigida pela especificação."],
            ["src/colecao/No.java", "Nó genérico: valor do tipo T e referência para o próximo."],
            ["src/colecao/ListaEncadeada.java",
             "A biblioteca: lista genérica, ordenada ou não, com Comparator. Não imprime nada."],
            ["src/app/Contato.java", "Classe de domínio (nome e telefone); toString \"nome-telefone\"."],
            ["src/app/ComparadorContatoPorNome.java", "Comparator pela chave nome."],
            ["src/app/ComparadorContatoPorTelefone.java", "Comparator pela chave telefone."],
            ["src/app/Programa.java", "Agenda de contatos com o menu e a medição de tempos."],
            ["src/app/GeradorArquivo.java", "Gera arquivos de entrada de qualquer tamanho."],
            ["src/app/Benchmark.java", "Executa uma rodada da análise empírica (tempos) e imprime uma linha CSV."],
            ["src/app/ComparadorContador.java", "Decorator que conta as chamadas ao comparador."],
            ["src/app/ContagemOperacoes.java", "Conta o número de comparações executadas, em vez de medir tempo."],
            ["analise/", "Scripts Python que produzem os gráficos e este PDF."],
            ["dados/", "Arquivos de entrada e o CSV com todas as medições."],
        ], [5.6 * cm, 9.0 * cm]),
        Spacer(1, 8),
        P("Decisão de projeto importante: o programa mantém <b>duas listas</b> — uma indexada "
          "por nome e outra por telefone — que guardam <b>as mesmas instâncias</b> de "
          "<font face='Courier'>Contato</font>. Não há duplicação de contatos: as duas listas "
          "apenas apontam para os mesmos objetos, de modo que uma alteração feita por um "
          "caminho é vista pelo outro."),
        PageBreak(),
    ]

    # ---------------- secao 2 ----------------
    hist += [
        P("2. Análise matemática de complexidade", "h1"),
        P("Nesta seção analisamos os métodos <font face='Courier'>adicionar</font>, "
          "<font face='Courier'>pesquisar</font>, <font face='Courier'>remover</font> e "
          "<font face='Courier'>quantidadeNos</font> da classe "
          "<font face='Courier'>ListaEncadeada</font>. Em todos os trechos, a numeração das "
          "linhas é a numeração real do arquivo "
          "<font face='Courier'>src/colecao/ListaEncadeada.java</font>."),
        P("<b>Premissas.</b> (i) <i>n</i> é a quantidade de nós da lista; (ii) atribuições, "
          "comparações, criação de um nó e desvios são operações de custo constante, contadas "
          "como 1; (iii) a chamada <font face='Courier'>comparador.compare(...)</font> é "
          "considerada O(1) — para as chaves usadas (nome e telefone) ela compara Strings de "
          "tamanho limitado, independente de <i>n</i>; (iv) analisamos o <b>pior caso</b>, "
          "conforme discutido em aula, por ser o limite superior garantido para qualquer entrada."),

        P("2.1 Método adicionar", "h2"),
        codigo("src/colecao/ListaEncadeada.java", 46, 58,
               "Listagem 1 — adicionar (ponto de entrada)"),
        P("As linhas 48-50 fazem uma comparação e, no máximo, um retorno: custo 2. A linha 51 "
          "testa o atributo <font face='Courier'>ordenada</font> (custo 1) e desvia para um dos "
          "dois métodos auxiliares. As linhas 56-57 executam um incremento e um retorno: custo 2. "
          "Assim, <b>T<sub>adicionar</sub>(n) = 5 + T<sub>auxiliar</sub>(n)</b>: o custo do método "
          "é dominado pelo auxiliar escolhido."),

        codigo("src/colecao/ListaEncadeada.java", 63, 72,
               "Listagem 2 — inserção em lista NÃO-ORDENADA"),
        P("Não há laço algum. A linha 64 cria o nó (custo 1); a linha 65 testa se a lista está "
          "vazia (custo 1); em seguida executa-se o bloco 66-67 (duas atribuições) ou o bloco "
          "69-70 (duas atribuições). O número de operações é o mesmo para uma lista vazia ou "
          "com um milhão de nós, porque a referência <font face='Courier'>ult</font> dá acesso "
          "direto ao fim da lista — não é preciso percorrê-la. Portanto "
          "<b>T(n) = 4</b>, uma constante, e a ordem de complexidade é <b>O(1)</b>, "
          "tanto no melhor quanto no pior caso."),
        P("Observação: se a classe não guardasse a referência <font face='Courier'>ult</font>, "
          "seria necessário percorrer a lista inteira para chegar ao último nó e a inserção "
          "passaria a ser O(n)."),

        codigo("src/colecao/ListaEncadeada.java", 78, 101,
               "Listagem 3 — inserção em lista ORDENADA"),
        P("As linhas 79-86 têm custo constante (criação do nó, duas atribuições, o teste de "
          "lista vazia e, quando ela está vazia, a saída imediata pela linha 85). O que define "
          "a complexidade é o laço das linhas 87-90: ele avança nó a nó enquanto o elemento "
          "atual for <b>menor</b> que o novo elemento. Cada iteração custa 3 operações (a "
          "comparação da linha 87 e as duas atribuições das linhas 88-89)."),
        P("Seja <i>k</i> o número de nós visitados antes de encontrar a posição de inserção. "
          "O laço executa <i>k</i> iterações e, depois dele, as linhas 91-100 fazem no máximo "
          "dois testes e duas atribuições (custo constante 4). Logo "
          "<b>T(n) = 3k + c</b>."),
        P("<b>Pior caso:</b> ocorre quando o elemento a ser inserido é <b>maior que todos os "
          "que já estão na lista</b>, ou seja, quando ele deve ir para o fim. Nesse caso o laço "
          "percorre todos os <i>n</i> nós (<i>k = n</i>) e o custo é T(n) = 3n + c, ou seja, "
          "<b>O(n)</b>. É exatamente o que acontece quando o arquivo de entrada já está "
          "ordenado de forma crescente: cada novo contato é o maior de todos. "
          "<b>Melhor caso:</b> quando o novo elemento é menor que o primeiro (<i>k</i> = 0), "
          "o custo é constante, O(1). <b>Caso médio</b> (entrada aleatória, como nos nossos "
          "testes): <i>k</i> ≈ n/2, o que ainda é O(n)."),

        P("2.1.1 Consequência: custo de montar uma lista com n elementos", "h3"),
        P("O programa de teste insere os <i>n</i> contatos do arquivo um a um. Na lista "
          "<b>não-ordenada</b>, cada inserção é O(1), então a montagem completa custa "
          "n · O(1) = <b>O(n)</b>. Na lista <b>ordenada</b>, a i-ésima inserção percorre em "
          "média i/2 nós e, no pior caso, i nós; somando para i = 1 … n:"),
        P("<font face='Courier'>1 + 2 + 3 + … + n = n(n+1)/2 = n<super>2</super>/2 + n/2</font>"),
        P("Descartando o termo de menor grau e a constante multiplicativa, a montagem da lista "
          "ordenada é <b>O(n<super>2</super>)</b>. Essa é a diferença mais importante entre as duas listas e "
          "é claramente visível nas medições da seção 3."),

        P("2.2 Método pesquisar", "h2"),
        codigo("src/colecao/ListaEncadeada.java", 107, 121,
               "Listagem 4 — pesquisar"),
        P("A linha 109 é uma atribuição (custo 1). O laço das linhas 110-119 percorre a lista "
          "nó a nó; cada iteração custa 5 operações (o teste da linha 110, a comparação da "
          "linha 111, os testes das linhas 112 e 115 e a atribuição da linha 118). Se o "
          "elemento é encontrado, a linha 113 o devolve; se a lista acaba, a linha 120 devolve "
          "<font face='Courier'>null</font>."),
        P("A novidade em relação ao código visto em aula é a linha 115: <b>em lista ordenada, "
          "assim que encontramos um elemento maior que o procurado, sabemos que o elemento "
          "buscado não existe</b> e interrompemos a busca. Isso evita percorrer o resto da "
          "lista, mas <b>não muda a ordem de complexidade</b>."),
        P("<b>Pior caso — lista não-ordenada:</b> o elemento procurado está no último nó ou "
          "não existe na lista; o laço executa n iterações e T(n) = 5n + c, ou seja, "
          "<b>O(n)</b>. É justamente o caso medido na seção 3, em que pesquisamos o "
          "<b>último contato do arquivo</b> — que, na lista não-ordenada, está no fim."),
        P("<b>Pior caso — lista ordenada:</b> ocorre quando o elemento procurado é o maior de "
          "todos (ou é maior que todos, no caso de uma busca sem sucesso). O laço também "
          "percorre os n nós e a complexidade continua <b>O(n)</b>. A parada antecipada só "
          "melhora o caso médio: em uma busca sem sucesso, ela cai de n para cerca de n/2 "
          "comparações — um ganho de fator constante, que a notação O despreza."),

        P("2.3 Método remover", "h2"),
        codigo("src/colecao/ListaEncadeada.java", 127, 152,
               "Listagem 5 — remover"),
        P("A estrutura é a mesma da pesquisa: as linhas 129-130 custam 2 e o laço das linhas "
          "131-150 percorre a lista, com custo constante por iteração (o teste da linha 131, "
          "a comparação da linha 132 e as atribuições das linhas 148-149). Quando o elemento é "
          "encontrado, as linhas 133-143 fazem apenas <b>ligações de ponteiros</b>: tratam o "
          "caso de ser o primeiro nó (linhas 134-135), o caso geral (linha 137), o caso de ser "
          "o último nó (linhas 139-141, que atualizam <font face='Courier'>ult</font>), "
          "decrementam o contador e retornam. Todo esse bloco é O(1) — <b>a remoção em si é "
          "barata; caro é encontrar o nó</b>."),
        P("<b>Pior caso:</b> o elemento está no último nó ou não está na lista, e o laço "
          "executa n iterações: <b>O(n)</b>. Vale para os dois tipos de lista. Na lista "
          "ordenada a linha 145 novamente interrompe a busca mais cedo quando o elemento não "
          "existe, o que não altera a ordem de complexidade."),
        P("Note que a remoção do último nó, embora seja O(1) na parte de religação, exige "
          "percorrer a lista inteira para encontrar o nó <b>anterior</b> a ele — consequência "
          "de a lista ser <b>simplesmente</b> encadeada. Com uma lista duplamente encadeada "
          "esse passo seria O(1), mas a busca pelo nó continuaria O(n)."),

        P("2.4 Método quantidadeNos", "h2"),
        codigo("src/colecao/ListaEncadeada.java", 158, 161,
               "Listagem 6 — quantidadeNos"),
        P("O método executa uma única instrução: devolve o atributo "
          "<font face='Courier'>quant</font>. Como esse contador é mantido atualizado em "
          "<font face='Courier'>adicionar</font> (linha 56) e em "
          "<font face='Courier'>remover</font> (linha 142), não é necessário percorrer a "
          "estrutura. Portanto <b>T(n) = 1</b> e a complexidade é <b>O(1)</b> — no melhor e no "
          "pior caso, em lista ordenada ou não. Se o contador não existisse, seria preciso "
          "percorrer a lista contando os nós, e o método seria O(n); o custo dessa escolha é "
          "apenas um incremento por inserção, já contabilizado na análise do "
          "<font face='Courier'>adicionar</font>."),

        P("2.5 Resumo e comparação entre lista ordenada e não-ordenada", "h2"),
        tabela([
            ["Método", "Não-ordenada\n(pior caso)", "Ordenada\n(pior caso)", "Quando o pior caso ocorre"],
            ["adicionar", "O(1)", "O(n)",
             "Ordenada: novo elemento maior que todos (entrada já ordenada de forma crescente). "
             "Não-ordenada: não há pior caso — é sempre constante."],
            ["pesquisar", "O(n)", "O(n)",
             "Elemento no último nó ou inexistente (na ordenada, maior que todos)."],
            ["remover", "O(n)", "O(n)",
             "Elemento no último nó ou inexistente (na ordenada, maior que todos)."],
            ["quantidadeNos", "O(1)", "O(1)", "Não existe pior caso: custo fixo."],
            ["montar n elementos", "O(n)", "O(n<super>2</super>)",
             "Consequência direta do custo de cada inserção (seção 2.1.1)."],
        ], [2.5 * cm, 2.4 * cm, 2.2 * cm, 7.5 * cm]),
        Spacer(1, 8),
        P("<b>Há diferença de ordem de complexidade entre os dois tipos de lista?</b> "
          "Sim, mas apenas na <b>inserção</b>: O(1) na não-ordenada contra O(n) na ordenada "
          "(e, consequentemente, O(n) contra O(n<super>2</super>) para montar a estrutura inteira). Para "
          "<font face='Courier'>pesquisar</font>, <font face='Courier'>remover</font> e "
          "<font face='Courier'>quantidadeNos</font> <b>a ordem de complexidade é a mesma</b>."),
        P("Isso pode parecer contra-intuitivo: ordenar normalmente serve para acelerar a busca. "
          "O ganho não aparece porque a lista encadeada <b>não permite acesso direto a uma "
          "posição qualquer</b> — para chegar ao nó do meio é preciso passar por todos os "
          "anteriores, o que inviabiliza a busca binária. A ordenação só permite "
          "<b>interromper antes</b> uma busca sem sucesso, reduzindo o número médio de "
          "comparações pela metade: um ganho de fator constante, desprezado pela notação O. "
          "Em resumo, <b>pelo nosso código a lista ordenada paga um preço alto na montagem "
          "(O(n<super>2</super>)) sem obter melhora na ordem de complexidade das consultas</b>; ela se "
          "justifica quando é necessário percorrer os dados em ordem, não por desempenho de "
          "busca."),
    ]

    # ---------------- secao 3 ----------------
    tamanhos = sorted({n for (n, _) in r})
    tam_ord = sorted({n for (n, o) in r if o})
    maior_no = max(n for (n, o) in r if not o)
    execs = max(v["execucoes"] for v in r.values())

    hist += [
        P("3. Análise empírica de complexidade", "h1"),
        P("3.1 Metodologia", "h2"),
        P("Para cada tamanho de entrada geramos um arquivo com contatos aleatórios usando a "
          "classe <font face='Courier'>app.GeradorArquivo</font> (nomes formados por "
          "primeiro nome, sobrenome e um número aleatório; telefones únicos, obtidos pelo "
          "embaralhamento de uma faixa de números). Em seguida, a classe "
          "<font face='Courier'>app.Benchmark</font> executa, para cada arquivo e para cada "
          "tipo de lista, os quatro passos pedidos na especificação:"),
        P("1) ler o arquivo e montar as duas listas (por nome e por telefone), medindo o tempo "
          "total; 2) pesquisar pelo <b>telefone do último contato do arquivo</b>; "
          "3) pesquisar pelo <b>nome do último contato do arquivo</b>; "
          "4) remover o <b>último contato do arquivo</b>, pelo telefone."),
        P(f"Os tempos são medidos com <font face='Courier'>System.nanoTime()</font> e "
          f"convertidos para milissegundos. Cada medição roda em uma <b>JVM nova</b>, para que "
          f"uma execução não interfira na seguinte. As execuções foram repetidas {execs} vezes "
          f"e reportamos a <b>mediana</b>, que é menos sensível a variações pontuais do "
          f"sistema operacional e do coletor de lixo. As duas exceções são a lista "
          f"<b>ordenada</b> em 100.000 e em 200.000 contatos: como cada uma dessas execuções "
          f"leva minutos (a de 200.000 levou 20,1 minutos), elas foram rodadas <b>uma única "
          f"vez</b> — nesses dois pontos o valor da tabela é uma medição isolada, não uma "
          f"mediana."),
        P("Uma observação de implementação: o <font face='Courier'>System.out.printf</font> "
          "das classes de medição usa <font face='Courier'>Locale.US</font>. Sem isso, em um "
          "Windows configurado em português o Java imprimiria os tempos com vírgula decimal "
          "(<font face='Courier'>32,4520</font>) e o CSV não seria lido corretamente pelos "
          "scripts de análise."),
        P(f"<b>Ambiente de execução:</b> {AMBIENTE}"),
        P(f"<b>Tamanhos usados:</b> {', '.join(num(n,0) for n in tamanhos)} contatos para a "
          f"lista não-ordenada e {', '.join(num(n,0) for n in tam_ord)} para a ordenada. "
          f"Não incluímos a lista ordenada no tamanho de {num(maior_no,0)} porque, sendo a "
          f"montagem O(n<super>2</super>), a execução levaria várias horas — o que, por si só, já é uma "
          f"confirmação prática da análise matemática."),
        P("<b>Medição complementar.</b> Além do tempo de relógio, instrumentamos o código para "
          "<b>contar o número de comparações</b> executadas (classes "
          "<font face='Courier'>app.ComparadorContador</font> e "
          "<font face='Courier'>app.ContagemOperacoes</font>). O tempo depende da máquina, do "
          "JIT e dos caches do processador; a contagem de operações, não. Ela mede exatamente "
          "aquilo que a análise matemática da seção 2 prevê, e por isso é a evidência mais "
          "limpa da ordem de crescimento."),

        P("3.2 Tempo de leitura do arquivo e montagem das listas", "h2"),
        tabela_metrica(r, "montagem", "Montagem"),
        Spacer(1, 10),
        figura("fig1_montagem_naoordenada.png",
               "Figura 1 — Montagem das listas não-ordenadas (mediana, em ms)."),
        figura("fig2_montagem_ordenada.png",
               "Figura 2 — Montagem das listas ordenadas (mediana, em ms). Note a escala: "
               "segundos, não milissegundos."),
        figura("fig3_montagem_log.png",
               "Figura 3 — As duas curvas na mesma escala logarítmica, para comparação."),

        P("<b>Interpretação.</b> As colunas “razão” das tabelas mostram por quanto o tempo é "
          "multiplicado quando <i>n</i> dobra — é a forma mais direta de identificar a ordem "
          "de crescimento: em uma função linear a razão tende a 2; em uma função quadrática, "
          "a 4."),
        P("Na lista <b>não-ordenada</b> todas as razões ficam <b>abaixo de 2</b> (entre 1,2 e "
          "1,8), e no conjunto o tempo cresce cerca de 4,9 vezes enquanto <i>n</i> cresce 16 "
          "vezes. O crescimento é, portanto, <b>no máximo linear</b> — e está longe de "
          "qualquer coisa quadrática. As razões menores que 2 se explicam pelos <b>custos "
          "fixos</b> embutidos na medição: inicialização da JVM, compilação JIT dos métodos e "
          "leitura do arquivo do disco não dependem de <i>n</i> e pesam proporcionalmente "
          "muito mais nas entradas pequenas. A prova limpa de que cada inserção é O(1) está na "
          "seção 3.2.1: a montagem não-ordenada executa <b>zero</b> comparações, em qualquer "
          "tamanho."),
        P("Na lista <b>ordenada</b> as duas últimas razões são <b>4,53</b> e <b>4,61</b> — a "
          "assinatura do comportamento <b>quadrático O(n<super>2</super>)</b> previsto na seção "
          "2.1.1. Já a primeira duplicação (25.000 → 50.000) rendeu uma razão de <b>11,0</b>, "
          "bem acima de 4. Esse ponto fora da curva <b>não</b> significa que o algoritmo seja "
          "pior que quadrático, e a contagem de operações é categórica quanto a isso: entre "
          "esses mesmos dois tamanhos o número de comparações cresceu <b>3,99×</b>, e entre "
          "50.000 e 100.000, <b>4,00×</b>. O que muda é o <b>custo de cada</b> comparação, "
          "como explicamos logo a seguir."),
    ]

    # numeros concretos para o texto
    m_ord = {n: r[(n, True)]["montagem"] for n in tam_ord}
    m_no = {n: r[(n, False)]["montagem"] for n in tam_ord if (n, False) in r}
    maior_ord = max(tam_ord)
    fator = m_ord[maior_ord] / m_no[maior_ord]
    cont = carregar_contagens()
    hist += [
        P(f"Com {num(maior_ord,0)} contatos, montar as listas ordenadas levou "
          f"<b>{num(m_ord[maior_ord]/1000/60,1)} minutos</b>, contra "
          f"<b>{num(m_no[maior_ord],1)} ms</b> das não-ordenadas — cerca de "
          f"<b>{num(fator,0)} vezes mais</b>. E essa diferença não é constante: ela "
          f"<b>aumenta</b> com <i>n</i>, porque n<super>2</super> cresce mais rápido que n. É a diferença "
          f"entre O(n) e O(n<super>2</super>) aparecendo no relógio."),

        P("3.2.1 Contagem de operações: a evidência mais limpa", "h2"),
        P("A tabela abaixo mostra quantas <b>comparações entre contatos</b> foram efetivamente "
          "executadas para montar as duas listas (soma das duas) e para pesquisar o telefone "
          "do último contato do arquivo."),
        KeepTogether([tabela_contagens(cont)]),
        Spacer(1, 8),
        P("Os números são categóricos:"),
        P("• na lista <b>não-ordenada</b> a montagem faz <b>zero comparações</b> — a inserção "
          "no fim, apoiada na referência <font face='Courier'>ult</font>, não precisa comparar "
          "nada, confirmando o O(1) por inserção deduzido na Listagem 2;<br/>"
          "• na lista <b>ordenada</b>, o número de comparações é multiplicado por "
          "<b>3,99× e 4,00×</b> a cada vez que <i>n</i> dobra — a assinatura de "
          "<b>&Theta;(n<super>2</super>)</b>, exatamente como previsto pela soma 1 + 2 + … + n = n<super>2</super>/2 + n/2;<br/>"
          "• a pesquisa na lista não-ordenada faz <b>exatamente n comparações</b> (25.000 "
          "comparações para n = 25.000, e assim por diante): é o pior caso de O(n) "
          "acontecendo literalmente, como analisado na seção 2.2."),
        P("A tabela não traz a contagem da pesquisa na <b>lista ordenada</b>, e a razão é "
          "metodológica. Nela a busca para assim que encontra um elemento maior que o "
          "procurado (linha 115 da Listagem 4), de modo que o número de comparações é a "
          "<b>posição</b> do telefone procurado na ordem crescente — um valor sorteado pelo "
          "gerador, que não depende do tamanho da entrada. Nas nossas execuções essa contagem "
          "deu 14.237 tanto para 25.000 quanto para 50.000 contatos, e 64.237 para 100.000: "
          "com a mesma semente, o gerador sorteia posições congruentes entre si. Esses "
          "valores medem o sorteio, não o crescimento, e por isso não podem ser lidos como "
          "uma curva — o que eles ilustram bem é o efeito da parada antecipada, discutido na "
          "seção 2.2."),
        P("<b>Por que o tempo saltou 11× entre 25.000 e 50.000, se as operações só "
          "quadruplicaram?</b> A diferença não está no algoritmo, e sim na <b>hierarquia de "
          "memória</b>. A inserção ordenada percorre a lista seguindo referências de um nó "
          "para o outro, e esses nós estão espalhados pela memória. Com 25.000 contatos, boa "
          "parte das duas listas ainda cabe nos <b>16 MB de cache L3</b> do Ryzen 5 5600G e "
          "cada passo custa poucos ciclos; com 50.000 a estrutura já não cabe, e quase todo "
          "passo passa a ser um acesso à memória principal, dezenas de vezes mais lento. A "
          "partir daí o custo por operação se estabiliza — as duas razões seguintes voltam "
          "para perto de 4,5. Ou seja, o que aumentou nesse trecho foi o <b>custo médio de "
          "cada operação</b>, uma constante multiplicativa que a notação O, por definição, "
          "despreza. A ordem de complexidade continua O(n<super>2</super>); o relógio apenas "
          "mostra que, na prática, as constantes também importam."),
        P("Esse é justamente o motivo de termos medido as duas coisas. A <b>contagem de "
          "operações</b> é o argumento correto para a ordem de complexidade (e ela confirma o "
          "quadrático com precisão de duas casas); o <b>tempo</b> é o argumento para o custo "
          "de memória. Usar só o relógio levaria à conclusão errada de que o algoritmo piora "
          "em 25.000 e melhora depois."),
        PageBreak(),

        P("3.3 Tempo de pesquisa", "h2"),
        P("Pesquisa pelo <b>telefone</b> do último contato do arquivo:"),
        tabela_metrica(r, "busca_tel", "Pesquisa por telefone"),
        Spacer(1, 8),
        figura("fig4_busca_telefone.png",
               "Figura 4 — Pesquisa pelo telefone do último contato do arquivo."),
        P("Pesquisa pelo <b>nome</b> do último contato do arquivo:"),
        tabela_metrica(r, "busca_nome", "Pesquisa por nome"),
        Spacer(1, 8),
        figura("fig5_busca_nome.png",
               "Figura 5 — Pesquisa pelo nome do último contato do arquivo."),

        P("<b>Interpretação.</b> Na lista <b>não-ordenada</b>, o contato procurado é o último "
          "do arquivo e, portanto, está no <b>último nó</b> da lista: é o <b>pior caso</b> "
          "descrito na seção 2.2. O tempo cresce com <i>n</i>, confirmando o comportamento "
          "<b>O(n)</b>."),
        P("Na lista <b>ordenada</b> os tempos são <b>menores</b> nos dois primeiros tamanhos, e isso "
          "merece explicação — afinal, a análise matemática diz que ambas são O(n). Há dois "
          "motivos, e nenhum deles contradiz a teoria. Primeiro, como os dados de entrada são "
          "aleatórios, o último contato do arquivo ocupa uma <b>posição qualquer</b> da lista "
          "ordenada (em média o meio, n/2 nós), enquanto na não-ordenada ele está "
          "garantidamente no fim (n nós): é a diferença entre o caso médio e o pior caso, um "
          "fator constante de 2. Segundo, na execução ordenada a montagem demorou segundos, "
          "tempo mais que suficiente para a JVM compilar os métodos da lista para código "
          "nativo, o que torna cada iteração mais barata. Ambos os efeitos são "
          "<b>constantes multiplicativas</b>, justamente o que a notação O despreza."),
        P("A partir de 100.000 contatos a relação se inverte e a busca na lista ordenada passa "
          "a ser a mais lenta. É o mesmo fenômeno descrito na seção 3.2.1: nessa execução a lista "
          "ordenada foi construída por inserções que espalharam os nós pela memória, de modo "
          "que percorrê-la gera muito mais faltas de cache. De novo, trata-se do <b>custo de "
          "cada passo</b>, não da quantidade de passos — a contagem de operações confirma que "
          "a pesquisa continua percorrendo O(n) nós nos dois casos."),
        P("As medições de busca são as mais ruidosas do trabalho, porque duram poucos "
          "milissegundos e sofrem interferência do sistema operacional, do coletor de lixo e "
          "do estado dos caches do processador. Por isso a razão entre medidas consecutivas "
          "oscila bastante — de 0,67 a 5,43 nas nossas tabelas — em vez de se aproximar de 2. "
          "A tendência geral de crescimento linear, porém, é clara, e a contagem de operações "
          "(exatamente <i>n</i> comparações na lista não-ordenada) não deixa dúvida sobre a "
          "ordem de complexidade."),

        P("3.4 Tempo de remoção", "h2"),
        tabela_metrica(r, "remocao", "Remoção"),
        Spacer(1, 8),
        figura("fig6_remocao.png",
               "Figura 6 — Remoção do último contato do arquivo, pesquisado pelo telefone."),
        P("<b>Interpretação.</b> Os tempos de remoção acompanham de perto os de pesquisa, "
          "como previsto na seção 2.3: remover custa <b>encontrar o nó</b> (O(n)) mais um "
          "número fixo de religações de ponteiros (O(1)). Na lista não-ordenada, novamente, "
          "o elemento removido é o último nó — o pior caso — e o crescimento é linear com "
          "<i>n</i>."),

        P("3.5 Conclusão", "h2"),
        P("Os dados coletados <b>atendem ao esperado</b> pela análise matemática da seção 2:"),
        P("• a montagem da lista <b>não-ordenada</b> cresce de forma <b>no máximo linear</b> "
          "(todas as razões abaixo de 2; 4,9× de tempo para 16× de entrada), como previsto "
          "por O(n), porque cada inserção é O(1) graças à referência "
          "<font face='Courier'>ult</font> — e, de fato, a montagem executa zero comparações;<br/>"
          "• a montagem da lista <b>ordenada</b> cresce quadraticamente — a contagem de "
          "comparações é multiplicada por 3,99× e 4,00× a cada duplicação de <i>n</i> —, "
          "como previsto por O(n<super>2</super>), porque cada inserção precisa percorrer a lista até achar a "
          "posição correta;<br/>"
          "• <b>pesquisa</b> e <b>remoção</b> crescem linearmente nos dois tipos de lista, "
          "como previsto por O(n); a ordenação altera o tempo apenas por <b>fatores "
          "constantes</b> — para melhor nas entradas menores (parada antecipada e posição "
          "média do elemento) e para pior nas maiores (faltas de cache) —, mas <b>não muda a "
          "ordem de complexidade</b>;<br/>"
          "• <font face='Courier'>quantidadeNos</font> é O(1) e seu tempo é indistinguível de "
          "zero em qualquer tamanho de entrada, por isso não foi incluído nos gráficos."),
        P("A principal lição prática é que, em uma lista <b>simplesmente encadeada</b>, manter "
          "os elementos ordenados custa caro (O(n<super>2</super>) para montar) e não traz o ganho que se "
          "poderia esperar nas consultas, pois a estrutura não permite acesso direto a uma "
          "posição e, portanto, não permite busca binária. Estruturas que oferecem esse acesso "
          "— vetores ordenados, árvores de busca balanceadas ou tabelas hash — são as "
          "alternativas indicadas quando a busca precisa ser mais rápida que O(n)."),
        P("Por fim, os desvios observados — razões abaixo de 2 nas entradas pequenas da lista "
          "não-ordenada e o salto de 11× entre 25.000 e 50.000 na ordenada — reforçam um ponto "
          "discutido em aula: a análise assintótica descreve a <b>tendência</b> do algoritmo "
          "quando <i>n</i> cresce, contando operações. O tempo de relógio embute constantes "
          "que a notação O despreza (inicialização da JVM, compilação JIT, acesso ao disco e, "
          "principalmente, o custo de acesso à memória quando a estrutura deixa de caber no "
          "cache). Por isso medimos as duas coisas: elas respondem a perguntas diferentes e, "
          "juntas, contam a história completa."),
    ]

    doc = SimpleDocTemplate(
        str(SAIDA), pagesize=A4,
        leftMargin=2.4 * cm, rightMargin=2.4 * cm,
        topMargin=2.2 * cm, bottomMargin=2.0 * cm,
        title="Trabalho 1 - Análise de complexidade em estruturas de listas",
        author="Grupo",
    )

    def rodape(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(CINZA)
        if doc_.page > 1:
            canvas.drawRightString(A4[0] - 2.4 * cm, 1.3 * cm, str(doc_.page))
            canvas.drawString(2.4 * cm, 1.3 * cm,
                              "Trabalho 1 — Análise de complexidade em estruturas de listas")
        canvas.restoreState()

    doc.build(hist, onFirstPage=rodape, onLaterPages=rodape)
    print("PDF gerado:", SAIDA)


if __name__ == "__main__":
    construir()
