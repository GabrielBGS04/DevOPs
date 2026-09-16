package com.example.devops.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    OpenAPI devopsOpenApi() {
        return new OpenAPI().info(new Info()
                .title("API DEVOPS - Educação Continuada")
                .version("1.0.0")
                .description("API para alunos, cursos e conclusão de cursos."));
    }
}
