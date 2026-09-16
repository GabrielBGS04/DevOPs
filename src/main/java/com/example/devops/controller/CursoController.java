package com.example.devops.controller;

import com.example.devops.domain.Curso;
import com.example.devops.dto.CriarCursoDTO;
import com.example.devops.service.CursoService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/cursos")
public class CursoController {

    private final CursoService cursoService;

    public CursoController(CursoService cursoService) {
        this.cursoService = cursoService;
    }

    @PostMapping
    public ResponseEntity<Curso> criar(@RequestBody CriarCursoDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(cursoService.criar(dto.getNome()));
    }

    @GetMapping
    public List<Curso> listar() {
        return cursoService.listar();
    }
}
