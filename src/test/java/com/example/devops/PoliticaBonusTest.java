package com.example.devops;

import com.example.devops.domain.Plano;
import com.example.devops.gamificacao.domain.PoliticaBonus;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.*;

class PoliticaBonusTest {
    private final PoliticaBonus regra = new PoliticaBonus();
    @ParameterizedTest
    @CsvSource({"BASICO,8.49,0", "BASICO,8.5,3", "BASICO,10,3", "PREMIUM,10,0", "BASICO,0,0"})
    void calculaBonus(Plano plano, double nota, int bonus) {
        assertThat(regra.calcularBonus(plano, nota)).isEqualTo(bonus);
    }
    @ParameterizedTest
    @ValueSource(doubles={-1,11,Double.NaN,Double.POSITIVE_INFINITY,Double.NEGATIVE_INFINITY})
    void rejeitaNotaInvalida(double nota) {
        assertThatThrownBy(() -> regra.calcularBonus(Plano.BASICO, nota))
            .isInstanceOf(IllegalArgumentException.class);
    }
    @Test void rejeitaPlanoAusente() {
        assertThatThrownBy(() -> regra.calcularBonus(null, 8.5))
            .isInstanceOf(IllegalArgumentException.class);
    }
}
