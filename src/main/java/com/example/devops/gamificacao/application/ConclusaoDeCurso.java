package com.example.devops.gamificacao.application;

import com.example.devops.domain.Aluno;
import com.example.devops.curso.domain.Curso;
import com.example.devops.dto.ConclusaoCursoDTO;

/** Caso de uso testável com qualquer adapter que implemente a porta. */
public class ConclusaoDeCurso {
    private final ConclusaoPort dados;
    public ConclusaoDeCurso(ConclusaoPort dados) { this.dados = dados; }
    public Aluno executar(Long alunoId, ConclusaoCursoDTO dto) {
        if (dto == null || dto.getCursoId() == null)
            throw new IllegalArgumentException("O id do curso é obrigatório");
        Aluno aluno = dados.buscarAluno(alunoId);
        Curso curso = dados.buscarCurso(dto.getCursoId());
        aluno.concluirCurso(curso, dto.getNota());
        return dados.salvar(aluno);
    }
}
