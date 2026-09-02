package br.com.finai.dto.user;

import br.com.finai.domain.entity.User;

import java.time.OffsetDateTime;
import java.util.UUID;

public record UserResponse(UUID id, String name, String email, OffsetDateTime createdAt) {
    public static UserResponse from(User user) {
        return new UserResponse(user.getId(), user.getName(), user.getEmail(), user.getCreatedAt());
    }
}
