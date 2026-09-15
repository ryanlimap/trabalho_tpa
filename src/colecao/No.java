package colecao;

/**
 * Nó genérico de uma lista encadeada simples.
 *
 * @param <T> tipo do valor armazenado no nó.
 */
public class No<T> {

    private T valor;
    private No<T> prox;

    public No(T valor) {
        this.valor = valor;
        this.prox = null;
    }

    public T getValor() {
        return valor;
    }

    public void setValor(T valor) {
        this.valor = valor;
    }

    public No<T> getProx() {
        return prox;
    }

    public void setProx(No<T> prox) {
        this.prox = prox;
    }
}
