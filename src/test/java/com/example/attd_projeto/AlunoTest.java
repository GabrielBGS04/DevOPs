package com.example.attd_projeto;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

public class AlunoTest {

    // RED — BDD 1: nota 8,5 deve liberar 3 cursos.
    @Test
    void bdd1_deveLiberarTresCursosComNotaOitoVirgulaCinco() {
        Aluno aluno = new Aluno("João", Plano.BASICO);

        aluno.concluirCurso(new Curso("Testes de Software"), 8.5);

        assertThat(aluno.getCursosDisponiveis()).isEqualTo(3);
    }

    // GREEN — BDD 1, TDD 1: ao concluir um curso com nota 8,5,
    // a nota deve ser armazenada no histórico do aluno.
    @Test
    void deveAtualizarHistoricoAoConcluirCurso() {
        Aluno aluno = new Aluno("João", Plano.BASICO);
        Curso curso = new Curso("Java Básico");

        aluno.concluirCurso(curso, 8.5);

        assertThat(aluno.getNotaDoCurso(curso)).isEqualTo(8.5);
    }

    // GREEN — BDD 1, TDD 2: a nota 8,5 deve conceder direito ao bônus.
    @Test
    void deveDarDireitoABonusComNotaMinimaDeOitoVirgulaCinco() {
        Aluno aluno = new Aluno("João", Plano.BASICO);

        boolean temBonus = aluno.temDireitoABonus(8.5);

        assertThat(temBonus).isTrue();
    }

    // GREEN — BDD 1, TDD 3: a conclusão com nota 8,5 deve liberar 3 cursos.
    @Test
    void deveLiberarTresCursosComNotaMinimaDeOitoVirgulaCinco() {
        Aluno aluno = new Aluno("João", Plano.BASICO);

        aluno.concluirCurso(new Curso("Testes"), 8.5);

        assertThat(aluno.getCursosDisponiveis()).isEqualTo(3);
    }

    // RED — BDD 2: nota 7,0 não deve liberar cursos extras.
    @Test
    void bdd2_naoDeveLiberarCursosExtraSeNotaForInferiorOuIgualASete() {
        Aluno aluno = new Aluno("Maria", Plano.BASICO);

        aluno.concluirCurso(new Curso("Docker"), 7.0);

        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    // GREEN — BDD 2, TDD 1: nota 7,0 não deve liberar cursos extras.
    @Test
    void naoDeveLiberarCursosExtrasComNotaIgualASete() {
        Aluno aluno = new Aluno("Maria", Plano.BASICO);

        aluno.concluirCurso(new Curso("Docker"), 7.0);

        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    // GREEN — BDD 2, TDD 2: nota 5,5 não deve liberar cursos extras.
    @Test
    void naoDeveLiberarCursosExtrasComNotaAbaixoDeSete() {
        Aluno aluno = new Aluno("Pedro", Plano.BASICO);

        aluno.concluirCurso(new Curso("Linux"), 5.5);

        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    // GREEN — BDD 2, TDD 3: média inteira de 9,0 e 4,0 deve ser 6.
    @Test
    void deveCalcularMediaGeralDosCursosConcluidos() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);

        aluno.concluirCurso(1, 9.0);
        aluno.concluirCurso(2, 4.0);

        assertThat(aluno.getMediaGeral()).isEqualTo(6);
    }
}
