package colecao;

/**
 * Interface que define o contrato mínimo de uma coleção.
 *
 * @author victoriocarvalho
 * @param <T> tipo dos elementos armazenados
 */
public interface IColecao<T> {

    /**
     * Adiciona um elemento à estrutura.
     *
     * @param novoValor elemento do tipo T a ser armazenado.
     * @return true caso o elemento tenha sido adicionado; caso contrário false.
     */
    public boolean adicionar(T novoValor);

    /**
     * Pesquisa um elemento na estrutura e o retorna.
     *
     * @param valor objeto contendo a chave a ser buscada.
     * @return o elemento encontrado ou null.
     */
    public T pesquisar(T valor);

    /**
     * Busca um elemento e, caso encontre, o remove da estrutura.
     *
     * @param valor objeto contendo a chave a ser buscada.
     * @return true se removeu; false caso contrário.
     */
    public boolean remover(T valor);

    /**
     * @return a quantidade de nós da estrutura.
     */
    public int quantidadeNos();
}
