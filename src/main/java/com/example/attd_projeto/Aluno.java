package com.example.attd_projeto;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class Aluno {

    private static final double NOTA_MINIMA_PARA_BONUS = 8.5;
    private static final int QUANTIDADE_CURSOS_BONUS = 3;

    private final String nome;
    private final Plano plano;
    private final Map<Curso, Double> historico = new HashMap<>();
    private int cursosDisponiveis;

    public Aluno(String nome, Plano plano) {
        this.nome = nome;
        this.plano = plano;
    }

    public static void main(String[] args) {
        SpringApplication.run(Aluno.class, args);
    }

    public void concluirCurso(Curso curso, double nota) {
        registrarConclusao(curso, nota);
        liberarCursosSeElegivel(nota);
    }

    public void concluirCurso(int codigoCurso, double nota) {
        concluirCurso(new Curso(String.valueOf(codigoCurso)), nota);
    }

    public boolean temDireitoABonus(double nota) {
        // GREEN — código antes da refatoração Blue:
        // boolean notaElegivel = nota < NOTA_MINIMA_PARA_BONUS;
        // notaElegivel = nota >= NOTA_MINIMA_PARA_BONUS;
        // return plano == Plano.BASICO && notaElegivel;

        // BLUE — mesma regra em uma linha, sem a atribuição repetida.
        return plano == Plano.BASICO && nota >= NOTA_MINIMA_PARA_BONUS;
    }

    // BLUE — refatoração: separa o registro da conclusão da aplicação da recompensa.
    private void registrarConclusao(Curso curso, double nota) {
        historico.put(curso, nota);
    }

    // BLUE — refatoração: centraliza a alteração de cursos disponíveis.
    private void liberarCursosSeElegivel(double nota) {
        if (temDireitoABonus(nota)) {
            cursosDisponiveis += QUANTIDADE_CURSOS_BONUS;
        }
    }

    public double getNotaDoCurso(Curso curso) {
        Double nota = historico.get(curso);
        if (nota == null) {
            throw new IllegalArgumentException("Curso não encontrado no histórico");
        }
        return nota;
    }

    public int getMediaGeral() {
        return (int) historico.values().stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElse(0.0);
    }

    public int getCursosDisponiveis() {
        return cursosDisponiveis;
    }
}

enum Plano {
    BASICO
}

class Curso {
    private final String nome;

    Curso(String nome) {
        this.nome = nome;
    }
}
