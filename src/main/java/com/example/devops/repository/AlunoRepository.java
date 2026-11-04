package com.example.devops.repository;

import com.example.devops.domain.Aluno;
import com.example.devops.aluno.api.AlunoRanking;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface AlunoRepository extends JpaRepository<Aluno, Long> {

    @Query("select new com.example.devops.aluno.api.AlunoRanking(a.id, a.nome, count(h)) "
            + "from Aluno a left join a.historico h group by a.id, a.nome order by count(h) desc, a.id asc")
    List<AlunoRanking> consultarRanking();

    // As respostas da API incluem o histórico, mesmo depois de fechar a sessão JPA.
    @Override
    @EntityGraph(attributePaths = "historico")
    List<Aluno> findAll();

    @Override
    @EntityGraph(attributePaths = "historico")
    Optional<Aluno> findById(Long id);
}
