package br.com.finai.dto.account;

import br.com.finai.domain.entity.Account;
import br.com.finai.domain.enums.AccountType;

import java.math.BigDecimal;
import java.util.UUID;

public record AccountResponse(UUID id, String name, AccountType type, BigDecimal balance, UUID userId) {
    public static AccountResponse from(Account account) {
        return new AccountResponse(account.getId(), account.getName(), account.getType(),
                account.getBalance(), account.getUser().getId());
    }
}
