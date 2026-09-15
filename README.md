# Trabalho 1 — Análise de complexidade em estruturas de listas

Biblioteca de **lista encadeada genérica** em Java (com opção de ordenação via
`Comparator`) e uma **agenda de contatos** que a utiliza, além dos programas
usados na análise empírica de complexidade.

Disciplina: Técnicas de Programação Avançada — IFES Campus Serra
Professor: Victorio Albani de Carvalho

---

## 1. Organização do código

```
trabalho1/
├── README.md
├── src/
│   ├── colecao/                      <- a BIBLIOTECA (não imprime nada)
│   │   ├── IColecao.java             interface exigida pelo trabalho
│   │   ├── No.java                   nó genérico (valor + próximo)
│   │   └── ListaEncadeada.java       lista genérica, ordenada ou não
│   └── app/                          <- programas que USAM a biblioteca
│       ├── Contato.java              classe de domínio (nome, telefone)
│       ├── ComparadorContatoPorNome.java
│       ├── ComparadorContatoPorTelefone.java
│       ├── Programa.java             agenda com o menu interativo
│       ├── GeradorArquivo.java       gera arquivos de entrada aleatórios
│       ├── Benchmark.java            uma rodada da análise empírica (tempos)
│       ├── ComparadorContador.java   decorator que conta chamadas ao comparador
│       └── ContagemOperacoes.java    conta comparações em vez de medir tempo
├── analise/
│   ├── gerar_graficos.py             gráficos do relatório (matplotlib)
│   ├── gerar_relatorio.py            monta o PDF do relatório (ReportLab)
│   └── figuras/                      PNGs gerados
├── dados/                            arquivos de entrada e medições (CSV)
└── relatorio/Relatorio_Trabalho1.pdf
```

Separação de responsabilidades: **nenhuma classe do pacote `colecao` imprime
mensagens**. Toda interação com o usuário está em `app.Programa`.

## 2. A biblioteca

`ListaEncadeada<T> implements IColecao<T>, Iterable<T>`

Construtor:

```java
new ListaEncadeada<>(Comparator<T> comparador, boolean ordenada)
```

* `comparador` — usado sempre que for preciso comparar elementos (inserção
  ordenada, pesquisa e remoção);
* `ordenada` — `true` mantém a lista ordenada a cada inserção; `false` insere
  sempre no fim (atributo `final`, definido na criação).

Métodos da interface: `adicionar`, `pesquisar`, `remover`, `quantidadeNos`.
Além deles, `toString()` devolve `[elem1,elem2,...]` e `iterator()` permite
percorrer a lista com `for-each`.

Atributos internos: `prim`, `ult` (referência para o último nó, que torna a
inserção no fim O(1)) e `quant` (contador que torna `quantidadeNos()` O(1)).

## 3. A agenda (`app.Programa`)

Ao iniciar, o programa pergunta se as listas devem ser ordenadas e cria
**duas listas** com as **mesmas instâncias** de `Contato` (não há duplicação de
objetos): uma indexada por nome e outra por telefone.

Menu:

1. Carregar dados de arquivo — exibe o tempo total de leitura + montagem;
2. Adicionar contato — recusa telefone já existente (regra de negócio, fora da biblioteca);
3. Pesquisar por nome — exibe o telefone e o tempo da busca;
4. Pesquisar por telefone — exibe o nome e o tempo da busca;
5. Remover por telefone — exibe o resultado e o tempo da remoção;
6. Alterar dados — remove, altera e reinsere (as chaves das duas listas mudam);
7. Sair — exibe a quantidade total de contatos.

**Formato do arquivo de entrada** (`entrada.txt`), uma linha por contato:

```
Ana Ribeiro 240409;27900005056
Lucas Teixeira 946305;27900023972
```

Observação sobre homônimos: a lista indexada por nome compara apenas pelo nome,
então, se houver contatos de mesmo nome, remover "pela chave nome" poderia
retirar o homônimo errado. O método `removerInstanciaDaListaPorNome` trata isso
retirando temporariamente os homônimos anteriores ao alvo e reinserindo-os.

## 4. Como compilar e executar

Requisito: JDK 17 ou superior (desenvolvido e testado com o OpenJDK 21).

```bash
# compilar
javac -d build $(find src -name "*.java")

# executar a agenda
java -cp build app.Programa

# gerar um arquivo de entrada com 100.000 contatos
java -cp build app.GeradorArquivo 100000 dados/entrada_100000.txt 7

# rodar uma medição (arquivo, lista ordenada?)  -> imprime uma linha CSV
java -cp build app.Benchmark dados/entrada_100000.txt false

# contar comparações em vez de medir tempo
java -cp build app.ContagemOperacoes dados/entrada_100000.txt true

# gerar os gráficos e o PDF do relatório (requer matplotlib e reportlab)
python3 analise/gerar_graficos.py dados/resultados.csv analise/figuras
python3 analise/gerar_relatorio.py
```

Saída do `Benchmark` (CSV separado por `;`):

```
n;ordenada;montagem_ms;busca_tel_ms;busca_nome_ms;remocao_ms;achouTel;achouNome;removeu
```

Cada medição é feita em uma **JVM nova**, para que uma execução não interfira na
seguinte.

## 5. Relatório

O relatório com as análises matemática e empírica está em
`relatorio/Relatorio_Trabalho1.pdf`.
