package br.com.finai.controller;

import br.com.finai.config.StandardApiResponses;
import br.com.finai.dto.goal.GoalRequest;
import br.com.finai.dto.goal.GoalResponse;
import br.com.finai.service.GoalService;
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
@RequestMapping("/api/v1/goals")
@Tag(name = "Metas", description = "Metas de economia e acompanhamento do progresso")
@StandardApiResponses
public class GoalController {

    private final GoalService service;

    public GoalController(GoalService service) { this.service = service; }

    @GetMapping
    @Operation(summary = "Listar metas do usuário")
    public List<GoalResponse> findAll(@RequestParam UUID userId) {
        return service.findAllByUser(userId);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar meta por ID")
    public GoalResponse findById(@PathVariable UUID id) { return service.findById(id); }

    @PostMapping
    @Operation(summary = "Criar meta financeira")
    @ApiResponses({@ApiResponse(responseCode = "201", description = "Meta criada"),
            @ApiResponse(responseCode = "400", description = "Dados inválidos"),
            @ApiResponse(responseCode = "409", description = "Regra de negócio violada")})
    public ResponseEntity<GoalResponse> create(@Valid @RequestBody GoalRequest request) {
        GoalResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/v1/goals/" + response.id())).body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar meta e seu progresso")
    public GoalResponse update(@PathVariable UUID id, @Valid @RequestBody GoalRequest request) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir meta")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
