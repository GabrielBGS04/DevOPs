package com.example.devops;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Curso;
import com.example.devops.domain.Plano;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.service.AlunoService;
import com.example.devops.service.CursoService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@ActiveProfiles("test")
class BancoH2IntegrationTest {

    @Autowired
    private AlunoService alunoService;

    @Autowired
    private CursoService cursoService;

    @Test
    void devePersistirConclusaoDeCursoNoBancoH2() {
        Aluno aluno = alunoService.criar("Aluno H2", Plano.BASICO);
        Curso curso = cursoService.criar("Persistência com H2");
        ConclusaoCursoDTO conclusao = new ConclusaoCursoDTO();
        conclusao.setCursoId(curso.getId());
        conclusao.setNota(8.5);

        Aluno atualizado = alunoService.processarConclusao(aluno.getId(), conclusao);

        assertThat(atualizado.getCursosDisponiveis()).isEqualTo(3);
        assertThat(atualizado.getHistorico()).containsEntry("Persistência com H2", 8.5);
    }
}
