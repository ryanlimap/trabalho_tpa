package app;

import arvorebinaria.ArvoreAVL;
import arvorebinaria.ArvoreBinaria;
import colecao.IColecao;
import colecao.ListaEncadeada;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Locale;

/**
 * Executa uma rodada da análise empírica do Trabalho 2:
 *   1) lê o arquivo e monta as duas estruturas (por nome e por telefone);
 *   2) identifica o PIOR CASO de busca: a folha mais distante da raiz na
 *      estrutura indexada por telefone;
 *   3) pesquisa esse contato pelo telefone;
 *   4) pesquisa o mesmo contato pelo nome;
 *   5) remove esse contato pelo telefone.
 *
 * Uso: java app.Benchmark <arquivo> <arvore|lista_nao_ordenada|lista_ordenada>
 * Saída CSV: estrutura;n;montagem_ms;altura_tel;altura_nome;busca_tel_ms;
 *            busca_nome_ms;remocao_ms;achouTel;achouNome;removeu
 */
public class Benchmark {

    public static void main(String[] args) throws IOException {
        String arquivo = args[0];
        String estrutura = args[1];

        IColecao<Contato> porNome;
        IColecao<Contato> porTelefone;
        boolean ehAvl = estrutura.startsWith("avl");
        boolean ehArvore = ehAvl || estrutura.startsWith("arvore");

        if (ehAvl) {
            porNome = new ArvoreAVL<>(new ComparadorContatoPorNome());
            porTelefone = new ArvoreAVL<>(new ComparadorContatoPorTelefone());
        } else if (ehArvore) {
            porNome = new ArvoreBinaria<>(new ComparadorContatoPorNome());
            porTelefone = new ArvoreBinaria<>(new ComparadorContatoPorTelefone());
        } else {
            boolean ordenada = estrutura.equals("lista_ordenada");
            porNome = new ListaEncadeada<>(new ComparadorContatoPorNome(), ordenada);
            porTelefone = new ListaEncadeada<>(new ComparadorContatoPorTelefone(), ordenada);
        }

        // ---------- 1) leitura do arquivo + montagem ----------
        long t0 = System.nanoTime();
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
        long t1 = System.nanoTime();
        double tMontagem = (t1 - t0) / 1_000_000.0;

        int n = porTelefone.quantidadeNos();
        int alturaTel = -1;
        int alturaNome = -1;
        Contato alvo;

        // ---------- 2) o pior caso de busca ----------
        if (ehArvore) {
            ArvoreBinaria<Contato> arvoreTel = (ArvoreBinaria<Contato>) porTelefone;
            alturaTel = arvoreTel.altura();
            alturaNome = ((ArvoreBinaria<Contato>) porNome).altura();
            alvo = arvoreTel.valorDaFolhaMaisProfunda();
        } else {
            // Nas listas, o pior caso é o último nó. Para que a comparação use o
            // MESMO contato, lemos a última linha do arquivo quando a lista é
            // não-ordenada; na ordenada, o pior caso é o maior telefone.
            alvo = ultimoContatoDoArquivo(arquivo);
        }

        Contato chaveTel = new Contato("", alvo.getTelefone());
        Contato chaveNome = new Contato(alvo.getNome(), "");

        // As três operações são repetidas REPETICOES vezes e reportamos a
        // mediana. Isso elimina o ruído de medidas isoladas de poucos
        // milissegundos, sem precisar remontar a estrutura (o que, nos casos
        // degenerados, levaria minutos a cada repetição). Depois de medir a
        // remoção, o contato é reinserido, de modo que todas as repetições
        // partem exatamente do mesmo estado.
        final int REPETICOES = 5;
        double[] tBuscaTel = new double[REPETICOES];
        double[] tBuscaNome = new double[REPETICOES];
        double[] tRemocao = new double[REPETICOES];
        Contato achadoTel = null;
        Contato achadoNome = null;
        boolean removeu = false;

        for (int i = 0; i < REPETICOES; i++) {
            long t2 = System.nanoTime();
            achadoTel = porTelefone.pesquisar(chaveTel);
            long t3 = System.nanoTime();
            tBuscaTel[i] = (t3 - t2) / 1_000_000.0;

            long t4 = System.nanoTime();
            achadoNome = porNome.pesquisar(chaveNome);
            long t5 = System.nanoTime();
            tBuscaNome[i] = (t5 - t4) / 1_000_000.0;

            long t6 = System.nanoTime();
            removeu = porTelefone.remover(chaveTel);
            long t7 = System.nanoTime();
            tRemocao[i] = (t7 - t6) / 1_000_000.0;

            porTelefone.adicionar(alvo);   // devolve a estrutura ao estado anterior
        }
        porTelefone.remover(chaveTel);     // deixa o contato removido ao final

        System.out.printf(Locale.US, "%s;%d;%.4f;%d;%d;%.4f;%.4f;%.4f;%b;%b;%b%n",
                estrutura, n, tMontagem, alturaTel, alturaNome,
                mediana(tBuscaTel), mediana(tBuscaNome), mediana(tRemocao),
                achadoTel != null, achadoNome != null, removeu);
    }

    private static double mediana(double[] v) {
        double[] c = v.clone();
        java.util.Arrays.sort(c);
        int m = c.length / 2;
        return (c.length % 2 == 1) ? c[m] : (c[m - 1] + c[m]) / 2.0;
    }

    private static Contato ultimoContatoDoArquivo(String arquivo) throws IOException {
        String ultima = null;
        try (BufferedReader br = new BufferedReader(new FileReader(arquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                if (!linha.isBlank()) {
                    ultima = linha;
                }
            }
        }
        int sep = ultima.indexOf(';');
        return new Contato(ultima.substring(0, sep), ultima.substring(sep + 1));
    }
}
