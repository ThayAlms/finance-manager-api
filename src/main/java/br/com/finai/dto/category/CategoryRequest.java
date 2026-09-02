package br.com.finai.dto.category;

import br.com.finai.domain.enums.TransactionType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.util.UUID;

public record CategoryRequest(
        @NotBlank @Size(max = 80)
        @Schema(example = "Alimentação") String name,

        @NotNull @Schema(example = "EXPENSE") TransactionType type,

        @NotNull @Schema(example = "c18d9c5f-0634-4af7-8ec5-b705c7305015") UUID userId
) {
}
