package com.example.devops.service;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Curso;
import com.example.devops.domain.Plano;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.repository.AlunoRepository;
import com.example.devops.repository.CursoRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class AlunoService {

    private final AlunoRepository alunoRepository;
    private final CursoRepository cursoRepository;

    public AlunoService(AlunoRepository alunoRepository, CursoRepository cursoRepository) {
        this.alunoRepository = alunoRepository;
        this.cursoRepository = cursoRepository;
    }

    public Aluno criar(String nome, Plano plano) {
        return alunoRepository.save(new Aluno(nome, plano));
    }

    public List<Aluno> listar() {
        return alunoRepository.findAll();
    }

    public Aluno buscarPorId(Long alunoId) {
        return alunoRepository.findById(alunoId)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Aluno não encontrado"));
    }

    @Transactional
    public Aluno processarConclusao(Long alunoId, ConclusaoCursoDTO dto) {
        if (dto == null || dto.getCursoId() == null) {
            throw new IllegalArgumentException("O id do curso é obrigatório");
        }

        Aluno aluno = buscarPorId(alunoId);
        Curso curso = cursoRepository.findById(dto.getCursoId())
                .orElseThrow(() -> new RecursoNaoEncontradoException("Curso não encontrado"));

        aluno.concluirCurso(curso, dto.getNota());
        return alunoRepository.save(aluno);
    }
}
