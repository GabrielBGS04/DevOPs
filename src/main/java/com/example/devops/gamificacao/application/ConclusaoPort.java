package com.example.devops.gamificacao.application;

import com.example.devops.domain.Aluno;
import com.example.devops.curso.domain.Curso;

public interface ConclusaoPort {
    Aluno buscarAluno(Long id);
    Curso buscarCurso(Long id);
    Aluno salvar(Aluno aluno);
}
