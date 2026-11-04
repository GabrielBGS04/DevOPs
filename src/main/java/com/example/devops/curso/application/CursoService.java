package com.example.devops.curso.application;

import com.example.devops.curso.domain.Curso;
import com.example.devops.curso.internal.persistence.CursoRepository;
import org.springframework.stereotype.Service;
import com.example.devops.service.RecursoNaoEncontradoException;

import java.util.List;

@Service
public class CursoService {

    private final CursoRepository cursoRepository;

    public CursoService(CursoRepository cursoRepository) {
        this.cursoRepository = cursoRepository;
    }

    public Curso criar(String nome) {
        return cursoRepository.save(new Curso(nome));
    }

    public List<Curso> listar() {
        return cursoRepository.findAll();
    }
    public Curso buscarPorId(Long id) {
        return cursoRepository.findById(id)
            .orElseThrow(() -> new RecursoNaoEncontradoException("Curso não encontrado"));
    }
}
