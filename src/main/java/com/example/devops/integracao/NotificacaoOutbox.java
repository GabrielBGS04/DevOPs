package com.example.devops.integracao;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
public class NotificacaoOutbox {
    private final NotificacaoRepository repository;
    public NotificacaoOutbox(NotificacaoRepository repository) { this.repository = repository; }
    @Transactional(propagation = Propagation.MANDATORY)
    public void gravar(Long alunoId, Long cursoId, double nota) {
        repository.save(new NotificacaoEvento(alunoId, cursoId, nota));
    }
}
