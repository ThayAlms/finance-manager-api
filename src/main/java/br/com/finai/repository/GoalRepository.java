package br.com.finai.repository;

import br.com.finai.domain.entity.Goal;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.UUID;

public interface GoalRepository extends JpaRepository<Goal, UUID> {
    List<Goal> findAllByUserIdOrderByDeadlineAsc(UUID userId);
    boolean existsByUserId(UUID userId);
}
