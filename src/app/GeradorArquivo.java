package app;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

/**
 * Gera arquivos de entrada com contatos aleatorios (nome;telefone).
 * Os telefones gerados sao unicos (embaralhamento de uma faixa de numeros).
 *
 * Uso: java app.GeradorArquivo <quantidade> <arquivoSaida> [semente]
 */
public class GeradorArquivo {

    private static final String[] PRIMEIROS = {
        "Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Fabio", "Gabriela", "Heitor",
        "Isabela", "Joao", "Karina", "Lucas", "Mariana", "Nelson", "Olivia", "Pedro",
        "Quesia", "Rafael", "Sabrina", "Thiago", "Ursula", "Vinicius", "Wesley",
        "Xenia", "Yuri", "Zelia", "Amanda", "Breno", "Cecilia", "Diego"
    };

    private static final String[] SOBRENOMES = {
        "Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues",
        "Almeida", "Nascimento", "Lima", "Araujo", "Fernandes", "Carvalho", "Gomes",
        "Martins", "Rocha", "Ribeiro", "Alves", "Monteiro", "Cardoso", "Teixeira",
        "Barbosa", "Correia", "Dias", "Moreira", "Cavalcanti", "Pinto", "Mendes"
    };

    public static void main(String[] args) throws IOException {
        if (args.length < 2) {
            System.out.println("Uso: java app.GeradorArquivo <quantidade> <arquivo> [semente]");
            return;
        }
        int quantidade = Integer.parseInt(args[0]);
        String arquivo = args[1];
        long semente = args.length > 2 ? Long.parseLong(args[2]) : 42L;

        Random rnd = new Random(semente);

        // telefones unicos: gera a faixa e embaralha
        int[] telefones = new int[quantidade];
        for (int i = 0; i < quantidade; i++) {
            telefones[i] = 900000000 + i;
        }
        for (int i = quantidade - 1; i > 0; i--) {
            int j = rnd.nextInt(i + 1);
            int tmp = telefones[i];
            telefones[i] = telefones[j];
            telefones[j] = tmp;
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(arquivo))) {
            for (int i = 0; i < quantidade; i++) {
                String nome = PRIMEIROS[rnd.nextInt(PRIMEIROS.length)] + " "
                        + SOBRENOMES[rnd.nextInt(SOBRENOMES.length)] + " "
                        + rnd.nextInt(1000000);
                bw.write(nome + ";" + "27" + telefones[i]);
                bw.newLine();
            }
        }
        System.out.println("Arquivo " + arquivo + " gerado com " + quantidade + " contatos.");
    }
}
