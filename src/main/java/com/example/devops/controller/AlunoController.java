package com.example.devops.controller;

import com.example.devops.domain.Aluno;
import com.example.devops.dto.AlunoResponseDTO;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.dto.CriarAlunoDTO;
import com.example.devops.service.AlunoService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/alunos")
public class AlunoController {

    private final AlunoService alunoService;

    public AlunoController(AlunoService alunoService) {
        this.alunoService = alunoService;
    }

    @PostMapping
    public ResponseEntity<AlunoResponseDTO> criar(@RequestBody CriarAlunoDTO dto) {
        Aluno aluno = alunoService.criar(dto.getNome(), dto.getPlano());
        return ResponseEntity.status(HttpStatus.CREATED).body(AlunoResponseDTO.from(aluno));
    }

    @GetMapping
    public List<AlunoResponseDTO> listar() {
        return alunoService.listar().stream().map(AlunoResponseDTO::from).toList();
    }

    @GetMapping("/{alunoId}")
    public AlunoResponseDTO buscarPorId(@PathVariable Long alunoId) {
        return AlunoResponseDTO.from(alunoService.buscarPorId(alunoId));
    }

    @PostMapping("/{alunoId}/concluir-curso")
    public AlunoResponseDTO concluirCurso(
            @PathVariable Long alunoId,
            @RequestBody ConclusaoCursoDTO dto) {
        return AlunoResponseDTO.from(alunoService.processarConclusao(alunoId, dto));
    }
}
