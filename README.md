# Trabalho 2 — Árvores Binárias e Análise de Complexidade

Biblioteca de **árvore binária de busca genérica** em Java (especializando a classe
`ArvoreBinariaBase` fornecida pelo professor), a agenda de contatos do Trabalho 1
adaptada para usar listas **ou** árvores, e os programas usados na análise
empírica de complexidade.

Disciplina: Técnicas de Programação Avançada — IFES Campus Serra
Professor: Victorio Albani de Carvalho
Grupo: Lucas Ramos Pianissola, Ryan Lima Peçanha, Davi Alvarenga

Inclui também a **árvore AVL**, que herda da árvore binária e sobrescreve
`adicionar` e `remover` para manter a árvore balanceada.

---

## 1. Organização do código

```
trabalho2/
├── README.md
├── src/
│   ├── colecao/                        <- reaproveitado do Trabalho 1
│   │   ├── IColecao.java               interface comum (fornecida pelo professor)
│   │   ├── No.java                     nó da lista encadeada
│   │   └── ListaEncadeada.java         lista genérica, ordenada ou não
│   ├── arvorebinaria/                  <- a BIBLIOTECA DE ÁRVORES (não imprime nada)
│   │   ├── ArvoreBinariaBase.java      classe abstrata do professor, preservada
│   │   ├── NoArvore.java               nó: valor, esquerda, direita e altura
│   │   ├── ArvoreBinaria.java          árvore binária de busca (sem balanceamento)
│   │   └── ArvoreAVL.java              AVL: herda da anterior e rebalanceia
│   └── app/
│       ├── Contato.java                classe de domínio (nome, telefone)
│       ├── ComparadorContatoPorNome.java
│       ├── ComparadorContatoPorTelefone.java
│       ├── Programa.java               agenda: lista não-ordenada, ordenada ou árvore
│       ├── GeradorArquivo.java         gera entradas crescente/balanceada/aleatória
│       ├── Benchmark.java              uma rodada de medição de tempo (CSV)
│       ├── ComparadorContador.java     decorator que conta comparações
│       ├── ContagemOperacoes.java      conta comparações em vez de medir tempo
│       ├── TesteArvore.java            testes da árvore binária
│       └── TesteAVL.java               testes da AVL (rotações e propriedade AVL)
├── analise/                            scripts dos gráficos e do PDF
├── dados/                              arquivos de entrada e CSVs das medições
├── medir.ps1                           script PowerShell que roda todas as medições
└── relatorio/Relatorio_Trabalho2.pdf    relatório completo (seções 1 a 6)
```

## 2. A biblioteca de árvores

```java
ArvoreBinaria<Contato> arvore = new ArvoreBinaria<>(new ComparadorContatoPorNome());
```

`ArvoreBinaria<T> extends ArvoreBinariaBase<T>`, que por sua vez implementa
`IColecao<T>`. O comparador é recebido no construtor (atributo `comparador`,
herdado da classe base), o que permite criar várias árvores do mesmo tipo
indexadas por critérios diferentes.

Métodos da interface: `adicionar`, `pesquisar`, `remover`, `quantidadeNos`.
Métodos exigidos pela classe base: `altura`, `caminharEmNivel`, `caminharEmOrdem`
(e `toString`, herdado, devolve o caminhamento em ordem).
Método auxiliar da análise empírica: `valorDaFolhaMaisProfunda()`.

**Decisões de implementação**

* **Na árvore binária, todos os percursos são iterativos, não recursivos.** Uma árvore degenerada
  com 200.000 nós tem altura 199.999; uma implementação recursiva estouraria a
  pilha da JVM (`StackOverflowError`). A inserção, a busca e a remoção descem com
  laços; `altura` e `caminharEmNivel` usam uma fila; `caminharEmOrdem` usa uma
  pilha explícita.
* **Elementos de chave igual são inseridos à direita**, mesma convenção dos
  exemplos em C vistos em aula.
* **Remoção de nó com dois filhos pelo predecessor** (o maior elemento da
  subárvore esquerda), também como no exemplo da disciplina.
* **Contador de nós** mantido na inserção e na remoção, para que
  `quantidadeNos()` seja O(1).
* **Na AVL, inserção e remoção são recursivas**, no estilo das funções
  `inserirV2`/`removerV2` vistas em aula: cada chamada devolve a nova raiz da
  subárvore. É seguro porque a AVL garante altura O(log n) (cerca de 25 níveis
  para 200.000 elementos). O fator de balanceamento é derivado da altura
  guardada em cada nó.

## 3. A agenda (`app.Programa`)

Ao iniciar, o programa pergunta qual estrutura usar:

```
1 - Lista encadeada NAO-ordenada
2 - Lista encadeada ORDENADA
3 - Arvore binaria de busca
4 - Arvore AVL (binaria balanceada)
```

Como todas implementam `IColecao`, **nenhuma outra parte do programa precisou ser
alterada** em relação ao Trabalho 1. O menu, a carga de arquivo, as buscas, a
remoção, a alteração e a medição de tempos continuam idênticos.

Formato do arquivo de entrada (uma linha por contato):

```
Contato 0000007;27900000007
```

## 4. Como compilar e executar

Requisito: JDK 17 ou superior (desenvolvido e testado com o OpenJDK 21).

```bash
# compilar
javac -d build $(find src -name "*.java")

# testes das bibliotecas de árvores
java -cp build app.TesteArvore
java -cp build app.TesteAVL

# executar a agenda
java -cp build app.Programa

# gerar arquivos de entrada (modo: crescente | balanceado | aleatorio)
java -cp build app.GeradorArquivo 100000 dados/cres_100000.txt crescente
java -cp build app.GeradorArquivo 100000 dados/bal_100000.txt  balanceado

# medir (estrutura: arvore | avl | lista_nao_ordenada | lista_ordenada)
java -cp build app.Benchmark dados/bal_100000.txt arvore
java -cp build app.Benchmark dados/cres_100000.txt avl

# contar comparações em vez de medir tempo (3o argumento "avl" usa a AVL)
java -cp build app.ContagemOperacoes dados/bal_100000.txt arvore_balanceada
java -cp build app.ContagemOperacoes dados/cres_100000.txt avl_crescente avl

# gerar os gráficos e o PDF do relatório (requer matplotlib e reportlab)
python3 analise/gerar_graficos.py
python3 analise/gerar_relatorio.py
```

Saída do `Benchmark` (CSV separado por `;`):

```
estrutura;n;montagem_ms;altura_tel;altura_nome;busca_tel_ms;busca_nome_ms;remocao_ms;achouTel;achouNome;removeu
```

Cada medição roda em uma **JVM nova**, e os números são impressos com
`Locale.US` para que o separador decimal seja sempre o ponto, independentemente
do idioma do sistema operacional.

## 5. Relatório

`relatorio/Relatorio_Trabalho2.pdf` — seções 1 (desenvolvimento), 2 (análise
matemática da árvore binária), 3 (análise empírica da árvore binária),
4 (análise da AVL), 5 (desempenho da AVL) e 6 (árvores na biblioteca padrão
de Java).
