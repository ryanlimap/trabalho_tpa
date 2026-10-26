package arvorebinaria;

import java.util.Comparator;

/**
 * Árvore AVL: uma árvore binária de busca que se reequilibra após cada
 * inserção e cada remoção, garantindo altura O(log n) para QUALQUER ordem de
 * entrada — inclusive a ordem crescente, que degenera a árvore binária comum.
 *
 * Herda de ArvoreBinaria e sobrescreve apenas adicionar e remover; pesquisar,
 * quantidadeNos, altura e os caminhamentos são reaproveitados sem alteração,
 * porque uma AVL continua sendo uma árvore binária de busca.
 *
 * O critério de equilíbrio é o <b>fator de balanceamento</b> de cada nó:
 *
 *      fb(no) = altura(subárvore esquerda) - altura(subárvore direita)
 *
 * A árvore é AVL enquanto |fb| <= 1 em todos os nós. Guardamos a altura dentro
 * do próprio nó (campo altura de NoArvore) e derivamos o fb a partir dela, o
 * que torna a atualização trivial tanto na inserção quanto na remoção.
 *
 * Inserção e remoção são recursivas, no mesmo estilo das funções inserirV2 e
 * removerV2 vistas em aula: cada chamada devolve a nova raiz da subárvore. Isso
 * é seguro aqui (diferentemente da árvore binária comum) justamente porque a
 * AVL garante altura O(log n): com 200.000 elementos a recursão desce no
 * máximo cerca de 25 níveis.
 *
 * @param <T> tipo dos elementos armazenados.
 */
public class ArvoreAVL<T> extends ArvoreBinaria<T> {

    /** Sinaliza se a última chamada a remover encontrou o elemento. */
    private boolean removeuElemento;

    public ArvoreAVL(Comparator<T> comparador) {
        super(comparador);
    }

    // ------------------------------------------------------------------
    // ADICIONAR (sobrescrito)
    // ------------------------------------------------------------------

    @Override
    public boolean adicionar(T novoValor) {
        if (novoValor == null) {
            return false;
        }
        this.raiz = inserir(this.raiz, novoValor);
        this.quant++;
        return true;
    }

    private NoArvore<T> inserir(NoArvore<T> no, T novoValor) {
        if (no == null) {
            return new NoArvore<>(novoValor);
        }
        if (comparador.compare(no.getValor(), novoValor) > 0) {
            no.setEsq(inserir(no.getEsq(), novoValor));
        } else {
            no.setDir(inserir(no.getDir(), novoValor));
        }
        atualizarAltura(no);
        return balancear(no);
    }

    // ------------------------------------------------------------------
    // REMOVER (sobrescrito)
    // ------------------------------------------------------------------

    @Override
    public boolean remover(T valor) {
        this.removeuElemento = false;
        this.raiz = remover(this.raiz, valor);
        if (this.removeuElemento) {
            this.quant--;
        }
        return this.removeuElemento;
    }

    private NoArvore<T> remover(NoArvore<T> no, T valor) {
        if (no == null) {
            return null;
        }
        int cmp = comparador.compare(no.getValor(), valor);
        if (cmp > 0) {
            no.setEsq(remover(no.getEsq(), valor));
        } else if (cmp < 0) {
            no.setDir(remover(no.getDir(), valor));
        } else {
            this.removeuElemento = true;
            // Caso 1 e 2: nó folha ou com um único filho.
            if (no.getEsq() == null) {
                return no.getDir();
            }
            if (no.getDir() == null) {
                return no.getEsq();
            }
            // Caso 3: dois filhos. Mesma estratégia da árvore binária comum —
            // o nó recebe o valor do predecessor (o maior da subárvore
            // esquerda) e o predecessor é removido da subárvore esquerda.
            NoArvore<T> predecessor = no.getEsq();
            while (predecessor.getDir() != null) {
                predecessor = predecessor.getDir();
            }
            T valorPredecessor = predecessor.getValor();
            no.setValor(valorPredecessor);
            no.setEsq(removerPredecessor(no.getEsq()));
        }
        atualizarAltura(no);
        return balancear(no);
    }

    /** Remove o nó mais à direita da subárvore, rebalanceando na volta. */
    private NoArvore<T> removerPredecessor(NoArvore<T> no) {
        if (no.getDir() == null) {
            return no.getEsq();
        }
        no.setDir(removerPredecessor(no.getDir()));
        atualizarAltura(no);
        return balancear(no);
    }

    // ------------------------------------------------------------------
    // BALANCEAMENTO
    // ------------------------------------------------------------------

    /** Altura da subárvore; -1 para subárvore vazia. */
    private int alturaDe(NoArvore<T> no) {
        return (no == null) ? -1 : no.getAltura();
    }

    private void atualizarAltura(NoArvore<T> no) {
        no.setAltura(1 + Math.max(alturaDe(no.getEsq()), alturaDe(no.getDir())));
    }

    /**
     * @return o fator de balanceamento do nó: altura da subárvore esquerda
     *         menos altura da subárvore direita.
     */
    private int fatorBalanceamento(NoArvore<T> no) {
        return alturaDe(no.getEsq()) - alturaDe(no.getDir());
    }

    /**
     * Aplica, se necessário, uma das quatro rotações que restauram a
     * propriedade AVL no nó recebido.
     */
    private NoArvore<T> balancear(NoArvore<T> no) {
        int fb = fatorBalanceamento(no);
        if (fb > 1) {
            // Desequilíbrio à esquerda.
            if (fatorBalanceamento(no.getEsq()) < 0) {
                no.setEsq(rotacaoEsquerda(no.getEsq()));   // caso esquerda-direita
            }
            return rotacaoDireita(no);                     // caso esquerda-esquerda
        }
        if (fb < -1) {
            // Desequilíbrio à direita.
            if (fatorBalanceamento(no.getDir()) > 0) {
                no.setDir(rotacaoDireita(no.getDir()));    // caso direita-esquerda
            }
            return rotacaoEsquerda(no);                    // caso direita-direita
        }
        return no;
    }

    /**
     * Rotação simples à direita: o filho esquerdo sobe e passa a ser a raiz
     * da subárvore.
     *
     *        no                 esq
     *       /  \               /   \
     *     esq   C    ==>      A    no
     *     / \                      / \
     *    A   B                    B   C
     */
    private NoArvore<T> rotacaoDireita(NoArvore<T> no) {
        NoArvore<T> esq = no.getEsq();
        no.setEsq(esq.getDir());
        esq.setDir(no);
        atualizarAltura(no);
        atualizarAltura(esq);
        return esq;
    }

    /**
     * Rotação simples à esquerda: o filho direito sobe e passa a ser a raiz
     * da subárvore.
     *
     *      no                     dir
     *     /  \                   /   \
     *    A   dir      ==>      no     C
     *        / \               / \
     *       B   C             A   B
     */
    private NoArvore<T> rotacaoEsquerda(NoArvore<T> no) {
        NoArvore<T> dir = no.getDir();
        no.setDir(dir.getEsq());
        dir.setEsq(no);
        atualizarAltura(no);
        atualizarAltura(dir);
        return dir;
    }

    // ------------------------------------------------------------------
    // APOIO AOS TESTES
    // ------------------------------------------------------------------

    /**
     * Verifica, percorrendo toda a árvore, se a propriedade AVL vale em todos
     * os nós (|fb| &lt;= 1) e se as alturas armazenadas estão corretas.
     *
     * @return true se a árvore é uma AVL válida.
     */
    public boolean ehAvlValida() {
        return verificar(this.raiz) >= -1;
    }

    /** @return a altura do nó se a subárvore é válida; -2 em caso de erro. */
    private int verificar(NoArvore<T> no) {
        if (no == null) {
            return -1;
        }
        int he = verificar(no.getEsq());
        int hd = verificar(no.getDir());
        if (he == -2 || hd == -2) {
            return -2;
        }
        if (Math.abs(he - hd) > 1) {
            return -2;
        }
        int altura = 1 + Math.max(he, hd);
        return (altura == no.getAltura()) ? altura : -2;
    }
}
