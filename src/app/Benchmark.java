package app;

import colecao.IColecao;
import colecao.ListaEncadeada;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Locale;

/**
 * Executa uma rodada da analise empirica:
 *   1) le o arquivo e monta as duas listas (por nome e por telefone);
 *   2) pesquisa pelo telefone do ULTIMO contato do arquivo;
 *   3) pesquisa pelo nome do ULTIMO contato do arquivo;
 *   4) remove o ULTIMO contato do arquivo, pelo telefone.
 *
 * Uso: java app.Benchmark <arquivo> <ordenada:true|false>
 * Saida: uma linha CSV com os tempos em milissegundos.
 */
public class Benchmark {

    public static void main(String[] args) throws IOException {
        String arquivo = args[0];
        boolean ordenada = Boolean.parseBoolean(args[1]);

        IColecao<Contato> porNome = new ListaEncadeada<>(new ComparadorContatoPorNome(), ordenada);
        IColecao<Contato> porTelefone = new ListaEncadeada<>(new ComparadorContatoPorTelefone(), ordenada);

        String ultimoNome = null;
        String ultimoTelefone = null;

        // ---------- 1) leitura do arquivo + montagem das listas ----------
        long t0 = System.nanoTime();
        try (BufferedReader br = new BufferedReader(new FileReader(arquivo))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                if (linha.isBlank()) {
                    continue;
                }
                int sep = linha.indexOf(';');
                String nome = linha.substring(0, sep);
                String telefone = linha.substring(sep + 1);
                Contato c = new Contato(nome, telefone);
                porNome.adicionar(c);
                porTelefone.adicionar(c);
                ultimoNome = nome;
                ultimoTelefone = telefone;
            }
        }
        long t1 = System.nanoTime();
        double tMontagem = (t1 - t0) / 1_000_000.0;

        int n = porNome.quantidadeNos();

        // ---------- 2) pesquisa pelo telefone do ultimo contato ----------
        Contato chaveTel = new Contato("", ultimoTelefone);
        long t2 = System.nanoTime();
        Contato achadoTel = porTelefone.pesquisar(chaveTel);
        long t3 = System.nanoTime();
        double tBuscaTel = (t3 - t2) / 1_000_000.0;

        // ---------- 3) pesquisa pelo nome do ultimo contato ----------
        Contato chaveNome = new Contato(ultimoNome, "");
        long t4 = System.nanoTime();
        Contato achadoNome = porNome.pesquisar(chaveNome);
        long t5 = System.nanoTime();
        double tBuscaNome = (t5 - t4) / 1_000_000.0;

        // ---------- 4) remocao do ultimo contato pelo telefone ----------
        long t6 = System.nanoTime();
        boolean removido = porTelefone.remover(chaveTel);
        long t7 = System.nanoTime();
        double tRemocao = (t7 - t6) / 1_000_000.0;

        // CSV: n;ordenada;montagem;buscaTelefone;buscaNome;remocao;achouTel;achouNome;removeu
        // Locale.US garante ponto como separador decimal, independente do idioma
        // do sistema operacional (no Windows em pt-BR o padrao sairia com virgula
        // e quebraria a leitura do CSV pelos scripts de analise).
        System.out.printf(Locale.US, "%d;%b;%.4f;%.4f;%.4f;%.4f;%b;%b;%b%n",
                n, ordenada, tMontagem, tBuscaTel, tBuscaNome, tRemocao,
                achadoTel != null, achadoNome != null, removido);
    }
}
