package com.example.devops.gamificacao.internal.persistence;

import com.example.devops.domain.Aluno;
import com.example.devops.curso.domain.Curso;
import com.example.devops.repository.AlunoRepository;
import com.example.devops.curso.application.CursoService;
import com.example.devops.gamificacao.application.ConclusaoPort;
import com.example.devops.service.RecursoNaoEncontradoException;

public class JpaConclusaoAdapter implements ConclusaoPort {
    private final AlunoRepository alunos;
    private final CursoService cursos;
    public JpaConclusaoAdapter(AlunoRepository alunos, CursoService cursos) {
        this.alunos = alunos; this.cursos = cursos;
    }
    public Aluno buscarAluno(Long id) {
        return alunos.findById(id).orElseThrow(() -> new RecursoNaoEncontradoException("Aluno não encontrado"));
    }
    public Curso buscarCurso(Long id) {
        return cursos.buscarPorId(id);
    }
    public Aluno salvar(Aluno aluno) { return alunos.save(aluno); }
}
