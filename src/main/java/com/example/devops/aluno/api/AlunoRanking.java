package com.example.devops.aluno.api;

/** Contrato público de leitura; não expõe histórico nem entidade JPA. */
public record AlunoRanking(Long alunoId, String nome, long cursosConcluidos) { }
