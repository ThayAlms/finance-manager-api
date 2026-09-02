package br.com.finai.dto.goal;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

public record GoalRequest(
        @NotBlank @Size(max = 100)
        @Schema(example = "Reserva de emergência") String name,

        @NotNull @DecimalMin(value = "0.01")
        @Schema(example = "10000.00") BigDecimal targetAmount,

        @NotNull @DecimalMin(value = "0.00")
        @Schema(example = "2500.00") BigDecimal currentAmount,

        @Schema(example = "2027-12-31") LocalDate deadline,

        @NotNull UUID userId
) {
}
