package com.example.devops;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Plano;
import com.example.devops.curso.domain.Curso;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.gamificacao.application.ConclusaoDeCurso;
import com.example.devops.gamificacao.application.ConclusaoPort;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class ConclusaoDeCursoTest {
    @Test void trocaPersistenciaPorMemoriaSemSpring() {
        Aluno aluno = new Aluno("Memória", Plano.BASICO);
        Curso curso = new Curso("Java");
        ConclusaoPort memoria = new ConclusaoPort() {
            public Aluno buscarAluno(Long id) { return aluno; }
            public Curso buscarCurso(Long id) { return curso; }
            public Aluno salvar(Aluno a) { return a; }
        };
        ConclusaoDeCurso caso = new ConclusaoDeCurso(memoria);
        ConclusaoCursoDTO dto = new ConclusaoCursoDTO(); dto.setCursoId(1L); dto.setNota(8.5);
        assertThat(caso.executar(1L, dto).getCursosDisponiveis()).isEqualTo(3);
        assertThat(aluno.getHistorico()).containsEntry("Java",8.5);
        dto.setCursoId(2L); dto.setNota(7);
        assertThat(caso.executar(1L,dto).getCursosDisponiveis()).isEqualTo(3);
    }
}
