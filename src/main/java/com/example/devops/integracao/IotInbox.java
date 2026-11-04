package com.example.devops.integracao;

import jakarta.persistence.EntityManager;
import org.springframework.stereotype.Repository;

@Repository
public class IotInbox {
    private final EntityManager entityManager;

    public IotInbox(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    public void inserir(IotEvento evento) {
        // Identificador atribuído pelo dispositivo: sempre INSERT, nunca merge de evento existente.
        entityManager.persist(evento);
        entityManager.flush();
    }
}
