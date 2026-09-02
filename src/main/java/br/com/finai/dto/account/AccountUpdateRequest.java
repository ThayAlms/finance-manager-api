package br.com.finai.dto.account;

import br.com.finai.domain.enums.AccountType;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public record AccountUpdateRequest(
        @NotBlank @Size(max = 80)
        @Schema(example = "Conta principal") String name,

        @NotNull @Schema(example = "CHECKING") AccountType type
) {
}
