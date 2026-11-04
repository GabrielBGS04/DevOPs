package com.example.devops;

import com.example.devops.domain.Plano;
import com.example.devops.service.AlunoService;
import com.example.devops.curso.application.CursoService;
import com.example.devops.integracao.*;
import com.sun.net.httpserver.HttpServer;
import io.micrometer.core.instrument.MeterRegistry;
import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.bean.override.mockito.MockitoSpyBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.http.MediaType;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;
import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;
import static org.mockito.Mockito.doAnswer;
import static org.mockito.ArgumentMatchers.*;

@SpringBootTest(properties = "b1.dispatch.enabled=false")
@AutoConfigureMockMvc
@ActiveProfiles("test")
class IntegracoesB1Test {
    static HttpServer server;
    static volatile String resposta = "{}";
    static volatile String recebido;
    static volatile int codigo = 200;
    static volatile long atraso;
    static {
        try {
            server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.setExecutor(Executors.newCachedThreadPool());
            server.createContext("/", exchange -> {
                recebido = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
                try { Thread.sleep(atraso); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
                byte[] body = resposta.getBytes(StandardCharsets.UTF_8);
                try {
                    exchange.sendResponseHeaders(codigo, body.length);
                    exchange.getResponseBody().write(body);
                } finally { exchange.close(); }
            });
            server.start();
        } catch (Exception e) { throw new ExceptionInInitializerError(e); }
    }
    @DynamicPropertySource static void properties(DynamicPropertyRegistry registry) {
        registry.add("b1.ia.url", () -> "http://127.0.0.1:" + server.getAddress().getPort());
        registry.add("b1.notificacoes.url", () -> "http://127.0.0.1:" + server.getAddress().getPort());
    }
    @Autowired MockMvc mvc;
    @Autowired AlunoService alunos;
    @Autowired CursoService cursos;
    @Autowired NotificacaoRepository outbox;
    @MockitoSpyBean IotRepository inbox;
    @MockitoSpyBean B1HttpClient http;
    @Autowired MeterRegistry metrics;
    @Autowired org.springframework.transaction.PlatformTransactionManager transactionManager;
    @Autowired IotService iot;
    @Autowired NotificacaoDispatcher scheduledDispatcher;
    @BeforeEach void reset() { resposta = "{}"; codigo = 200; atraso = 0; recebido = null; inbox.deleteAll(); outbox.deleteAll(); }
    @AfterAll static void stop() { server.stop(0); }

    @Test void recomendacoesEnviamCatalogoEHistoricoEAlunoInexistenteRetorna404() throws Exception {
        var aluno = alunos.criar("IA B1", Plano.BASICO);
        var curso = cursos.criar("Java B1");
        resposta = "{\"disponivel\":true,\"recomendacoes\":[{\"id\":" + curso.getId() + ",\"nome\":\"Java B1\"}]}";
        mvc.perform(get("/api/alunos/{id}/recomendacoes", aluno.getId()))
                .andExpect(status().isOk()).andExpect(jsonPath("$.disponivel").value(true))
                .andExpect(jsonPath("$.recomendacoes[0].nome").value("Java B1"));
        assertThat(recebido).contains("\"alunoId\":" + aluno.getId(), "\"historico\":[]", "Java B1");
        mvc.perform(get("/api/alunos/999999/recomendacoes")).andExpect(status().isNotFound());
    }
    @Test void assistenteRetornaRespostaEFonte() throws Exception {
        resposta = "{\"disponivel\":true,\"resposta\":\"Estude Java\",\"fonte\":\"conteudo.md\"}";
        mvc.perform(post("/api/assistente").contentType(MediaType.APPLICATION_JSON).content("{\"pergunta\":\"Como estudar?\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.resposta").value("Estude Java"))
                .andExpect(jsonPath("$.fonte").value("conteudo.md"));
        assertThat(recebido).contains("Como estudar?");
        for (String body : new String[]{"{}", "{\"pergunta\":\" \"}"})
            mvc.perform(post("/api/assistente").contentType(MediaType.APPLICATION_JSON).content(body)).andExpect(status().isBadRequest());
    }
    @Test void falhasHttpJsonETimeoutDegradamSemRetentativa() throws Exception {
        var aluno = alunos.criar("Degradacao", Plano.BASICO);
        double antes = metrics.counter("b1.ia.falhas").count();
        for (String body : new String[]{"invalido", "{}", "{\"disponivel\":true,\"recomendacoes\":null}"}) {
            resposta = body;
            mvc.perform(get("/api/alunos/{id}/recomendacoes", aluno.getId())).andExpect(status().isOk())
                    .andExpect(jsonPath("$.disponivel").value(false)).andExpect(jsonPath("$.recomendacoes").isEmpty());
        }
        codigo = 503;
        mvc.perform(post("/api/assistente").contentType(MediaType.APPLICATION_JSON).content("{\"pergunta\":\"Java\"}"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.disponivel").value(false));
        codigo = 200; atraso = 2300;
        long inicio = System.nanoTime();
        mvc.perform(get("/api/alunos/{id}/recomendacoes", aluno.getId())).andExpect(jsonPath("$.disponivel").value(false));
        assertThat((System.nanoTime() - inicio) / 1_000_000).isBetween(1800L, 2250L);
        assertThat(metrics.counter("b1.ia.falhas").count() - antes).isEqualTo(5);
    }
    @Test void respostasIncompletasDoAssistenteDegradamERecomendacaoValidaMantemDisponibilidade() throws Exception {
        for (String body : new String[]{"{}", "{\"disponivel\":true}"}) {
            resposta = body;
            mvc.perform(post("/api/assistente").contentType(MediaType.APPLICATION_JSON).content("{\"pergunta\":\"Java\"}"))
                    .andExpect(jsonPath("$.disponivel").value(false)).andExpect(jsonPath("$.resposta").isNotEmpty());
        }
        resposta = "{\"disponivel\":false,\"recomendacoes\":[]}";
        assertThat(http.recomendar(1L, java.util.List.of("Java"), java.util.List.of()).disponivel()).isFalse();
    }
    @Test void recomendacaoSemIdentidadeOuNomeDoCursoDegrada() {
        for (String body : new String[]{"{\"disponivel\":true,\"recomendacoes\":[{}]}", "{\"disponivel\":true,\"recomendacoes\":[{\"id\":1}]}", "{\"disponivel\":true,\"recomendacoes\":[{\"id\":1,\"nome\":\" \"}]}", "{\"disponivel\":true,\"recomendacoes\":[null]}"}) {
            resposta = body;
            assertThat(http.recomendar(1L, java.util.List.of(), java.util.List.of()).disponivel()).isFalse();
        }
    }
    @Test void assistenteDisponivelExigeTextoEFontePreenchidos() {
        for (String body : new String[]{
                "{\"disponivel\":true,\"resposta\":\"\",\"fonte\":\"local.md\"}",
                "{\"disponivel\":true,\"resposta\":\" \" ,\"fonte\":\"local.md\"}",
                "{\"disponivel\":true,\"resposta\":\"Java\"}",
                "{\"disponivel\":true,\"resposta\":\"Java\",\"fonte\":\"\"}",
                "{\"disponivel\":true,\"resposta\":\"Java\",\"fonte\":\" \"}"}) {
            resposta = body;
            var resultado = http.perguntar("Java");
            assertThat(resultado.disponivel()).isFalse();
            assertThat(resultado.resposta()).isNotBlank();
        }
        resposta = "{\"disponivel\":false,\"resposta\":\"Conteúdo indisponível\",\"fonte\":null}";
        assertThat(http.perguntar("Java").resposta()).isEqualTo("Conteúdo indisponível");
    }
    @Test void chamadaLentaDaIaOcorreSemTransacaoDoBancoEAindaDegradaNoTimeout() throws Exception {
        var aluno = alunos.criar("Sem transacao HTTP", Plano.BASICO);
        var curso = cursos.criar("Historico antes do HTTP");
        var conclusao = new com.example.devops.dto.ConclusaoCursoDTO();
        conclusao.setCursoId(curso.getId());
        conclusao.setNota(7);
        alunos.processarConclusao(aluno.getId(), conclusao);
        var transacaoDuranteHttp = new java.util.concurrent.atomic.AtomicBoolean(true);
        doAnswer(invocation -> {
            transacaoDuranteHttp.set(org.springframework.transaction.support.TransactionSynchronizationManager.isActualTransactionActive());
            return invocation.callRealMethod();
        }).when(http).recomendar(anyLong(), anyList(), anyList());
        atraso = 2300;
        mvc.perform(get("/api/alunos/{id}/recomendacoes", aluno.getId()))
                .andExpect(status().isOk()).andExpect(jsonPath("$.disponivel").value(false));
        assertThat(transacaoDuranteHttp).isFalse();
        assertThat(recebido).contains("Historico antes do HTTP");
        mvc.perform(get("/api/alunos/{id}", aluno.getId())).andExpect(status().isOk());
    }
    @Test void inboxDeduplicaConclusaoEPersisteOutboxAteConfirmacao() throws Exception {
        var aluno = alunos.criar("IoT B1", Plano.BASICO);
        var curso = cursos.criar("MQTT B1");
        String evento = evento("iot-b1", "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":8.5");
        for (int i = 0; i < 2; i++) mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento)).andExpect(status().isOk());
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isEqualTo(3);
        assertThat(inbox.count()).isEqualTo(1);
        assertThat(outbox.countByEntregueFalse()).isEqualTo(1);
        String eventId = outbox.findAll().get(0).getEventId();
        var dispatcher = new NotificacaoDispatcher(outbox, http, metrics);
        codigo = 503; dispatcher.entregarPendentes();
        assertThat(outbox.countByEntregueFalse()).isEqualTo(1);
        assertThat(recebido).contains(eventId, "\"nota\":8.5");
        mvc.perform(get("/api/notificacoes/pendentes")).andExpect(jsonPath("$.quantidade").value(1));
        assertThat(metrics.get("b1.notificacoes.pendentes").gauge().value()).isEqualTo(1);
        codigo = 200; dispatcher.executar();
        assertThat(outbox.countByEntregueFalse()).isZero();
        assertThat(recebido).contains(eventId);
        dispatcher.entregarPendentes();
    }
    @Test void dispatcherDesabilitadoNaoEntregaEInterrupcaoPreservaPendencia() {
        var aluno = alunos.criar("Interrupcao", Plano.BASICO);
        var curso = cursos.criar("Interrupcao");
        iot.receber(new IotService.Evento("interrupt", "CONCLUSAO", "sensor", aluno.getId(), curso.getId(), 9.0));
        scheduledDispatcher.executar();
        assertThat(outbox.countByEntregueFalse()).isEqualTo(1);
        Thread.currentThread().interrupt();
        try {
            new NotificacaoDispatcher(outbox, http, metrics).entregarPendentes();
            assertThat(Thread.currentThread().isInterrupted()).isTrue();
        } finally { Thread.interrupted(); }
        assertThat(outbox.countByEntregueFalse()).isEqualTo(1);
    }
    @Test void erroRealDePersistenciaNaoConfirmaEventoNemConcedeBonus() {
        var aluno = alunos.criar("Erro Persistencia", Plano.BASICO);
        var curso = cursos.criar("Erro Persistencia");
        String evento = evento("x".repeat(300), "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":9");
        assertThatThrownBy(() -> mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento)))
                .hasCauseInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);
        assertThat(inbox.count()).isZero();
        assertThat(outbox.count()).isZero();
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isZero();
    }
    @Test void notaNaoFinitaRejeitadaSemPersistir() {
        assertThatThrownBy(() -> iot.receber(new IotService.Evento("nan", "CONCLUSAO", "sensor", 1L, 1L, Double.NaN)))
                .isInstanceOf(IllegalArgumentException.class);
        assertThat(inbox.count()).isZero();
    }
    @Test void presencaInicioValidacoesEReferenciasNaoGeramBonus() throws Exception {
        var aluno = alunos.criar("Presenca B1", Plano.BASICO);
        var curso = cursos.criar("Presenca B1");
        for (String tipo : new String[]{"PRESENCA", "INICIO"})
            mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento(tipo, tipo, aluno.getId(), curso.getId(), ""))).andExpect(status().isOk());
        for (String body : new String[]{"{}", evento("", "PRESENCA", aluno.getId(), curso.getId(), ""), evento("n", "INVALIDO", aluno.getId(), curso.getId(), ""), evento("n", "CONCLUSAO", aluno.getId(), curso.getId(), ""), evento("n", "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":11"), evento("n", "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":-1"), evento("n", "PRESENCA", null, curso.getId(), ""), evento("n", "INICIO", aluno.getId(), null, ""), "{\"eventId\":\"n\",\"tipo\":\"PRESENCA\",\"alunoId\":1,\"cursoId\":1}"})
            mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(body)).andExpect(status().isBadRequest());
        for (String body : new String[]{evento("absent", "PRESENCA", 999999L, curso.getId(), ""), evento("absent", "INICIO", aluno.getId(), 999999L, "")})
            mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(body)).andExpect(status().isNotFound());
        assertThat(inbox.count()).isEqualTo(2);
        assertThat(outbox.count()).isZero();
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isZero();
    }
    @Test void rollbackReverteInboxHistoricoBonusEOutbox() {
        var aluno = alunos.criar("Rollback", Plano.BASICO);
        var curso = cursos.criar("Rollback");
        new org.springframework.transaction.support.TransactionTemplate(transactionManager).executeWithoutResult(tx -> {
            iot.receber(new IotService.Evento("rollback", "CONCLUSAO", "sensor", aluno.getId(), curso.getId(), 9.0));
            tx.setRollbackOnly();
        });
        assertThat(inbox.existsById("rollback")).isFalse();
        assertThat(outbox.count()).isZero();
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isZero();
    }
    @Test void retransmissaoConcorrenteConfirmaAmbasRequisicoesComUmaRecompensa() throws Exception {
        var aluno = alunos.criar("Concorrencia", Plano.BASICO);
        var curso = cursos.criar("Concorrencia");
        String evento = evento("concorrente", "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":8.5");
        var executor = Executors.newFixedThreadPool(2);
        var inicio = new java.util.concurrent.CountDownLatch(1);
        try {
            java.util.concurrent.Callable<Integer> request = () -> {
                inicio.await();
                return mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento)).andReturn().getResponse().getStatus();
            };
            var a = executor.submit(request);
            var b = executor.submit(request);
            inicio.countDown();
            assertThat(a.get()).isEqualTo(200);
            assertThat(b.get()).isEqualTo(200);
        } finally { executor.shutdownNow(); }
        assertThat(inbox.count()).isEqualTo(1);
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isEqualTo(3);
        assertThat(outbox.count()).isEqualTo(1);
    }
    @Test void eventoQueConsultouAusenciaAntesDeOutraConfirmacaoNaoRepeteEfeitos() throws Exception {
        var aluno = alunos.criar("Merge concorrente", Plano.BASICO);
        var curso = cursos.criar("Merge concorrente");
        String evento = evento("insercao-tardia", "CONCLUSAO", aluno.getId(), curso.getId(), ",\"nota\":8.5");
        var ausenciaConsultada = new java.util.concurrent.CountDownLatch(1);
        var liberarInsercao = new java.util.concurrent.CountDownLatch(1);
        doAnswer(invocation -> {
            boolean existe = inbox.findById("insercao-tardia").isPresent();
            if (Thread.currentThread().getName().equals("evento-atrasado") && Boolean.FALSE.equals(existe)) {
                assertThat(existe).isEqualTo(false);
                ausenciaConsultada.countDown();
                assertThat(liberarInsercao.await(10, java.util.concurrent.TimeUnit.SECONDS)).isTrue();
            }
            return existe;
        }).when(inbox).existsById("insercao-tardia");
        var executor = Executors.newSingleThreadExecutor(runnable -> new Thread(runnable, "evento-atrasado"));
        try {
            var atrasado = executor.submit(() -> mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento))
                    .andReturn().getResponse().getStatus());
            assertThat(ausenciaConsultada.await(10, java.util.concurrent.TimeUnit.SECONDS)).isTrue();
            mvc.perform(post("/api/iot/eventos").contentType(MediaType.APPLICATION_JSON).content(evento)).andExpect(status().isOk());
            liberarInsercao.countDown();
            assertThat(atrasado.get(10, java.util.concurrent.TimeUnit.SECONDS)).isEqualTo(200);
        } finally {
            liberarInsercao.countDown();
            executor.shutdownNow();
        }
        assertThat(alunos.buscarPorId(aluno.getId()).getCursosDisponiveis()).isEqualTo(3);
        assertThat(inbox.count()).isEqualTo(1);
        assertThat(outbox.count()).isEqualTo(1);
    }
    static String evento(String id, String tipo, Long aluno, Long curso, String nota) {
        return "{\"eventId\":\"" + id + "\",\"tipo\":\"" + tipo + "\",\"dispositivoId\":\"sensor-1\",\"alunoId\":" + aluno + ",\"cursoId\":" + curso + nota + "}";
    }
}
