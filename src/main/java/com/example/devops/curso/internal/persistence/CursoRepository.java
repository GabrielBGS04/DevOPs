package com.example.devops.curso.internal.persistence;

import com.example.devops.curso.domain.Curso;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CursoRepository extends JpaRepository<Curso, Long> {
}
