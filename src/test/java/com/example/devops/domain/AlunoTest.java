package com.example.devops.domain;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class AlunoTest {

    @Test
    void deveRegistrarNotaELiberarTresCursosParaPlanoBasicoComNotaOitoVirgulaCinco() {
        Aluno aluno = new Aluno("João", Plano.BASICO);
        Curso curso = new Curso("Testes de Software");

        aluno.concluirCurso(curso, 8.5);

        assertThat(aluno.getNotaDoCurso(curso)).isEqualTo(8.5);
        assertThat(aluno.getCursosDisponiveis()).isEqualTo(3);
    }

    @Test
    void naoDeveLiberarCursosExtrasParaNotaSete() {
        Aluno aluno = new Aluno("Maria", Plano.BASICO);

        aluno.concluirCurso(new Curso("Docker"), 7.0);

        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    @Test
    void deveCalcularMediaInteiraDoHistorico() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);

        aluno.concluirCurso(new Curso("Java"), 9.0);
        aluno.concluirCurso(new Curso("Linux"), 4.0);

        assertThat(aluno.getMediaGeral()).isEqualTo(6);
    }
}
