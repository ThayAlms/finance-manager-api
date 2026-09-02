package br.com.finai.dto.transaction;

import br.com.finai.domain.entity.FinancialTransaction;
import br.com.finai.domain.enums.TransactionStatus;
import br.com.finai.domain.enums.TransactionType;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.UUID;

public record TransactionResponse(
        UUID id,
        String description,
        BigDecimal amount,
        LocalDate date,
        TransactionType type,
        TransactionStatus status,
        UUID categoryId,
        String categoryName,
        UUID accountId,
        String accountName,
        UUID userId,
        OffsetDateTime createdAt
) {
    public static TransactionResponse from(FinancialTransaction transaction) {
        return new TransactionResponse(
                transaction.getId(), transaction.getDescription(), transaction.getAmount(),
                transaction.getDate(), transaction.getType(), transaction.getStatus(),
                transaction.getCategory().getId(), transaction.getCategory().getName(),
                transaction.getAccount().getId(), transaction.getAccount().getName(),
                transaction.getUser().getId(), transaction.getCreatedAt());
    }
}
