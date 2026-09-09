package com.example.attd_projeto;

import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

public class AlunoTest {

    @Test
    public void deveLiberarTresCursosComMediaMaiorQueSete() {
        Aluno aluno = new Aluno("João", Plano.BASICO);
        aluno.concluirCurso(new Curso("Testes de Software"), 8.5);

        assertThat(aluno.getCursosDisponiveis()).isEqualTo(3);
    }

    @Test
    public void naoDeveLiberarCursosExtraSeNotaForInferiorOuIgualASete() {
        Aluno aluno = new Aluno("Maria", Plano.BASICO);
        aluno.concluirCurso(new Curso("Docker"), 7.0);

        assertThat(aluno.getCursosDisponiveis()).isZero();
    }
}