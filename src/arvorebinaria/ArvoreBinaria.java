package arvorebinaria;

import java.util.ArrayDeque;
import java.util.Comparator;
import java.util.Deque;

/**
 * Árvore binária de busca genérica, não balanceada.
 *
 * A comparação entre elementos é delegada ao Comparator recebido no construtor
 * (herdado de ArvoreBinariaBase), o que permite criar várias árvores do mesmo
 * tipo indexadas por critérios diferentes.
 *
 * Todos os percursos são ITERATIVOS, e não recursivos: uma árvore degenerada
 * com n nós tem altura n-1, e uma implementação recursiva estouraria a pilha
 * da JVM (StackOverflowError) muito antes dos tamanhos usados nos testes.
 *
 * Elementos com chave igual são inseridos na subárvore DIREITA.
 *
 * @param <T> tipo dos elementos armazenados.
 */
public class ArvoreBinaria<T> extends ArvoreBinariaBase<T> {

    /** Protegidos para que a ArvoreAVL, que herda desta classe, possa
     *  substituir a raiz após o rebalanceamento e manter o contador. */
    protected NoArvore<T> raiz;
    protected int quant;

    public ArvoreBinaria(Comparator<T> comparador) {
        super(comparador);
        this.raiz = null;
        this.quant = 0;
    }

    // ------------------------------------------------------------------
    // ADICIONAR
    // ------------------------------------------------------------------

    @Override
    public boolean adicionar(T novoValor) {
        if (novoValor == null) {
            return false;
        }
        NoArvore<T> novo = new NoArvore<>(novoValor);
        if (this.raiz == null) {
            this.raiz = novo;
            this.quant++;
            return true;
        }
        NoArvore<T> atual = this.raiz;
        while (true) {
            if (comparador.compare(atual.getValor(), novoValor) > 0) {
                if (atual.getEsq() == null) {
                    atual.setEsq(novo);
                    break;
                }
                atual = atual.getEsq();
            } else {
                if (atual.getDir() == null) {
                    atual.setDir(novo);
                    break;
                }
                atual = atual.getDir();
            }
        }
        this.quant++;
        return true;
    }

    // ------------------------------------------------------------------
    // PESQUISAR
    // ------------------------------------------------------------------

    @Override
    public T pesquisar(T valor) {
        NoArvore<T> atual = this.raiz;
        while (atual != null) {
            int cmp = comparador.compare(atual.getValor(), valor);
            if (cmp == 0) {
                return atual.getValor();
            }
            atual = (cmp > 0) ? atual.getEsq() : atual.getDir();
        }
        return null;
    }

    // ------------------------------------------------------------------
    // REMOVER
    // ------------------------------------------------------------------

    @Override
    public boolean remover(T valor) {
        NoArvore<T> pai = null;
        NoArvore<T> atual = this.raiz;
        while (atual != null) {
            int cmp = comparador.compare(atual.getValor(), valor);
            if (cmp == 0) {
                break;
            }
            pai = atual;
            atual = (cmp > 0) ? atual.getEsq() : atual.getDir();
        }
        if (atual == null) {
            return false;
        }
        // Caso 3: dois filhos. Seguindo a mesma estratégia vista em aula, o nó
        // recebe o valor do seu PREDECESSOR (o maior valor da subárvore
        // esquerda) e passa-se a remover o nó do predecessor, que por ser o
        // mais à direita da subárvore esquerda tem no máximo um filho.
        if (atual.getEsq() != null && atual.getDir() != null) {
            NoArvore<T> paiPredecessor = atual;
            NoArvore<T> predecessor = atual.getEsq();
            while (predecessor.getDir() != null) {
                paiPredecessor = predecessor;
                predecessor = predecessor.getDir();
            }
            atual.setValor(predecessor.getValor());
            pai = paiPredecessor;
            atual = predecessor;
        }
        // Casos 1 e 2: folha (filho == null) ou um único filho.
        NoArvore<T> filho = (atual.getEsq() != null) ? atual.getEsq() : atual.getDir();
        if (pai == null) {
            this.raiz = filho;
        } else if (pai.getEsq() == atual) {
            pai.setEsq(filho);
        } else {
            pai.setDir(filho);
        }
        this.quant--;
        return true;
    }

    // ------------------------------------------------------------------
    // QUANTIDADE DE NÓS
    // ------------------------------------------------------------------

    @Override
    public int quantidadeNos() {
        return this.quant;
    }

    // ------------------------------------------------------------------
    // ALTURA
    // ------------------------------------------------------------------

    @Override
    public int altura() {
        if (this.raiz == null) {
            return -1;
        }
        int altura = -1;
        Deque<NoArvore<T>> fila = new ArrayDeque<>();
        fila.add(this.raiz);
        while (!fila.isEmpty()) {
            int doNivel = fila.size();
            altura++;
            for (int i = 0; i < doNivel; i++) {
                NoArvore<T> no = fila.poll();
                if (no.getEsq() != null) {
                    fila.add(no.getEsq());
                }
                if (no.getDir() != null) {
                    fila.add(no.getDir());
                }
            }
        }
        return altura;
    }

    // ------------------------------------------------------------------
    // CAMINHAMENTOS
    // ------------------------------------------------------------------

    @Override
    public String caminharEmNivel() {
        StringBuilder s = new StringBuilder("[");
        if (this.raiz != null) {
            Deque<NoArvore<T>> fila = new ArrayDeque<>();
            fila.add(this.raiz);
            while (!fila.isEmpty()) {
                int doNivel = fila.size();
                for (int i = 0; i < doNivel; i++) {
                    NoArvore<T> no = fila.poll();
                    s.append(no.getValor());
                    if (i < doNivel - 1) {
                        s.append(",");
                    }
                    if (no.getEsq() != null) {
                        fila.add(no.getEsq());
                    }
                    if (no.getDir() != null) {
                        fila.add(no.getDir());
                    }
                }
                if (!fila.isEmpty()) {
                    s.append("\n");
                }
            }
        }
        return s.append("]").toString();
    }

    @Override
    public String caminharEmOrdem() {
        StringBuilder s = new StringBuilder("[");
        Deque<NoArvore<T>> pilha = new ArrayDeque<>();
        NoArvore<T> atual = this.raiz;
        boolean primeiro = true;
        while (atual != null || !pilha.isEmpty()) {
            while (atual != null) {
                pilha.push(atual);
                atual = atual.getEsq();
            }
            atual = pilha.pop();
            if (!primeiro) {
                s.append(",");
            }
            s.append(atual.getValor());
            primeiro = false;
            atual = atual.getDir();
        }
        return s.append("]").toString();
    }

    // ------------------------------------------------------------------
    // APOIO À ANÁLISE EMPÍRICA
    // ------------------------------------------------------------------

    /**
     * Devolve o valor guardado em uma folha de profundidade máxima, ou seja, o
     * elemento cuja busca percorre o caminho mais longo da raiz até uma folha.
     * É o PIOR CASO de busca com sucesso nesta árvore.
     *
     * @return o valor da folha mais distante da raiz, ou null se a árvore
     *         estiver vazia.
     */
    public T valorDaFolhaMaisProfunda() {
        if (this.raiz == null) {
            return null;
        }
        NoArvore<T> ultimo = this.raiz;
        Deque<NoArvore<T>> fila = new ArrayDeque<>();
        fila.add(this.raiz);
        while (!fila.isEmpty()) {
            NoArvore<T> no = fila.poll();
            ultimo = no;
            if (no.getEsq() != null) {
                fila.add(no.getEsq());
            }
            if (no.getDir() != null) {
                fila.add(no.getDir());
            }
        }
        return ultimo.getValor();
    }
}
