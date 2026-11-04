package com.example.devops.service;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Plano;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.repository.AlunoRepository;
import com.example.devops.curso.application.CursoService;
import com.example.devops.aluno.api.AlunoRanking;
import com.example.devops.gamificacao.application.ConclusaoDeCurso;
import com.example.devops.gamificacao.internal.persistence.JpaConclusaoAdapter;
import com.example.devops.integracao.NotificacaoOutbox;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class AlunoService {

    private final AlunoRepository alunoRepository;
    private final ConclusaoDeCurso conclusao;
    private final NotificacaoOutbox notificacoes;

    public AlunoService(AlunoRepository alunoRepository, CursoService cursos, NotificacaoOutbox notificacoes) {
        this.alunoRepository = alunoRepository;
        this.conclusao = new ConclusaoDeCurso(new JpaConclusaoAdapter(alunoRepository, cursos));
        this.notificacoes = notificacoes;
    }

    public Aluno criar(String nome, Plano plano) {
        return alunoRepository.save(new Aluno(nome, plano));
    }

    public List<Aluno> listar() {
        return alunoRepository.findAll();
    }

    public List<AlunoRanking> consultarRanking() { return alunoRepository.consultarRanking(); }

    public Aluno buscarPorId(Long alunoId) {
        return alunoRepository.findById(alunoId)
                .orElseThrow(() -> new RecursoNaoEncontradoException("Aluno não encontrado"));
    }

    @Transactional
    public Aluno processarConclusao(Long alunoId, ConclusaoCursoDTO dto) {
        Aluno aluno = conclusao.executar(alunoId, dto);
        notificacoes.gravar(alunoId, dto.getCursoId(), dto.getNota());
        return aluno;
    }
}
