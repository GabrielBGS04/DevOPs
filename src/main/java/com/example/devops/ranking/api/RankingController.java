package com.example.devops.ranking.api;

import com.example.devops.ranking.application.RankingService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;

@RestController
public class RankingController {
    private final RankingService ranking;
    public RankingController(RankingService ranking) { this.ranking = ranking; }
    @GetMapping("/api/ranking")
    public List<RankingItem> listar() { return ranking.listar(); }
    public record RankingItem(Long alunoId, String nome, long cursosConcluidos, long pontos) {}
}
