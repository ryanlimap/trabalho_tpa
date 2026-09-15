package colecao;

import java.util.Comparator;
import java.util.Iterator;
import java.util.NoSuchElementException;

/**
 * Lista encadeada simples e genérica, com opção de manter os elementos
 * ordenados. A comparação entre elementos é delegada a um Comparator<T>
 * informado na construção da lista.
 *
 * A lista NÃO imprime nada: toda interação com o usuário é responsabilidade
 * do programa cliente.
 *
 * @param <T> tipo dos elementos armazenados.
 */
public class ListaEncadeada<T> implements IColecao<T>, Iterable<T> {

    private No<T> prim;
    private No<T> ult;
    private int quant;
    private final boolean ordenada;
    private final Comparator<T> comparador;

    /**
     * @param comparador comparador usado sempre que for preciso comparar
     *                   elementos (ordenação e busca).
     * @param ordenada   true para lista ordenada; false para não-ordenada.
     */
    public ListaEncadeada(Comparator<T> comparador, boolean ordenada) {
        this.prim = null;
        this.ult = null;
        this.quant = 0;
        this.ordenada = ordenada;
        this.comparador = comparador;
    }

    public boolean isOrdenada() {
        return this.ordenada;
    }

    // ------------------------------------------------------------------
    // ADICIONAR
    // ------------------------------------------------------------------

    @Override
    public boolean adicionar(T novoValor) {
        if (novoValor == null) {
            return false;
        }
        if (this.ordenada) {
            adicionarOrdenado(novoValor);
        } else {
            adicionarNaoOrdenado(novoValor);
        }
        this.quant++;
        return true;
    }

    /**
     * Insere sempre no fim da lista, usando a referência ult.
     */
    private void adicionarNaoOrdenado(T novoValor) {
        No<T> novo = new No<>(novoValor);
        if (this.prim == null) {
            this.prim = novo;
            this.ult = novo;
        } else {
            this.ult.setProx(novo);
            this.ult = novo;
        }
    }

    /**
     * Percorre a lista até achar a posição de inserção que mantém a ordem
     * crescente definida pelo comparador.
     */
    private void adicionarOrdenado(T novoValor) {
        No<T> novo = new No<>(novoValor);
        No<T> atual = this.prim;
        No<T> ant = null;
        if (this.prim == null) {
            this.prim = novo;
            this.ult = novo;
            return;
        }
        while (atual != null && comparador.compare(atual.getValor(), novoValor) < 0) {
            ant = atual;
            atual = atual.getProx();
        }
        if (ant == null) {
            novo.setProx(this.prim);
            this.prim = novo;
        } else if (atual == null) {
            this.ult.setProx(novo);
            this.ult = novo;
        } else {
            ant.setProx(novo);
            novo.setProx(atual);
        }
    }

    // ------------------------------------------------------------------
    // PESQUISAR
    // ------------------------------------------------------------------

    @Override
    public T pesquisar(T valor) {
        No<T> aux = this.prim;
        while (aux != null) {
            int cmp = comparador.compare(aux.getValor(), valor);
            if (cmp == 0) {
                return aux.getValor();
            }
            if (this.ordenada && cmp > 0) {
                return null;
            }
            aux = aux.getProx();
        }
        return null;
    }

    // ------------------------------------------------------------------
    // REMOVER
    // ------------------------------------------------------------------

    @Override
    public boolean remover(T valor) {
        No<T> aux = this.prim;
        No<T> ant = null;
        while (aux != null) {
            int cmp = comparador.compare(aux.getValor(), valor);
            if (cmp == 0) {
                if (ant == null) {
                    this.prim = aux.getProx();
                } else {
                    ant.setProx(aux.getProx());
                }
                if (aux == this.ult) {
                    this.ult = ant;
                }
                this.quant--;
                return true;
            }
            if (this.ordenada && cmp > 0) {
                return false;
            }
            ant = aux;
            aux = aux.getProx();
        }
        return false;
    }

    // ------------------------------------------------------------------
    // QUANTIDADE DE NÓS
    // ------------------------------------------------------------------

    @Override
    public int quantidadeNos() {
        return this.quant;
    }

    // ------------------------------------------------------------------
    // Iterator (percorre a lista do primeiro ao ultimo)
    // ------------------------------------------------------------------

    @Override
    public Iterator<T> iterator() {
        return new Iterator<T>() {
            private No<T> atual = prim;

            @Override
            public boolean hasNext() {
                return atual != null;
            }

            @Override
            public T next() {
                if (atual == null) {
                    throw new NoSuchElementException();
                }
                T v = atual.getValor();
                atual = atual.getProx();
                return v;
            }
        };
    }

    // ------------------------------------------------------------------
    // toString
    // ------------------------------------------------------------------

    @Override
    public String toString() {
        StringBuilder s = new StringBuilder("[");
        No<T> aux = this.prim;
        while (aux != null) {
            s.append(aux.getValor());
            if (aux != this.ult) {
                s.append(",");
            }
            aux = aux.getProx();
        }
        return s.append("]").toString();
    }
}
