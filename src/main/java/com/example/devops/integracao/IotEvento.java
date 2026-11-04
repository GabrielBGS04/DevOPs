package com.example.devops.integracao;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "b1_iot_inbox")
public class IotEvento {
    @Id private String eventId;
    private String tipo;
    private String dispositivoId;
    private Long alunoId;
    private Long cursoId;
    private Double nota;
    protected IotEvento() { }
    public IotEvento(IotService.Evento evento) {
        eventId = evento.eventId();
        tipo = evento.tipo();
        dispositivoId = evento.dispositivoId();
        alunoId = evento.alunoId();
        cursoId = evento.cursoId();
        nota = evento.nota();
    }
}
