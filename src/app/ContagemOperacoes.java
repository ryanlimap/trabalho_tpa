package app;

import arvorebinaria.ArvoreAVL;
import arvorebinaria.ArvoreBinaria;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Locale;

/**
 * Conta o NÚMERO DE COMPARAÇÕES executadas na montagem das árvores e na busca
 * de pior caso, em vez de medir tempo. O tempo depende da máquina, do JIT e dos
 * caches; a contagem de operações, não — ela mede exatamente o que a análise
 * matemática prevê.
 *
 * Uso: java app.ContagemOperacoes <arquivo> <rotulo>
 * Saída CSV: rotulo;n;comp_montagem;comp_busca_tel;altura_tel
 */
public class ContagemOperacoes {

    public static void main(String[] args) throws IOException {
        String arquivo = args[0];
        String rotulo = args[1];

        ComparadorContador<Contato> cNome =
                new ComparadorContador<>(new ComparadorContatoPorNome());
        ComparadorContador<Contato> cTel =
                new ComparadorContador<>(new ComparadorContatoPorTelefone());

        boolean ehAvl = args.length > 2 && args[2].equalsIgnoreCase("avl");
        ArvoreBinaria<Contato> porNome =
                ehAvl ? new ArvoreAVL<>(cNome) : new ArvoreBinaria<>(cNome);
        ArvoreBinaria<Contato> porTelefone =
                ehAvl ? new ArvoreAVL<>(cTel) : new ArvoreBinaria<>(cTel);

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
            }
        }
        long montagem = cNome.getChamadas() + cTel.getChamadas();

        Contato folha = porTelefone.valorDaFolhaMaisProfunda();
        cTel.zerar();
        porTelefone.pesquisar(new Contato("", folha.getTelefone()));
        long busca = cTel.getChamadas();

        System.out.printf(Locale.US, "%s;%d;%d;%d;%d%n",
                rotulo, porTelefone.quantidadeNos(), montagem, busca, porTelefone.altura());
    }
}
