package com.example.devops.integracao;

import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
public class IotController {
    private final IotService service;
    public IotController(IotService service) { this.service = service; }
    @PostMapping("/api/iot/eventos")
    public Map<String, Boolean> receber(@RequestBody IotService.Evento evento) {
        try {
            service.receber(evento);
        } catch (DataIntegrityViolationException e) {
            // Outra transação pode ter confirmado o mesmo ID; a transação perdedora já foi revertida.
            if (!service.recebido(evento.eventId())) throw e;
        }
        return Map.of("aceito", true);
    }
}
