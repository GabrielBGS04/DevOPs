package com.example.devops.gamificacao.domain;

import com.example.devops.domain.Plano;

/** Política pura: não depende de Spring, HTTP ou persistência. */
public class PoliticaBonus {
    public static final double NOTA_MINIMA = 8.5;
    public static final int BONUS = 3;

    public int calcularBonus(Plano plano, double nota) {
        if (plano == null) throw new IllegalArgumentException("O plano do aluno é obrigatório");
        if (!Double.isFinite(nota) || nota < 0 || nota > 10)
            throw new IllegalArgumentException("A nota deve estar entre 0 e 10");
        return plano == Plano.BASICO && nota >= NOTA_MINIMA ? BONUS : 0;
    }
}
