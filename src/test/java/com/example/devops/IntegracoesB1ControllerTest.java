package com.example.devops;

import com.example.devops.integracao.IotController;
import com.example.devops.integracao.IotService;
import org.junit.jupiter.api.Test;
import org.springframework.dao.DataIntegrityViolationException;
import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class IntegracoesB1ControllerTest {
    @Test void colisaoDeIdConfirmadoPorOutraTransacaoRetornaSucesso() {
        // Reproduz deterministicamente a janela entre existsById e a inserção concorrente.
        IotService service = mock(IotService.class);
        var evento = new IotService.Evento("corrida", "CONCLUSAO", "sensor", 1L, 1L, 8.5);
        doThrow(new DataIntegrityViolationException("ID inserido pela outra transação")).when(service).receber(evento);
        when(service.recebido("corrida")).thenReturn(true);
        assertThat(new IotController(service).receber(evento)).containsEntry("aceito", true);
    }
}
