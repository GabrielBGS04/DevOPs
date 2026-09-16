package com.example.devops.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;

@Entity
public class Curso {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String nome;

    protected Curso() {
    }

    public Curso(String nome) {
        if (nome == null || nome.isBlank()) {
            throw new IllegalArgumentException("O nome do curso é obrigatório");
        }
        this.nome = nome.trim();
    }

    public Long getId() {
        return id;
    }

    public String getNome() {
        return nome;
    }
}
