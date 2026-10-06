package com.example.devops.repository;

import com.example.devops.domain.Aluno;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AlunoRepository extends JpaRepository<Aluno, Long> {

    // As respostas da API incluem o histórico, mesmo depois de fechar a sessão JPA.
    @Override
    @EntityGraph(attributePaths = "historico")
    List<Aluno> findAll();

    @Override
    @EntityGraph(attributePaths = "historico")
    Optional<Aluno> findById(Long id);
}
