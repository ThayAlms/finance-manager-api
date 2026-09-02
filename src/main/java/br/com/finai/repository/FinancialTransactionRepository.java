package br.com.finai.repository;

import br.com.finai.domain.entity.FinancialTransaction;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

public interface FinancialTransactionRepository extends JpaRepository<FinancialTransaction, UUID> {
    List<FinancialTransaction> findAllByUserIdAndDateBetweenOrderByDateDesc(
            UUID userId, LocalDate startDate, LocalDate endDate);
    boolean existsByCategoryId(UUID categoryId);
    boolean existsByAccountId(UUID accountId);
    boolean existsByUserId(UUID userId);
}
