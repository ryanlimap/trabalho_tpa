package arvorebinaria;

/**
 * Nó de uma árvore binária: guarda um valor e as referências para as duas
 * subárvores (esquerda e direita).
 *
 * @param <T> tipo do valor armazenado.
 */
public class NoArvore<T> {

    private T valor;
    private NoArvore<T> esq;
    private NoArvore<T> dir;
    /**
     * Altura da subárvore que começa neste nó (folha = 0). Só é mantida pela
     * ArvoreAVL, que a usa para calcular o fator de balanceamento; a árvore
     * binária comum ignora este campo.
     */
    private int altura;

    public NoArvore(T valor) {
        this.valor = valor;
        this.esq = null;
        this.dir = null;
        this.altura = 0;
    }

    public int getAltura() {
        return altura;
    }

    public void setAltura(int altura) {
        this.altura = altura;
    }

    public T getValor() {
        return valor;
    }

    public void setValor(T valor) {
        this.valor = valor;
    }

    public NoArvore<T> getEsq() {
        return esq;
    }

    public void setEsq(NoArvore<T> esq) {
        this.esq = esq;
    }

    public NoArvore<T> getDir() {
        return dir;
    }

    public void setDir(NoArvore<T> dir) {
        this.dir = dir;
    }

    /** @return true se o nó não tem nenhum filho. */
    public boolean ehFolha() {
        return this.esq == null && this.dir == null;
    }
}
