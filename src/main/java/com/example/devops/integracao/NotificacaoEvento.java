package com.example.devops.integracao;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.util.UUID;

@Entity
@Table(name = "b1_notificacao_outbox")
public class NotificacaoEvento {
    @Id private String eventId;
    private Long alunoId;
    private Long cursoId;
    private double nota;
    private boolean entregue;
    protected NotificacaoEvento() { }
    public NotificacaoEvento(Long alunoId, Long cursoId, double nota) {
        this.eventId = UUID.randomUUID().toString();
        this.alunoId = alunoId;
        this.cursoId = cursoId;
        this.nota = nota;
    }
    public String getEventId() { return eventId; }
    public record Payload(String eventId, Long alunoId, Long cursoId, double nota) { }
    public Payload payload() { return new Payload(eventId, alunoId, cursoId, nota); }
    public void confirmarEntrega() { entregue = true; }
}
