package br.com.finai.controller;

import br.com.finai.dto.category.CategoryRequest;
import br.com.finai.dto.category.CategoryResponse;
import br.com.finai.service.CategoryService;
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
@RequestMapping("/api/v1/categories")
@Tag(name = "Categorias", description = "Categorias personalizadas de receitas e despesas")
public class CategoryController {

    private final CategoryService service;

    public CategoryController(CategoryService service) { this.service = service; }

    @GetMapping
    @Operation(summary = "Listar categorias do usuário")
    public List<CategoryResponse> findAll(@RequestParam UUID userId) {
        return service.findAllByUser(userId);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar categoria por ID")
    public CategoryResponse findById(@PathVariable UUID id) { return service.findById(id); }

    @PostMapping
    @Operation(summary = "Criar categoria")
    @ApiResponses({@ApiResponse(responseCode = "201", description = "Categoria criada"),
            @ApiResponse(responseCode = "400", description = "Dados inválidos"),
            @ApiResponse(responseCode = "409", description = "Categoria duplicada")})
    public ResponseEntity<CategoryResponse> create(@Valid @RequestBody CategoryRequest request) {
        CategoryResponse response = service.create(request);
        return ResponseEntity.created(URI.create("/api/v1/categories/" + response.id())).body(response);
    }

    @PutMapping("/{id}")
    @Operation(summary = "Atualizar categoria")
    public CategoryResponse update(@PathVariable UUID id, @Valid @RequestBody CategoryRequest request) {
        return service.update(id, request);
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Excluir categoria sem transações vinculadas")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        service.delete(id);
        return ResponseEntity.noContent().build();
    }
}
