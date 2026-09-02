package br.com.finai.repository;

import br.com.finai.domain.entity.Category;
import br.com.finai.domain.enums.TransactionType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface CategoryRepository extends JpaRepository<Category, UUID> {
    List<Category> findAllByUserIdOrderByName(UUID userId);
    boolean existsByNameIgnoreCaseAndTypeAndUserId(String name, TransactionType type, UUID userId);
    boolean existsByNameIgnoreCaseAndTypeAndUserIdAndIdNot(
            String name, TransactionType type, UUID userId, UUID id);
    boolean existsByUserId(UUID userId);
}
