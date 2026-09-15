package app;

import java.util.Comparator;

/**
 * Decorator que conta quantas vezes o comparador foi chamado. Usado apenas na
 * analise empirica, para medir o NUMERO DE OPERACOES (independente do tempo de
 * relogio e dos efeitos de cache do processador).
 */
public class ComparadorContador<T> implements Comparator<T> {

    private final Comparator<T> interno;
    private long chamadas = 0;

    public ComparadorContador(Comparator<T> interno) {
        this.interno = interno;
    }

    @Override
    public int compare(T o1, T o2) {
        this.chamadas++;
        return interno.compare(o1, o2);
    }

    public long getChamadas() {
        return chamadas;
    }

    public void zerar() {
        this.chamadas = 0;
    }
}
