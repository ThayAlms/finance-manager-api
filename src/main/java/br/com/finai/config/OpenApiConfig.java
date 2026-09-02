package br.com.finai.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    OpenAPI finAiOpenApi() {
        return new OpenAPI().info(new Info()
                .title("FinAI Finance Manager API")
                .description("API REST para gestão financeira pessoal — FIAP CP1")
                .version("v1")
                .contact(new Contact().name("Equipe FinAI"))
                .license(new License().name("Uso acadêmico")));
    }
}
