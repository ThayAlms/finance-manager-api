package br.com.finai.dto.transaction;

import br.com.finai.domain.enums.TransactionStatus;
import br.com.finai.domain.enums.TransactionType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record TransactionRequest(
        @NotBlank @Size(max = 160)
        @Schema(example = "Compra no supermercado") String description,

        @NotNull @DecimalMin(value = "0.01")
        @Schema(example = "250.90") BigDecimal amount,

        @NotNull @Schema(example = "2026-09-02") LocalDate date,

        @NotNull @Schema(example = "EXPENSE") TransactionType type,

        @NotNull @Schema(example = "COMPLETED") TransactionStatus status,

        @NotNull UUID categoryId,
        @NotNull UUID accountId,
        @NotNull UUID userId
) {
}
