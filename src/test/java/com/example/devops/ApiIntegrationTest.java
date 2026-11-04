package com.example.devops;

import com.example.devops.domain.Aluno;
import com.example.devops.domain.Plano;
import com.example.devops.repository.AlunoRepository;
import com.example.devops.curso.internal.persistence.CursoRepository;
import com.example.devops.service.AlunoService;
import com.jayway.jsonpath.JsonPath;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(useMainMethod = SpringBootTest.UseMainMethod.ALWAYS)
@AutoConfigureMockMvc
@ActiveProfiles("test")
class ApiIntegrationTest {

    @Autowired private MockMvc mvc;
    @Autowired private AlunoRepository alunoRepository;
    @Autowired private CursoRepository cursoRepository;
    @Autowired private AlunoService alunoService;

    @BeforeEach
    void limparBanco() {
        alunoRepository.deleteAll();
        cursoRepository.deleteAll();
    }

    @Test
    void deveListarAlunosECursosVazios() throws Exception {
        mvc.perform(get("/api/alunos")).andExpect(status().isOk()).andExpect(jsonPath("$").isEmpty());
        mvc.perform(get("/api/cursos")).andExpect(status().isOk()).andExpect(jsonPath("$").isEmpty());
    }

    @Test
    void deveCriarConsultarEListarAlunoComDadosNormalizados() throws Exception {
        long alunoId = idDaResposta(enviar("/api/alunos", """
                {"nome":"  Ana  ","plano":"BASICO"}
                """).andExpect(status().isCreated())
                .andExpect(jsonPath("$.nome").value("Ana"))
                .andExpect(jsonPath("$.plano").value("BASICO"))
                .andExpect(jsonPath("$.cursosDisponiveis").value(0))
                .andExpect(jsonPath("$.mediaGeral").value(0))
                .andExpect(jsonPath("$.historico").isEmpty()));

        mvc.perform(get("/api/alunos/{id}", alunoId)).andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(alunoId))
                .andExpect(jsonPath("$.nome").value("Ana"))
                .andExpect(jsonPath("$.historico").isEmpty());
        mvc.perform(get("/api/alunos")).andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].id").value(alunoId))
                .andExpect(jsonPath("$[0].nome").value("Ana"));
    }

    @Test
    void deveCriarEListarCursoComNomeNormalizado() throws Exception {
        long cursoId = idDaResposta(enviar("/api/cursos", """
                {"nome":"  Docker  "}
                """).andExpect(status().isCreated())
                .andExpect(jsonPath("$.nome").value("Docker")));

        mvc.perform(get("/api/cursos")).andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].id").value(cursoId))
                .andExpect(jsonPath("$[0].nome").value("Docker"));
    }

    @Test
    void devePersistirConclusaoERetornarHistoricoEBonusNasConsultas() throws Exception {
        long alunoId = criarAluno();
        long cursoId = criarCurso();

        enviar("/api/alunos/" + alunoId + "/concluir-curso",
                "{\"cursoId\":" + cursoId + ",\"nota\":8.5}")
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(alunoId))
                .andExpect(jsonPath("$.cursosDisponiveis").value(3))
                .andExpect(jsonPath("$.mediaGeral").value(8))
                .andExpect(jsonPath("$.historico.Java").value(8.5));

        mvc.perform(get("/api/alunos/{id}", alunoId)).andExpect(status().isOk())
                .andExpect(jsonPath("$.historico.Java").value(8.5))
                .andExpect(jsonPath("$.cursosDisponiveis").value(3));
        mvc.perform(get("/api/alunos")).andExpect(status().isOk())
                .andExpect(jsonPath("$[0].historico.Java").value(8.5));
    }

    @Test
    void deveListarCadaAlunoUmaVezComHistoricoCompleto() throws Exception {
        long alunoId = criarAluno();
        long outroAlunoId = idDaResposta(enviar("/api/alunos", "{\"nome\":\"Bia\",\"plano\":\"PREMIUM\"}")
                .andExpect(status().isCreated()));
        long javaId = criarCurso();
        long dockerId = idDaResposta(enviar("/api/cursos", "{\"nome\":\"Docker\"}")
                .andExpect(status().isCreated()));
        enviar("/api/alunos/" + alunoId + "/concluir-curso", "{\"cursoId\":" + javaId + ",\"nota\":9}")
                .andExpect(status().isOk());
        enviar("/api/alunos/" + alunoId + "/concluir-curso", "{\"cursoId\":" + dockerId + ",\"nota\":4}")
                .andExpect(status().isOk());

        mvc.perform(get("/api/alunos")).andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[?(@.id == " + alunoId + ")].historico.Java").value(9.0))
                .andExpect(jsonPath("$[?(@.id == " + alunoId + ")].historico.Docker").value(4.0))
                .andExpect(jsonPath("$[?(@.id == " + alunoId + ")].mediaGeral").value(6))
                .andExpect(jsonPath("$[?(@.id == " + outroAlunoId + ")].nome").value("Bia"));
    }

    @ParameterizedTest
    @ValueSource(strings = {"{}", "{\"nome\":\" \"}", "{\"nome\":\"Ana\"}"})
    void deveRetornar400AoCriarAlunoInvalido(String json) throws Exception {
        enviar("/api/alunos", json).andExpect(status().isBadRequest()).andExpect(jsonPath("$.erro").isNotEmpty());
        assertThat(alunoRepository.count()).isZero();
    }

    @ParameterizedTest
    @ValueSource(strings = {"{}", "{\"nome\":\" \"}"})
    void deveRetornar400AoCriarCursoInvalido(String json) throws Exception {
        enviar("/api/cursos", json).andExpect(status().isBadRequest()).andExpect(jsonPath("$.erro").isNotEmpty());
        assertThat(cursoRepository.count()).isZero();
    }

    @Test
    void deveRetornar404AoConsultarAlunoInexistente() throws Exception {
        mvc.perform(get("/api/alunos/{id}", Long.MAX_VALUE)).andExpect(status().isNotFound())
                .andExpect(jsonPath("$.erro").value("Aluno não encontrado"));
    }

    @Test
    void deveRetornar404AoConcluirCursoDeAlunoInexistente() throws Exception {
        long cursoId = criarCurso();
        enviar("/api/alunos/" + Long.MAX_VALUE + "/concluir-curso",
                "{\"cursoId\":" + cursoId + ",\"nota\":9}")
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.erro").value("Aluno não encontrado"));
    }

    @Test
    void deveRetornar404AoConcluirCursoInexistente() throws Exception {
        long alunoId = criarAluno();
        enviar("/api/alunos/" + alunoId + "/concluir-curso",
                "{\"cursoId\":" + Long.MAX_VALUE + ",\"nota\":9}")
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.erro").value("Curso não encontrado"));
    }

    @Test
    void deveRetornar400AoConcluirSemIdDoCurso() throws Exception {
        long alunoId = criarAluno();
        enviar("/api/alunos/" + alunoId + "/concluir-curso", "{\"nota\":9}")
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.erro").value("O id do curso é obrigatório"));
    }

    @Test
    void deveRejeitarConclusaoNulaSemAlterarAlunoPersistido() {
        Aluno aluno = alunoService.criar("Ana", Plano.BASICO);

        assertThatThrownBy(() -> alunoService.processarConclusao(aluno.getId(), null))
                .isInstanceOf(IllegalArgumentException.class);
        assertThat(alunoService.buscarPorId(aluno.getId()).getCursosDisponiveis()).isZero();
    }

    @ParameterizedTest
    @ValueSource(doubles = {-1, 11})
    void deveRetornar400ParaNotaInvalidaSemConcederBonus(double nota) throws Exception {
        long alunoId = criarAluno();
        long cursoId = criarCurso();
        enviar("/api/alunos/" + alunoId + "/concluir-curso",
                "{\"cursoId\":" + cursoId + ",\"nota\":" + nota + "}")
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.erro").value("A nota deve estar entre 0 e 10"));
        mvc.perform(get("/api/alunos/{id}", alunoId)).andExpect(status().isOk())
                .andExpect(jsonPath("$.cursosDisponiveis").value(0))
                .andExpect(jsonPath("$.historico").isEmpty());
    }

    private long criarAluno() throws Exception {
        return idDaResposta(enviar("/api/alunos", "{\"nome\":\"Ana\",\"plano\":\"BASICO\"}")
                .andExpect(status().isCreated()));
    }

    private long criarCurso() throws Exception {
        return idDaResposta(enviar("/api/cursos", "{\"nome\":\"Java\"}").andExpect(status().isCreated()));
    }

    private ResultActions enviar(String url, String json) throws Exception {
        return mvc.perform(post(url).contentType(MediaType.APPLICATION_JSON).content(json));
    }

    private long idDaResposta(ResultActions resposta) throws Exception {
        Number id = JsonPath.read(resposta.andReturn().getResponse().getContentAsString(), "$.id");
        return id.longValue();
    }
}
