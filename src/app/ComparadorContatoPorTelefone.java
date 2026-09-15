package app;

import java.util.Comparator;

/**
 * Compara contatos pelo telefone (chave da lista indexada por telefone).
 */
public class ComparadorContatoPorTelefone implements Comparator<Contato> {

    @Override
    public int compare(Contato c1, Contato c2) {
        return c1.getTelefone().compareTo(c2.getTelefone());
    }
}
