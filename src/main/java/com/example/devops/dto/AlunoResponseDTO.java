package com.example.devops.dto;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Plano;

import java.util.Map;

public record AlunoResponseDTO(
        Long id,
        String nome,
        Plano plano,
        int cursosDisponiveis,
        int mediaGeral,
        Map<String, Double> historico
) {
    public static AlunoResponseDTO from(Aluno aluno) {
        return new AlunoResponseDTO(
                aluno.getId(),
                aluno.getNome(),
                aluno.getPlano(),
                aluno.getCursosDisponiveis(),
                aluno.getMediaGeral(),
                aluno.getHistorico()
        );
    }
}
