package com.example.devops.integracao;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import tools.jackson.databind.json.JsonMapper;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;

@Component
public class B1HttpClient {
    public record CursoItem(Long id, String nome) { }
    public record Recomendacoes(Boolean disponivel, List<CursoItem> recomendacoes) { }
    public record Resposta(Boolean disponivel, String resposta, String fonte) { }
    private final String iaUrl;
    private final String notificacoesUrl;
    private final JsonMapper mapper;
    private final Counter falhas;
    private final HttpClient client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();

    public B1HttpClient(@Value("${b1.ia.url:http://localhost:8001}") String iaUrl,
                        @Value("${b1.notificacoes.url:http://localhost:8002}") String notificacoesUrl,
                        JsonMapper mapper, MeterRegistry registry) {
        this.iaUrl = iaUrl;
        this.notificacoesUrl = notificacoesUrl;
        this.mapper = mapper;
        this.falhas = registry.counter("b1.ia.falhas");
    }

    public Recomendacoes recomendar(Long alunoId, List<String> historico, List<CursoItem> cursos) {
        try {
            Recomendacoes resposta = mapper.readValue(post(iaUrl + "/recomendacoes",
                    Map.of("alunoId", alunoId, "historico", historico, "cursos", cursos)), Recomendacoes.class);
            if (resposta.disponivel() == null || resposta.recomendacoes() == null) throw new IOException("Resposta incompleta da IA");
            for (CursoItem curso : resposta.recomendacoes()) {
                if (curso == null || curso.id() == null || curso.nome() == null || curso.nome().isBlank())
                    throw new IOException("Curso inválido na resposta da IA");
            }
            return resposta;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (IOException | RuntimeException e) {
            // A falha externa vira uma resposta degradada; não há retentativa na requisição.
        }
        falhas.increment();
        return new Recomendacoes(false, List.of());
    }

    public Resposta perguntar(String pergunta) {
        try {
            Resposta resposta = mapper.readValue(post(iaUrl + "/assistente", Map.of("pergunta", pergunta)), Resposta.class);
            if (resposta.disponivel() == null || resposta.resposta() == null) throw new IOException("Resposta incompleta da IA");
            if (resposta.disponivel()) {
                if (resposta.resposta().isBlank() || resposta.fonte() == null || resposta.fonte().isBlank())
                    throw new IOException("Resposta disponível sem conteúdo ou fonte");
            }
            return resposta;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } catch (IOException | RuntimeException e) {
            // A indisponibilidade do assistente não impede o uso do Core.
        }
        falhas.increment();
        return new Resposta(false, "Assistente temporariamente indisponível.", null);
    }

    public void notificar(NotificacaoEvento evento) throws IOException, InterruptedException {
        post(notificacoesUrl + "/notificacoes", evento.payload());
    }

    private String post(String url, Object payload) throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(2))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(payload))).build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() / 100 != 2) throw new IOException("HTTP " + response.statusCode());
        return response.body();
    }
}
