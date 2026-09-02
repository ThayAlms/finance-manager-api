package br.com.finai.dto.user;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record UserRequest(
        @NotBlank @Size(max = 120)
        @Schema(example = "Maria Silva") String name,

        @NotBlank @Email @Size(max = 180)
        @Schema(example = "maria@email.com") String email,

        @NotBlank @Size(min = 8, max = 72)
        @Schema(example = "Senha@123", accessMode = Schema.AccessMode.WRITE_ONLY) String password
) {
}
