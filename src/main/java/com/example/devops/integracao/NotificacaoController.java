package com.example.devops.integracao;

import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
public class NotificacaoController {
    private final NotificacaoRepository repository;
    public NotificacaoController(NotificacaoRepository repository) { this.repository = repository; }
    @GetMapping("/api/notificacoes/pendentes")
    public Map<String, Long> pendentes() { return Map.of("quantidade", repository.countByEntregueFalse()); }
}
