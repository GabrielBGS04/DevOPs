package com.example.devops.domain;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.MapKeyColumn;

import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

@Entity
public class Aluno {

    public static final double NOTA_MINIMA_PARA_BONUS = 8.5;
    public static final int QUANTIDADE_CURSOS_BONUS = 3;

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    @Enumerated(EnumType.STRING)
    private Plano plano;

    private int cursosDisponiveis;

    @ElementCollection
    @CollectionTable(name = "historico_notas", joinColumns = @JoinColumn(name = "aluno_id"))
    @MapKeyColumn(name = "curso_nome")
    @Column(name = "nota", nullable = false)
    private Map<String, Double> historico = new HashMap<>();

    protected Aluno() {
    }

    public Aluno(String nome, Plano plano) {
        if (nome == null || nome.isBlank()) {
            throw new IllegalArgumentException("O nome do aluno é obrigatório");
        }
        if (plano == null) {
            throw new IllegalArgumentException("O plano do aluno é obrigatório");
        }
        this.nome = nome.trim();
        this.plano = plano;
    }

    public void concluirCurso(Curso curso, double nota) {
        if (curso == null) {
            throw new IllegalArgumentException("O curso é obrigatório");
        }
        if (nota < 0 || nota > 10) {
            throw new IllegalArgumentException("A nota deve estar entre 0 e 10");
        }

        historico.put(curso.getNome(), nota);
        if (temDireitoABonus(nota)) {
            cursosDisponiveis += QUANTIDADE_CURSOS_BONUS;
        }
    }

    public boolean temDireitoABonus(double nota) {
        return plano == Plano.BASICO && nota >= NOTA_MINIMA_PARA_BONUS;
    }

    public double getNotaDoCurso(Curso curso) {
        if (curso == null || !historico.containsKey(curso.getNome())) {
            throw new IllegalArgumentException("Curso não encontrado no histórico");
        }
        return historico.get(curso.getNome());
    }

    public int getMediaGeral() {
        return (int) historico.values().stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElse(0.0);
    }

    public Long getId() {
        return id;
    }

    public String getNome() {
        return nome;
    }

    public Plano getPlano() {
        return plano;
    }

    public int getCursosDisponiveis() {
        return cursosDisponiveis;
    }

    public Map<String, Double> getHistorico() {
        return Collections.unmodifiableMap(historico);
    }
}
