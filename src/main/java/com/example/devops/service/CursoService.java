package com.example.devops.service;

import com.example.devops.domain.Curso;
import com.example.devops.repository.CursoRepository;
import org.springframework.stereotype.Service;

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
}
