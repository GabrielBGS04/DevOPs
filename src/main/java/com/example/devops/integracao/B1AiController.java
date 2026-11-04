package com.example.devops.integracao;

import com.example.devops.curso.application.CursoService;
import com.example.devops.service.AlunoService;
import org.springframework.web.bind.annotation.*;
import java.util.ArrayList;

@RestController
public class B1AiController {
    public record Pergunta(String pergunta) { }
    private final AlunoService alunos;
    private final CursoService cursos;
    private final B1HttpClient client;
    public B1AiController(AlunoService alunos, CursoService cursos, B1HttpClient client) {
        this.alunos = alunos;
        this.cursos = cursos;
        this.client = client;
    }
    @GetMapping("/api/alunos/{id}/recomendacoes")
    public B1HttpClient.Recomendacoes recomendar(@PathVariable Long id) {
        var aluno = alunos.buscarPorId(id);
        var catalogo = cursos.listar().stream().map(c -> new B1HttpClient.CursoItem(c.getId(), c.getNome())).toList();
        return client.recomendar(id, new ArrayList<>(aluno.getHistorico().keySet()), catalogo);
    }
    @PostMapping("/api/assistente")
    public B1HttpClient.Resposta perguntar(@RequestBody Pergunta request) {
        if (request.pergunta() == null || request.pergunta().isBlank()) throw new IllegalArgumentException("A pergunta é obrigatória");
        return client.perguntar(request.pergunta());
    }
}
