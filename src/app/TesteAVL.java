package app;

import arvorebinaria.ArvoreAVL;
import arvorebinaria.ArvoreBinaria;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Random;

/**
 * Testes da árvore AVL: além de conferir o conteúdo, verifica após cada
 * operação se a propriedade AVL continua valendo em todos os nós.
 *
 * Uso: java app.TesteAVL
 */
public class TesteAVL {

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

        // ---------- as quatro rotações ----------
        ArvoreAVL<Integer> ee = new ArvoreAVL<>(cmp);
        for (int v : new int[]{30, 20, 10}) {
            ee.adicionar(v);        // caso esquerda-esquerda -> rotação simples à direita
        }
        verificar("rotacao esquerda-esquerda: em ordem", ee.caminharEmOrdem(), "[10,20,30]");
        verificar("rotacao esquerda-esquerda: altura", ee.altura(), 1);

        ArvoreAVL<Integer> dd = new ArvoreAVL<>(cmp);
        for (int v : new int[]{10, 20, 30}) {
            dd.adicionar(v);        // caso direita-direita -> rotação simples à esquerda
        }
        verificar("rotacao direita-direita: em ordem", dd.caminharEmOrdem(), "[10,20,30]");
        verificar("rotacao direita-direita: altura", dd.altura(), 1);

        ArvoreAVL<Integer> ed = new ArvoreAVL<>(cmp);
        for (int v : new int[]{30, 10, 20}) {
            ed.adicionar(v);        // caso esquerda-direita -> rotação dupla
        }
        verificar("rotacao esquerda-direita: em ordem", ed.caminharEmOrdem(), "[10,20,30]");
        verificar("rotacao esquerda-direita: altura", ed.altura(), 1);

        ArvoreAVL<Integer> de = new ArvoreAVL<>(cmp);
        for (int v : new int[]{10, 30, 20}) {
            de.adicionar(v);        // caso direita-esquerda -> rotação dupla
        }
        verificar("rotacao direita-esquerda: em ordem", de.caminharEmOrdem(), "[10,20,30]");
        verificar("rotacao direita-esquerda: altura", de.altura(), 1);

        // ---------- insercao em ordem crescente: o caso que degenera a ABB ----------
        ArvoreAVL<Integer> avl = new ArvoreAVL<>(cmp);
        ArvoreBinaria<Integer> abb = new ArvoreBinaria<>(cmp);
        for (int i = 0; i < 1000; i++) {
            avl.adicionar(i);
            abb.adicionar(i);
        }
        verificar("1.000 chaves crescentes na ABB: altura = n-1", abb.altura(), 999);
        verificar("1.000 chaves crescentes na AVL: altura = 9", avl.altura(), 9);
        verificar("1.000 chaves crescentes na AVL: propriedade AVL", avl.ehAvlValida(), true);
        verificar("1.000 chaves crescentes na AVL: quantidade", avl.quantidadeNos(), 1000);

        // altura minima teorica e limite da AVL
        int alturaMinima = (int) Math.floor(Math.log(1000) / Math.log(2));
        verificar("altura da AVL igual ao minimo teorico piso(log2 n)",
                avl.altura(), alturaMinima);

        // ---------- remocoes com rebalanceamento ----------
        for (int i = 0; i < 500; i++) {
            avl.remover(i);
            if (!avl.ehAvlValida()) {
                falhas++;
                System.out.println("propriedade AVL quebrou ao remover " + i);
                break;
            }
        }
        verificar("apos 500 remocoes: quantidade", avl.quantidadeNos(), 500);
        verificar("apos 500 remocoes: propriedade AVL", avl.ehAvlValida(), true);
        verificar("apos 500 remocoes: primeiro elemento", avl.pesquisar(500), 500);
        verificar("apos 500 remocoes: elemento removido", avl.pesquisar(499), null);

        // ---------- teste cruzado com 20.000 operacoes aleatorias ----------
        ArvoreAVL<Integer> a = new ArvoreAVL<>(cmp);
        List<Integer> referencia = new ArrayList<>();
        Random rnd = new Random(42);
        boolean propriedadeOk = true;
        for (int i = 0; i < 20_000; i++) {
            int v = rnd.nextInt(5_000);
            if (rnd.nextInt(100) < 70) {
                a.adicionar(v);
                referencia.add(v);
            } else {
                boolean removeu = a.remover(v);
                boolean removeuRef = referencia.remove((Integer) v);
                if (removeu != removeuRef) {
                    falhas++;
                    System.out.println("divergencia na remocao do valor " + v);
                    break;
                }
            }
            if (i % 500 == 0 && !a.ehAvlValida()) {
                propriedadeOk = false;
                break;
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
        verificar("20.000 operacoes aleatorias: conteudo em ordem",
                a.caminharEmOrdem(), esperado.toString());
        verificar("20.000 operacoes aleatorias: quantidade",
                a.quantidadeNos(), referencia.size());
        verificar("20.000 operacoes aleatorias: propriedade AVL sempre valida",
                propriedadeOk && a.ehAvlValida(), true);

        // a altura precisa respeitar o limite teorico da AVL: h < 1,4404*log2(n+2)
        int n = a.quantidadeNos();
        double limite = 1.4404 * (Math.log(n + 2) / Math.log(2)) - 0.3277;
        verificar("altura dentro do limite teorico da AVL",
                a.altura() <= limite, true);

        System.out.println();
        System.out.println(falhas == 0 ? "TODOS OS TESTES PASSARAM"
                : falhas + " TESTE(S) FALHARAM");
    }
}
