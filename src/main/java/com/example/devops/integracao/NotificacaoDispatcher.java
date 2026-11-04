package com.example.devops.integracao;

import io.micrometer.core.instrument.Gauge;
import io.micrometer.core.instrument.MeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import java.io.IOException;

@Component
public class NotificacaoDispatcher {
    private static final Logger log = LoggerFactory.getLogger(NotificacaoDispatcher.class);
    private final NotificacaoRepository repository;
    private final B1HttpClient client;
    @Value("${b1.dispatch.enabled:true}") private boolean enabled = true;
    public NotificacaoDispatcher(NotificacaoRepository repository, B1HttpClient client, MeterRegistry registry) {
        this.repository = repository;
        this.client = client;
        Gauge.builder("b1.notificacoes.pendentes", repository, NotificacaoRepository::countByEntregueFalse).register(registry);
    }
    @Scheduled(fixedDelayString = "${b1.notificacoes.intervalo-ms:5000}", initialDelayString = "${b1.notificacoes.intervalo-ms:5000}")
    public void executar() {
        if (enabled) entregarPendentes();
    }
    public void entregarPendentes() {
        for (var evento : repository.findTop50ByEntregueFalseOrderByEventIdAsc()) {
            try {
                client.notificar(evento);
                evento.confirmarEntrega();
                repository.save(evento);
                log.info("Notificação confirmada eventId={}", evento.getEventId());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            } catch (IOException | RuntimeException e) {
                log.warn("Notificação permanece pendente eventId={} causa={}", evento.getEventId(), e.toString());
            }
        }
    }
}
