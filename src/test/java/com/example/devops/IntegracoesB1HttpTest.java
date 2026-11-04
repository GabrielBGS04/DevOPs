package com.example.devops;

import com.example.devops.integracao.B1HttpClient;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.junit.jupiter.api.Test;
import tools.jackson.databind.json.JsonMapper;
import java.util.List;
import static org.assertj.core.api.Assertions.*;

class IntegracoesB1HttpTest {
    @Test void conexaoRecusadaDegradaAmbosFluxos() {
        var metrics = new SimpleMeterRegistry();
        var client = new B1HttpClient("http://127.0.0.1:1", "http://127.0.0.1:1", JsonMapper.builder().build(), metrics);
        assertThat(client.recomendar(1L, List.of(), List.of()).disponivel()).isFalse();
        assertThat(client.perguntar("Java").disponivel()).isFalse();
        assertThat(metrics.counter("b1.ia.falhas").count()).isEqualTo(2);
    }
    @Test void interrupcaoPreservaFlagEDegrada() {
        var client = new B1HttpClient("http://127.0.0.1:1", "http://127.0.0.1:1", JsonMapper.builder().build(), new SimpleMeterRegistry());
        Thread.currentThread().interrupt();
        try {
            assertThat(client.perguntar("Java").disponivel()).isFalse();
            assertThat(Thread.currentThread().isInterrupted()).isTrue();
        } finally { Thread.interrupted(); }
        Thread.currentThread().interrupt();
        try {
            assertThat(client.recomendar(1L, List.of(), List.of()).disponivel()).isFalse();
            assertThat(Thread.currentThread().isInterrupted()).isTrue();
        } finally { Thread.interrupted(); }
    }
}
