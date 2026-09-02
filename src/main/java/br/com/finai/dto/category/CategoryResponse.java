package br.com.finai.dto.category;

import br.com.finai.domain.entity.Category;
import br.com.finai.domain.enums.TransactionType;

import java.util.UUID;

public record CategoryResponse(UUID id, String name, TransactionType type, UUID userId) {
    public static CategoryResponse from(Category category) {
        return new CategoryResponse(category.getId(), category.getName(), category.getType(),
                category.getUser().getId());
    }
}
