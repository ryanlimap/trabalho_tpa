package app;

import java.util.Comparator;

/**
 * Compara contatos pelo nome (chave da lista indexada por nome).
 */
public class ComparadorContatoPorNome implements Comparator<Contato> {

    @Override
    public int compare(Contato c1, Contato c2) {
        return c1.getNome().compareTo(c2.getNome());
    }
}
