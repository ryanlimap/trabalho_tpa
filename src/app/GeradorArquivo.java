package app;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Random;

/**
 * Gera arquivos de entrada de contatos em três ordens diferentes, para
 * controlar a TOPOLOGIA da árvore binária resultante:
 *
 *   crescente   - identificadores em ordem crescente. Inseridos em uma árvore
 *                 binária de busca, cada novo elemento é maior que todos os
 *                 anteriores e desce sempre para a direita: a árvore fica
 *                 COMPLETAMENTE DEGENERADA (vira uma lista encadeada).
 *   balanceado  - os identificadores são emitidos pela divisão sucessiva do
 *                 intervalo ao meio (o meio primeiro, depois o meio de cada
 *                 metade, e assim por diante). A árvore resultante fica
 *                 PERFEITAMENTE BALANCEADA.
 *   aleatorio   - ordem embaralhada (árvore de altura aproximadamente log n).
 *
 * O nome do contato é derivado do mesmo identificador do telefone, com zeros à
 * esquerda, de modo que a ordem alfabética dos nomes seja idêntica à ordem
 * numérica dos telefones. Assim as DUAS árvores (a indexada por nome e a
 * indexada por telefone) têm a mesma topologia controlada.
 *
 * Uso: java app.GeradorArquivo <quantidade> <arquivo> <modo> [semente]
 */
public class GeradorArquivo {

    public static void main(String[] args) throws IOException {
        if (args.length < 3) {
            System.out.println("Uso: java app.GeradorArquivo <quantidade> <arquivo> "
                    + "<crescente|balanceado|aleatorio> [semente]");
            return;
        }
        int quantidade = Integer.parseInt(args[0]);
        String arquivo = args[1];
        String modo = args[2].toLowerCase();
        long semente = args.length > 3 ? Long.parseLong(args[3]) : 7L;

        int[] ids = switch (modo) {
            case "crescente" -> emOrdemCrescente(quantidade);
            case "balanceado" -> emOrdemBalanceada(quantidade);
            case "aleatorio" -> embaralhado(quantidade, semente);
            default -> throw new IllegalArgumentException("Modo inválido: " + modo);
        };

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(arquivo))) {
            for (int id : ids) {
                bw.write(nomeDe(id) + ";" + telefoneDe(id));
                bw.newLine();
            }
        }
        System.out.println("Arquivo " + arquivo + " gerado com " + quantidade
                + " contatos em ordem " + modo + ".");
    }

    private static String nomeDe(int id) {
        return String.format("Contato %07d", id);
    }

    private static String telefoneDe(int id) {
        return "27" + (900000000 + id);
    }

    /** Ordem crescente: 0, 1, 2, ... -> árvore degenerada. */
    private static int[] emOrdemCrescente(int n) {
        int[] ids = new int[n];
        for (int i = 0; i < n; i++) {
            ids[i] = i;
        }
        return ids;
    }

    /**
     * Ordem "do meio para fora": emite o elemento central do intervalo e depois
     * repete o processo para a metade esquerda e para a metade direita, nível a
     * nível. Inserindo nessa ordem, a árvore fica perfeitamente balanceada.
     */
    private static int[] emOrdemBalanceada(int n) {
        int[] ids = new int[n];
        int k = 0;
        Deque<int[]> fila = new ArrayDeque<>();
        fila.add(new int[]{0, n - 1});
        while (!fila.isEmpty()) {
            int[] faixa = fila.poll();
            int ini = faixa[0];
            int fim = faixa[1];
            if (ini > fim) {
                continue;
            }
            int meio = ini + (fim - ini) / 2;
            ids[k++] = meio;
            fila.add(new int[]{ini, meio - 1});
            fila.add(new int[]{meio + 1, fim});
        }
        return ids;
    }

    /** Embaralhamento de Fisher-Yates: ordem aleatória sem repetição. */
    private static int[] embaralhado(int n, long semente) {
        int[] ids = emOrdemCrescente(n);
        Random rnd = new Random(semente);
        for (int i = n - 1; i > 0; i--) {
            int j = rnd.nextInt(i + 1);
            int tmp = ids[i];
            ids[i] = ids[j];
            ids[j] = tmp;
        }
        return ids;
    }
}
