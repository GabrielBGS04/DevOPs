package com.example.devops.domain;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class CursoTest {

    @ParameterizedTest
    @NullAndEmptySource
    @ValueSource(strings = {" ", "\t\n"})
    void deveRejeitarNomeAusenteOuEmBranco(String nome) {
        assertThatThrownBy(() -> new Curso(nome)).isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    void deveNormalizarNomeDoCurso() {
        assertThat(new Curso("  Docker  ").getNome()).isEqualTo("Docker");
    }
}
