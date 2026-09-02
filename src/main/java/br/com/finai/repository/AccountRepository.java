package br.com.finai.repository;

import br.com.finai.domain.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface AccountRepository extends JpaRepository<Account, UUID> {
    List<Account> findAllByUserIdOrderByName(UUID userId);
    boolean existsByNameIgnoreCaseAndUserId(String name, UUID userId);
    boolean existsByNameIgnoreCaseAndUserIdAndIdNot(String name, UUID userId, UUID id);
    boolean existsByUserId(UUID userId);
}
