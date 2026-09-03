package br.com.finai.controller;

import br.com.finai.config.StandardApiResponses;
import br.com.finai.dto.transaction.TransactionRequest;
import br.com.finai.dto.transaction.TransactionResponse;
import br.com.finai.service.FinancialTransactionService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.net.URI;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/transactions")
@Tag(name = "Transações", description = "Receitas e despesas com atualização automática do saldo")
@StandardApiResponses
public class FinancialTransactionController {

    private final FinancialTransactionService service;

    public FinancialTransactionController(FinancialTransactionService service) { this.service = service; }

    @GetMapping
    @Operation(summary = "Listar transações do usuário por período")
    public List<TransactionResponse> findAll(
            @RequestParam UUID userId,
            @RequestParam(defaultValue = "1900-01-01") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate startDate,
            @RequestParam(defaultValue = "2999-12-31") @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate endDate) {
        return service.findAll(userId, startDate, endDate);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar transação por ID")
    public TransactionResponse findById(@PathVariable UUID id) { return service.findById(id); }

    @PostMapping
    @Operation(summary = "Criar transação")
    @ApiResponses({@ApiResponse(responseCode = "201", description = "Transação criada"),
            @ApiResponse(responseCode = "400", description = "Dados inválidos"),
            @ApiResponse(responseCode = "409", description = "Regra de negócio violada")})
    public ResponseEntity<TransactionResponse> create(@Valid @RequestBody TransactionRequest request) {
        TransactionResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/v1/transactions/" + response.id())).body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar transação e recalcular o saldo")
    public TransactionResponse update(@PathVariable UUID id,
                                      @Valid @RequestBody TransactionRequest request) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir transação e desfazer seu efeito no saldo")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
