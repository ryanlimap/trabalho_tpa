package app;

import colecao.IColecao;
import colecao.ListaEncadeada;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Locale;

/**
 * Conta o NUMERO DE COMPARACOES executadas ao montar a lista e ao pesquisar,
 * em vez de medir tempo. Serve para verificar a ordem de crescimento do
 * algoritmo sem a interferencia de cache, JIT e escalonador.
 *
 * Uso: java app.ContagemOperacoes <arquivo> <ordenada:true|false>
 * Saida CSV: n;ordenada;comparacoes_montagem;comparacoes_busca_tel
 */
public class ContagemOperacoes {

    public static void main(String[] args) throws IOException {
        String arquivo = args[0];
        boolean ordenada = Boolean.parseBoolean(args[1]);

        ComparadorContador<Contato> cNome =
                new ComparadorContador<>(new ComparadorContatoPorNome());
        ComparadorContador<Contato> cTel =
                new ComparadorContador<>(new ComparadorContatoPorTelefone());

        IColecao<Contato> porNome = new ListaEncadeada<>(cNome, ordenada);
        IColecao<Contato> porTelefone = new ListaEncadeada<>(cTel, ordenada);

        String ultimoTelefone = null;
        try (BufferedReader br = new BufferedReader(new FileReader(arquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                if (linha.isBlank()) {
                    continue;
                }
                int sep = linha.indexOf(';');
                Contato c = new Contato(linha.substring(0, sep), linha.substring(sep + 1));
                porNome.adicionar(c);
                porTelefone.adicionar(c);
                ultimoTelefone = c.getTelefone();
            }
        }
        long montagem = cNome.getChamadas() + cTel.getChamadas();

        cTel.zerar();
        porTelefone.pesquisar(new Contato("", ultimoTelefone));
        long busca = cTel.getChamadas();

        System.out.printf(Locale.US, "%d;%b;%d;%d%n",
                porNome.quantidadeNos(), ordenada, montagem, busca);
    }
}
