package br.com.finai.dto.account;

import br.com.finai.domain.enums.AccountType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.util.UUID;

public record AccountRequest(
        @NotBlank @Size(max = 80)
        @Schema(example = "Conta principal") String name,

        @NotNull @Schema(example = "CHECKING") AccountType type,

        @NotNull @DecimalMin(value = "0.00", inclusive = true)
        @Schema(example = "1500.00") BigDecimal initialBalance,

        @NotNull @Schema(example = "c18d9c5f-0634-4af7-8ec5-b705c7305015") UUID userId
) {
}
