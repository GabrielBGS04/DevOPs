package com.example.devops.ranking.application;

import com.example.devops.service.AlunoService;
import com.example.devops.ranking.api.RankingController.RankingItem;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class RankingService {
    private final AlunoService alunos;
    public RankingService(AlunoService alunos) { this.alunos = alunos; }
    public List<RankingItem> listar() {
        return alunos.consultarRanking().stream()
            .map(a -> new RankingItem(a.alunoId(), a.nome(), a.cursosConcluidos(), 100*a.cursosConcluidos()))
            .toList();
    }
}
