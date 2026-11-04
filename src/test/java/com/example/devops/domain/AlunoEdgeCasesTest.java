package com.example.devops.domain;

import com.example.devops.curso.domain.Curso;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class AlunoEdgeCasesTest {

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {" ", "\t\n"})
    void deveRejeitarNomeAusenteOuEmBranco(String nome) {
        assertThatThrownBy(() -> new Aluno(nome, Plano.BASICO))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void deveRejeitarPlanoAusente() {
        assertThatThrownBy(() -> new Aluno("Ana", null))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void deveNormalizarNomeEIniciarSemHistoricoOuBonus() {
        Aluno aluno = new Aluno("  Ana  ", Plano.PREMIUM);

        assertThat(aluno.getNome()).isEqualTo("Ana");
        assertThat(aluno.getPlano()).isEqualTo(Plano.PREMIUM);
        assertThat(aluno.getMediaGeral()).isZero();
        assertThat(aluno.getCursosDisponiveis()).isZero();
        assertThat(aluno.getHistorico()).isEmpty();
    }

    @ParameterizedTest
    @CsvSource({"0, 0", "8.49, 0", "8.5, 3", "10, 3"})
    void deveRespeitarOsLimitesDeNotaEBonus(double nota, int cursosEsperados) {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        Curso curso = new Curso("Java");

        aluno.concluirCurso(curso, nota);

        assertThat(aluno.getNotaDoCurso(curso)).isEqualTo(nota);
        assertThat(aluno.getCursosDisponiveis()).isEqualTo(cursosEsperados);
    }

    @Test
    void naoDeveConcederBonusAoPlanoPremium() {
        Aluno aluno = new Aluno("Ana", Plano.PREMIUM);
        Curso curso = new Curso("Java");

        aluno.concluirCurso(curso, 10);

        assertThat(aluno.temDireitoABonus(10)).isFalse();
        assertThat(aluno.getNotaDoCurso(curso)).isEqualTo(10);
        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    @ParameterizedTest
    @ValueSource(doubles = {-0.01, 10.01})
    void deveRejeitarNotaForaDoIntervaloSemAlterarHistoricoOuBonus(double nota) {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);

        assertThatThrownBy(() -> aluno.concluirCurso(new Curso("Java"), nota))
                .isInstanceOf(IllegalArgumentException.class);
        assertThat(aluno.getHistorico()).isEmpty();
        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    @Test
    void deveRejeitarConclusaoSemCurso() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);

        assertThatThrownBy(() -> aluno.concluirCurso(null, 9))
                .isInstanceOf(IllegalArgumentException.class);
        assertThat(aluno.getHistorico()).isEmpty();
        assertThat(aluno.getCursosDisponiveis()).isZero();
    }

    @Test
    void deveRejeitarConsultaDeNotaSemCurso() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);

        assertThatThrownBy(() -> aluno.getNotaDoCurso(null))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void deveRejeitarConsultaDeCursoNaoConcluido() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        aluno.concluirCurso(new Curso("Java"), 9);

        assertThatThrownBy(() -> aluno.getNotaDoCurso(new Curso("Docker")))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void deveConsultarNotaPeloNomeDoCurso() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        aluno.concluirCurso(new Curso("Java"), 9);

        assertThat(aluno.getNotaDoCurso(new Curso("Java"))).isEqualTo(9);
    }

    @Test
    void deveAcumularBonusDeCursosDiferentes() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        aluno.concluirCurso(new Curso("Java"), 8.5);
        aluno.concluirCurso(new Curso("Docker"), 10);

        assertThat(aluno.getCursosDisponiveis()).isEqualTo(6);
        assertThat(aluno.getHistorico()).containsEntry("Java", 8.5).containsEntry("Docker", 10.0);
        assertThat(aluno.getMediaGeral()).isEqualTo(9);
    }

    @Test
    void deveProtegerHistoricoContraAlteracaoExterna() {
        Aluno aluno = new Aluno("Ana", Plano.BASICO);
        Curso curso = new Curso("Java");
        aluno.concluirCurso(curso, 7);

        assertThatThrownBy(() -> aluno.getHistorico().put("Java", 10.0))
                .isInstanceOf(UnsupportedOperationException.class);
        assertThat(aluno.getNotaDoCurso(curso)).isEqualTo(7);
        assertThat(aluno.getCursosDisponiveis()).isZero();
    }
}
