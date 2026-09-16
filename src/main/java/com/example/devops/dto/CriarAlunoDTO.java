package com.example.devops.dto;

import com.example.devops.domain.Plano;

public class CriarAlunoDTO {
    private String nome;
    private Plano plano;

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public Plano getPlano() {
        return plano;
    }

    public void setPlano(Plano plano) {
        this.plano = plano;
    }
}
