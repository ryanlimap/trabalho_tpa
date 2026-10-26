package app;

import arvorebinaria.ArvoreAVL;
import arvorebinaria.ArvoreBinaria;
import colecao.IColecao;
import colecao.ListaEncadeada;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Scanner;

/**
 * Programa de teste das bibliotecas de coleções.
 *
 * Mantém DUAS estruturas com as MESMAS instâncias de Contato: uma indexada por
 * nome e outra indexada por telefone. Nenhum contato é duplicado (as duas
 * estruturas guardam referências para o mesmo objeto).
 *
 * A estrutura usada — lista não-ordenada, lista ordenada ou árvore binária — é
 * escolhida pelo usuário ao iniciar o programa. Como todas implementam
 * IColecao, o restante do programa não muda.
 */
public class Programa {

    private static IColecao<Contato> colecaoPorNome;
    private static IColecao<Contato> colecaoPorTelefone;
    /** Nome da estrutura escolhida, usado apenas nas mensagens na tela. */
    private static String nomeEstrutura = "estruturas";
    private static final Scanner ENTRADA = new Scanner(System.in);

    public static void main(String[] args) {
        int estrutura = perguntarEstrutura();
        switch (estrutura) {
            case 2 -> {
                colecaoPorNome = new ListaEncadeada<>(new ComparadorContatoPorNome(), true);
                colecaoPorTelefone = new ListaEncadeada<>(new ComparadorContatoPorTelefone(), true);
                nomeEstrutura = "listas ordenadas";
            }
            case 3 -> {
                colecaoPorNome = new ArvoreBinaria<>(new ComparadorContatoPorNome());
                colecaoPorTelefone = new ArvoreBinaria<>(new ComparadorContatoPorTelefone());
                nomeEstrutura = "arvores binarias de busca";
            }
            case 4 -> {
                colecaoPorNome = new ArvoreAVL<>(new ComparadorContatoPorNome());
                colecaoPorTelefone = new ArvoreAVL<>(new ComparadorContatoPorTelefone());
                nomeEstrutura = "arvores AVL";
            }
            default -> {
                colecaoPorNome = new ListaEncadeada<>(new ComparadorContatoPorNome(), false);
                colecaoPorTelefone = new ListaEncadeada<>(new ComparadorContatoPorTelefone(), false);
                nomeEstrutura = "listas nao-ordenadas";
            }
        }

        int opcao;
        do {
            exibirMenu();
            opcao = lerInteiro();
            switch (opcao) {
                case 1 -> carregarArquivo();
                case 2 -> adicionarContato();
                case 3 -> pesquisarPorNome();
                case 4 -> pesquisarPorTelefone();
                case 5 -> removerPorTelefone();
                case 6 -> alterarContato();
                case 7 -> sair();
                default -> System.out.println("Opcao invalida.");
            }
        } while (opcao != 7);
    }

    // ------------------------------------------------------------------
    // Menu
    // ------------------------------------------------------------------

    private static int perguntarEstrutura() {
        System.out.println("Qual estrutura deseja utilizar?");
        System.out.println("1 - Lista encadeada NAO-ordenada");
        System.out.println("2 - Lista encadeada ORDENADA");
        System.out.println("3 - Arvore binaria de busca");
        System.out.println("4 - Arvore AVL (binaria balanceada)");
        System.out.print("Opcao: ");
        int op = lerInteiro();
        return (op >= 1 && op <= 4) ? op : 1;
    }

    private static void exibirMenu() {
        System.out.println();
        System.out.println("===== AGENDA DE CONTATOS =====");
        System.out.println("1 - Carregar dados de arquivo (entrada.txt)");
        System.out.println("2 - Adicionar contato");
        System.out.println("3 - Pesquisar contato por nome");
        System.out.println("4 - Pesquisar contato por telefone");
        System.out.println("5 - Remover contato por telefone");
        System.out.println("6 - Alterar dados de contato");
        System.out.println("7 - Sair");
        System.out.print("Opcao: ");
    }

    private static int lerInteiro() {
        try {
            return Integer.parseInt(ENTRADA.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    // ------------------------------------------------------------------
    // Opcao 1 - carregar arquivo
    // ------------------------------------------------------------------

    /**
     * Formato do arquivo entrada.txt: uma linha por contato, com nome e
     * telefone separados por ponto-e-virgula. Ex.: Joao Silva;27999990000
     */
    private static void carregarArquivo() {
        System.out.print("Nome do arquivo (ENTER para 'entrada.txt'): ");
        String caminho = ENTRADA.nextLine().trim();
        if (caminho.isEmpty()) {
            caminho = "entrada.txt";
        }
        System.out.print("Verificar duplicidade de telefone durante a carga? "
                + "(s/n - a verificacao custa uma busca por linha): ");
        boolean verificar = ENTRADA.nextLine().trim().toLowerCase().startsWith("s");

        long inicio = System.nanoTime();
        int lidos = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(caminho))) {
            String linha;
            while ((linha = br.readLine()) != null) {
                if (linha.isBlank()) {
                    continue;
                }
                String[] partes = linha.split(";");
                if (partes.length < 2) {
                    continue;
                }
                Contato c = new Contato(partes[0].trim(), partes[1].trim());
                // regra de negocio: nao pode haver dois contatos com o mesmo telefone
                if (verificar && colecaoPorTelefone.pesquisar(c) != null) {
                    continue;
                }
                colecaoPorNome.adicionar(c);
                colecaoPorTelefone.adicionar(c);
                lidos++;
            }
        } catch (IOException e) {
            System.out.println("Erro ao ler o arquivo: " + e.getMessage());
            return;
        }
        long fim = System.nanoTime();
        System.out.println(lidos + " contatos carregados.");
        System.out.println("Tempo total de leitura e montagem das " + nomeEstrutura + ": "
                + formatar(fim - inicio));
    }

    // ------------------------------------------------------------------
    // Opcao 2 - adicionar
    // ------------------------------------------------------------------

    private static void adicionarContato() {
        System.out.print("Nome: ");
        String nome = ENTRADA.nextLine().trim();
        System.out.print("Telefone: ");
        String telefone = ENTRADA.nextLine().trim();
        Contato novo = new Contato(nome, telefone);

        if (colecaoPorTelefone.pesquisar(novo) != null) {
            System.out.println("Ja existe um contato com esse telefone. Insercao cancelada.");
            return;
        }
        long inicio = System.nanoTime();
        colecaoPorNome.adicionar(novo);
        colecaoPorTelefone.adicionar(novo);
        long fim = System.nanoTime();
        System.out.println("Contato adicionado. Tempo: " + formatar(fim - inicio));
    }

    // ------------------------------------------------------------------
    // Opcoes 3 e 4 - pesquisas
    // ------------------------------------------------------------------

    private static void pesquisarPorNome() {
        System.out.print("Nome a pesquisar: ");
        String nome = ENTRADA.nextLine().trim();
        Contato chave = new Contato(nome, "");
        long inicio = System.nanoTime();
        Contato achado = colecaoPorNome.pesquisar(chave);
        long fim = System.nanoTime();
        if (achado == null) {
            System.out.println("Contato nao encontrado.");
        } else {
            System.out.println("Telefone: " + achado.getTelefone());
        }
        System.out.println("Tempo da pesquisa: " + formatar(fim - inicio));
    }

    private static void pesquisarPorTelefone() {
        System.out.print("Telefone a pesquisar: ");
        String telefone = ENTRADA.nextLine().trim();
        Contato chave = new Contato("", telefone);
        long inicio = System.nanoTime();
        Contato achado = colecaoPorTelefone.pesquisar(chave);
        long fim = System.nanoTime();
        if (achado == null) {
            System.out.println("Contato nao encontrado.");
        } else {
            System.out.println("Nome: " + achado.getNome());
        }
        System.out.println("Tempo da pesquisa: " + formatar(fim - inicio));
    }

    // ------------------------------------------------------------------
    // Opcao 5 - remover por telefone
    // ------------------------------------------------------------------

    private static void removerPorTelefone() {
        System.out.print("Telefone do contato a remover: ");
        String telefone = ENTRADA.nextLine().trim();
        Contato chave = new Contato("", telefone);

        Contato alvo = colecaoPorTelefone.pesquisar(chave);
        long inicio = System.nanoTime();
        boolean removido = colecaoPorTelefone.remover(chave);
        long fim = System.nanoTime();
        if (removido && alvo != null) {
            removerInstanciaDaListaPorNome(alvo);
        }
        if (removido) {
            System.out.println("Contato excluido.");
        } else {
            System.out.println("Contato nao existia.");
        }
        System.out.println("Tempo da remocao: " + formatar(fim - inicio));
    }

    /**
     * A lista indexada por nome compara os contatos apenas pelo nome. Se
     * existirem homonimos, uma remocao "pela chave" poderia tirar da lista o
     * homonimo errado. Por isso os homonimos encontrados antes do alvo sao
     * retirados temporariamente e depois reinseridos.
     */
    private static void removerInstanciaDaListaPorNome(Contato alvo) {
        ListaEncadeada<Contato> temporarios =
                new ListaEncadeada<>(new ComparadorContatoPorNome(), false);
        while (true) {
            Contato achado = colecaoPorNome.pesquisar(alvo);
            if (achado == null) {
                break;
            }
            colecaoPorNome.remover(achado);
            if (achado == alvo) {
                break;
            }
            temporarios.adicionar(achado);
        }
        for (Contato c : temporarios) {
            colecaoPorNome.adicionar(c);
        }
    }

    // ------------------------------------------------------------------
    // Opcao 6 - alterar
    // ------------------------------------------------------------------

    private static void alterarContato() {
        System.out.print("Nome do contato: ");
        String nome = ENTRADA.nextLine().trim();
        Contato achado = colecaoPorNome.pesquisar(new Contato(nome, ""));
        if (achado == null) {
            System.out.println("Contato nao encontrado.");
            return;
        }
        System.out.println("Telefone atual: " + achado.getTelefone());
        System.out.print("Novo nome: ");
        String novoNome = ENTRADA.nextLine().trim();
        System.out.print("Novo telefone: ");
        String novoTelefone = ENTRADA.nextLine().trim();

        // Mesma regra de negocio da opcao "Adicionar": nao pode haver dois
        // contatos com o mesmo telefone. Se o novo telefone ja pertence a OUTRO
        // contato, a alteracao e cancelada.
        Contato donoDoTelefone = colecaoPorTelefone.pesquisar(new Contato("", novoTelefone));
        if (donoDoTelefone != null && donoDoTelefone != achado) {
            System.out.println("Ja existe outro contato com esse telefone ("
                    + donoDoTelefone.getNome() + "). Alteracao cancelada.");
            return;
        }

        // Como as chaves das listas mudam, o contato e removido e reinserido
        // para que a ordenacao continue valida.
        removerInstanciaDaListaPorNome(achado);
        colecaoPorTelefone.remover(achado);
        achado.setNome(novoNome);
        achado.setTelefone(novoTelefone);
        colecaoPorNome.adicionar(achado);
        colecaoPorTelefone.adicionar(achado);
        System.out.println("Contato alterado: " + achado);
    }

    // ------------------------------------------------------------------
    // Opcao 7 - sair
    // ------------------------------------------------------------------

    private static void sair() {
        System.out.println("Total de contatos na agenda: " + colecaoPorNome.quantidadeNos());
        System.out.println("Encerrando.");
    }

    private static String formatar(long nanos) {
        return nanos + " ns (" + (nanos / 1_000_000.0) + " ms)";
    }
}
