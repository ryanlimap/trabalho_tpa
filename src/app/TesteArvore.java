package app;

import arvorebinaria.ArvoreBinaria;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

/**
 * Testes da biblioteca de árvore binária. Executa verificações automáticas e
 * imprime OK/FALHOU para cada uma.
 *
 * Uso: java app.TesteArvore
 */
public class TesteArvore {

    private static int falhas = 0;

    private static void verificar(String titulo, Object obtido, Object esperado) {
        boolean ok = (obtido == null) ? esperado == null : obtido.equals(esperado);
        System.out.printf("%-58s %s%n", titulo, ok ? "OK" : "FALHOU");
        if (!ok) {
            falhas++;
            System.out.println("    esperado: " + esperado);
            System.out.println("    obtido  : " + obtido);
        }
    }

    public static void main(String[] args) {
        Comparator<Integer> cmp = Comparator.naturalOrder();

        // ---------- árvore vazia ----------
        ArvoreBinaria<Integer> vazia = new ArvoreBinaria<>(cmp);
        verificar("arvore vazia: altura", vazia.altura(), -1);
        verificar("arvore vazia: quantidadeNos", vazia.quantidadeNos(), 0);
        verificar("arvore vazia: caminharEmOrdem", vazia.caminharEmOrdem(), "[]");
        verificar("arvore vazia: pesquisar", vazia.pesquisar(1), null);
        verificar("arvore vazia: remover", vazia.remover(1), false);

        // ---------- árvore balanceada de 7 nós ----------
        ArvoreBinaria<Integer> a = new ArvoreBinaria<>(cmp);
        for (int v : new int[]{40, 20, 60, 10, 30, 50, 70}) {
            a.adicionar(v);
        }
        verificar("balanceada 7 nos: altura", a.altura(), 2);
        verificar("balanceada 7 nos: quantidadeNos", a.quantidadeNos(), 7);
        verificar("balanceada 7 nos: em ordem",
                a.caminharEmOrdem(), "[10,20,30,40,50,60,70]");
        verificar("balanceada 7 nos: em nivel (1a linha)",
                a.caminharEmNivel().split("\n")[0], "[40");
        verificar("balanceada 7 nos: toString == em ordem",
                a.toString(), a.caminharEmOrdem());
        verificar("balanceada 7 nos: pesquisar existente", a.pesquisar(50), 50);
        verificar("balanceada 7 nos: pesquisar inexistente", a.pesquisar(55), null);
        verificar("balanceada 7 nos: folha mais profunda existe",
                a.pesquisar(a.valorDaFolhaMaisProfunda()) != null, true);

        // ---------- remoção: folha ----------
        verificar("remover folha (10): retorno", a.remover(10), true);
        verificar("remover folha (10): em ordem",
                a.caminharEmOrdem(), "[20,30,40,50,60,70]");
        verificar("remover folha (10): quantidade", a.quantidadeNos(), 6);

        // ---------- remoção: nó com um filho ----------
        verificar("remover no com 1 filho (20): retorno", a.remover(20), true);
        verificar("remover no com 1 filho (20): em ordem",
                a.caminharEmOrdem(), "[30,40,50,60,70]");

        // ---------- remoção: nó com dois filhos (a raiz) ----------
        verificar("remover raiz com 2 filhos (40): retorno", a.remover(40), true);
        verificar("remover raiz com 2 filhos (40): em ordem",
                a.caminharEmOrdem(), "[30,50,60,70]");
        verificar("remover inexistente", a.remover(999), false);

        // ---------- remover todos ----------
        for (int v : new int[]{30, 50, 60, 70}) {
            a.remover(v);
        }
        verificar("apos remover todos: quantidade", a.quantidadeNos(), 0);
        verificar("apos remover todos: altura", a.altura(), -1);
        a.adicionar(99);
        verificar("arvore volta a aceitar insercao", a.caminharEmOrdem(), "[99]");

        // ---------- topologias ----------
        ArvoreBinaria<Integer> degenerada = new ArvoreBinaria<>(cmp);
        for (int i = 0; i < 15; i++) {
            degenerada.adicionar(i);
        }
        verificar("degenerada com 15 nos: altura = n-1", degenerada.altura(), 14);

        ArvoreBinaria<Integer> balanceada = new ArvoreBinaria<>(cmp);
        for (int v : new int[]{8, 4, 12, 2, 6, 10, 14, 1, 3, 5, 7, 9, 11, 13, 15}) {
            balanceada.adicionar(v);
        }
        verificar("balanceada com 15 nos: altura = 3", balanceada.altura(), 3);

        // ---------- profundidade e pilha: arvore degenerada grande ----------
        ArvoreBinaria<Integer> grande = new ArvoreBinaria<>(cmp);
        for (int i = 0; i < 100_000; i++) {
            grande.adicionar(i);
        }
        verificar("degenerada com 100.000 nos: altura", grande.altura(), 99_999);
        verificar("degenerada com 100.000 nos: caminhamento nao estoura a pilha",
                grande.caminharEmOrdem().length() > 0, true);

        // ---------- teste cruzado com 10.000 operacoes aleatorias ----------
        ArvoreBinaria<Integer> arv = new ArvoreBinaria<>(cmp);
        List<Integer> referencia = new ArrayList<>();
        Random rnd = new Random(42);
        for (int i = 0; i < 10_000; i++) {
            int v = rnd.nextInt(5_000);
            if (rnd.nextInt(100) < 70) {
                arv.adicionar(v);
                referencia.add(v);
            } else {
                boolean removeu = arv.remover(v);
                boolean removeuRef = referencia.remove((Integer) v);
                if (removeu != removeuRef) {
                    falhas++;
                    System.out.println("divergencia na remocao do valor " + v);
                }
            }
        }
        Collections.sort(referencia);
        StringBuilder esperado = new StringBuilder("[");
        for (int i = 0; i < referencia.size(); i++) {
            if (i > 0) {
                esperado.append(",");
            }
            esperado.append(referencia.get(i));
        }
        esperado.append("]");
        verificar("10.000 operacoes aleatorias: conteudo em ordem",
                arv.caminharEmOrdem(), esperado.toString());
        verificar("10.000 operacoes aleatorias: quantidade",
                arv.quantidadeNos(), referencia.size());

        System.out.println();
        System.out.println(falhas == 0 ? "TODOS OS TESTES PASSARAM"
                : falhas + " TESTE(S) FALHARAM");
    }
}
