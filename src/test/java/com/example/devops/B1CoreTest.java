package com.example.devops;

import com.example.devops.repository.AlunoRepository;
import com.example.devops.curso.internal.persistence.CursoRepository;
import com.example.devops.domain.Aluno;
import com.example.devops.curso.domain.Curso;
import com.example.devops.domain.Plano;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class B1CoreTest {
    @Autowired MockMvc mvc;
    @Autowired AlunoRepository alunos;
    @Autowired CursoRepository cursos;
    @BeforeEach void limpar() { alunos.deleteAll(); cursos.deleteAll(); }

    @Test void rankingVazio() throws Exception {
        mvc.perform(get("/api/ranking")).andExpect(status().isOk()).andExpect(content().json("[]"));
    }
    @Test void rankingPontuaHistoricoEOrdenaComDesempatePorId() throws Exception {
        Curso curso = cursos.save(new Curso("Java"));
        Aluno primeiro = new Aluno("Primeiro", Plano.BASICO);
        primeiro.concluirCurso(curso, 9);
        alunos.save(primeiro);
        Aluno segundo = new Aluno("Segundo", Plano.BASICO);
        segundo.concluirCurso(curso, 7);
        alunos.save(segundo);
        alunos.save(new Aluno("Sem histórico", Plano.PREMIUM));
        mvc.perform(get("/api/ranking")).andExpect(status().isOk())
            .andExpect(jsonPath("$[0].nome").value("Primeiro"))
            .andExpect(jsonPath("$[0].pontos").value(100))
            .andExpect(jsonPath("$[1].nome").value("Segundo"))
            .andExpect(jsonPath("$[2].pontos").value(0));
    }
    @Test void notaNaoFinitaNaoDeveAlterarEstado() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        assertThatThrownBy(() -> aluno.concluirCurso(new Curso("Java"), Double.NaN))
            .isInstanceOf(IllegalArgumentException.class);
        assertThat(aluno.getHistorico()).isEmpty();
    }
    @Test void consultaElegibilidadeDoPlanoBasicoNosDoisLadosDoLimite() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        assertThat(aluno.temDireitoABonus(8.5)).isTrue();
        assertThat(aluno.temDireitoABonus(8.49)).isFalse();
    }
    @Test void rankingContaCursosNoBancoSemExporHistorico() throws Exception {
        Curso java = cursos.save(new Curso("Java"));
        Curso docker = cursos.save(new Curso("Docker"));
        Aluno menos = new Aluno("Um curso", Plano.BASICO);
        menos.concluirCurso(java,7); alunos.save(menos);
        Aluno mais = new Aluno("Dois cursos", Plano.BASICO);
        mais.concluirCurso(java,8.5); mais.concluirCurso(docker,9); alunos.save(mais);
        mvc.perform(get("/api/ranking")).andExpect(status().isOk())
            .andExpect(jsonPath("$[0].nome").value("Dois cursos"))
            .andExpect(jsonPath("$[0].cursosConcluidos").value(2))
            .andExpect(jsonPath("$[0].pontos").value(200))
            .andExpect(jsonPath("$[0].historico").doesNotExist())
            .andExpect(jsonPath("$[1].pontos").value(100));
    }
}
