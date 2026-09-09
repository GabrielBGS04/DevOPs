package com.example.attd_projeto;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
public class Aluno {

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
        historico.put(curso, nota);
        // O código do if foi removido para simular a ausência da regra
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
