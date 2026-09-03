package br.com.finai.controller;

import br.com.finai.config.StandardApiResponses;
import br.com.finai.dto.account.AccountRequest;
import br.com.finai.dto.account.AccountResponse;
import br.com.finai.dto.account.AccountUpdateRequest;
import br.com.finai.service.AccountService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
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
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/accounts")
@Tag(name = "Contas", description = "Contas bancárias, carteiras e saldos")
@StandardApiResponses
public class AccountController {

    private final AccountService service;

    public AccountController(AccountService service) { this.service = service; }

    @GetMapping
    @Operation(summary = "Listar contas do usuário")
    public List<AccountResponse> findAll(@RequestParam UUID userId) {
        return service.findAllByUser(userId);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar conta por ID")
    public AccountResponse findById(@PathVariable UUID id) { return service.findById(id); }

    @PostMapping
    @Operation(summary = "Criar conta")
    @ApiResponses({@ApiResponse(responseCode = "201", description = "Conta criada"),
            @ApiResponse(responseCode = "400", description = "Dados inválidos"),
            @ApiResponse(responseCode = "409", description = "Conta duplicada")})
    public ResponseEntity<AccountResponse> create(@Valid @RequestBody AccountRequest request) {
        AccountResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/v1/accounts/" + response.id())).body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar nome e tipo da conta; o saldo é controlado pelas transações")
    public AccountResponse update(@PathVariable UUID id,
                                  @Valid @RequestBody AccountUpdateRequest request) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir conta sem transações vinculadas")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
