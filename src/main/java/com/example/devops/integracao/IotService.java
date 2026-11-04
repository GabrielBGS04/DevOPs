package com.example.devops.integracao;

import com.example.devops.curso.application.CursoService;
import com.example.devops.dto.ConclusaoCursoDTO;
import com.example.devops.service.AlunoService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.Set;

@Service
public class IotService {
    public record Evento(String eventId, String tipo, String dispositivoId, Long alunoId, Long cursoId, Double nota) { }
    private final IotRepository repository;
    private final AlunoService alunos;
    private final CursoService cursos;
    private final IotInbox inbox;
    public IotService(IotRepository repository, AlunoService alunos, CursoService cursos, IotInbox inbox) {
        this.repository = repository;
        this.alunos = alunos;
        this.cursos = cursos;
        this.inbox = inbox;
    }
    @Transactional
    public void receber(Evento evento) {
        textoObrigatorio(evento.eventId());
        textoObrigatorio(evento.tipo());
        textoObrigatorio(evento.dispositivoId());
        if (!Set.of("PRESENCA", "INICIO", "CONCLUSAO").contains(evento.tipo())) throw new IllegalArgumentException("Tipo de evento inválido");
        if (evento.alunoId() == null) throw new IllegalArgumentException("Aluno obrigatório");
        if (evento.cursoId() == null) throw new IllegalArgumentException("Curso obrigatório");
        if ("CONCLUSAO".equals(evento.tipo())) validarNota(evento.nota());
        if (repository.existsById(evento.eventId())) return;
        alunos.buscarPorId(evento.alunoId());
        cursos.buscarPorId(evento.cursoId());
        // A unicidade é conferida no banco antes do efeito. Ambos pertencem à mesma transação.
        inbox.inserir(new IotEvento(evento));
        if ("CONCLUSAO".equals(evento.tipo())) {
            var dto = new ConclusaoCursoDTO();
            dto.setCursoId(evento.cursoId());
            dto.setNota(evento.nota());
            alunos.processarConclusao(evento.alunoId(), dto);
        }
    }
    public boolean recebido(String eventId) { return repository.existsById(eventId); }
    private static void textoObrigatorio(String texto) {
        if (texto == null || texto.isBlank()) throw new IllegalArgumentException("Identificador, tipo e dispositivo são obrigatórios");
    }
    private static void validarNota(Double nota) {
        if (nota == null) throw new IllegalArgumentException("Nota obrigatória para conclusão");
        if (!Double.isFinite(nota) || nota < 0 || nota > 10) throw new IllegalArgumentException("Nota inválida");
    }
}
