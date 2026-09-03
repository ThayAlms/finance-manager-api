package br.com.finai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class FinanceManagerApiIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void shouldExecuteFinancialWorkflowAndRecalculateBalance() throws Exception {
        UUID userId = idFrom(postJson("/api/v1/users", """
                {
                  "name": "Maria Silva",
                  "email": "MARIA@EMAIL.COM",
                  "password": "Senha@123"
                }
                """, 201));

        UUID categoryId = idFrom(postJson("/api/v1/categories", """
                {
                  "name": "Salário",
                  "type": "INCOME",
                  "userId": "%s"
                }
                """.formatted(userId), 201));

        UUID accountId = idFrom(postJson("/api/v1/accounts", """
                {
                  "name": "Conta principal",
                  "type": "CHECKING",
                  "initialBalance": 1000.00,
                  "userId": "%s"
                }
                """.formatted(userId), 201));

        UUID transactionId = idFrom(postJson("/api/v1/transactions", """
                {
                  "description": "Salário mensal",
                  "amount": 2500.00,
                  "date": "2026-09-03",
                  "type": "INCOME",
                  "status": "COMPLETED",
                  "categoryId": "%s",
                  "accountId": "%s",
                  "userId": "%s"
                }
                """.formatted(categoryId, accountId, userId), 201));

        mockMvc.perform(get("/api/v1/accounts/{id}", accountId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.balance").value(3500.0));

        mockMvc.perform(put("/api/v1/transactions/{id}", transactionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {
                                  "description": "Salário cancelado",
                                  "amount": 2500.00,
                                  "date": "2026-09-03",
                                  "type": "INCOME",
                                  "status": "CANCELLED",
                                  "categoryId": "%s",
                                  "accountId": "%s",
                                  "userId": "%s"
                                }
                                """.formatted(categoryId, accountId, userId)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("CANCELLED"));

        mockMvc.perform(get("/api/v1/accounts/{id}", accountId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.balance").value(1000.0));

        mockMvc.perform(delete("/api/v1/accounts/{id}", accountId))
                .andExpect(status().isConflict())
                .andExpect(jsonPath("$.message").value("A conta possui transações e não pode ser excluída"));
    }

    @Test
    void shouldReturnStandardValidationAndBusinessErrors() throws Exception {
        postJson("/api/v1/users", """
                {
                  "name": "Maria Silva",
                  "email": "email-invalido",
                  "password": "123"
                }
                """, 400)
                .andExpect(jsonPath("$.message").value("Existem campos inválidos na requisição"))
                .andExpect(jsonPath("$.fieldErrors.email").exists())
                .andExpect(jsonPath("$.fieldErrors.password").exists());

        postJson("/api/v1/users", """
                {
                  "name": "Maria Silva",
                  "email": "maria@email.com",
                  "password": "Senha@123"
                }
                """, 201);

        postJson("/api/v1/users", """
                {
                  "name": "Outra Maria",
                  "email": "maria@email.com",
                  "password": "OutraSenha@123"
                }
                """, 409)
                .andExpect(jsonPath("$.message").value("Já existe um usuário cadastrado com este e-mail"));
    }

    @Test
    void shouldPublishOpenApiContract() throws Exception {
        String response = mockMvc.perform(get("/v3/api-docs"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.info.title").value("FinAI Finance Manager API"))
                .andExpect(jsonPath("$.paths['/api/v1/users']").exists())
                .andExpect(jsonPath("$.paths['/api/v1/transactions']").exists())
                .andReturn().getResponse().getContentAsString();

        assertThat(objectMapper.readTree(response).path("openapi").asText()).startsWith("3.");
    }

    private org.springframework.test.web.servlet.ResultActions postJson(
            String path, String body, int expectedStatus) throws Exception {
        return mockMvc.perform(post(path)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(body))
                .andExpect(status().is(expectedStatus));
    }

    private UUID idFrom(org.springframework.test.web.servlet.ResultActions result) throws Exception {
        JsonNode response = objectMapper.readTree(result.andReturn().getResponse().getContentAsString());
        return UUID.fromString(response.path("id").asText());
    }
}
