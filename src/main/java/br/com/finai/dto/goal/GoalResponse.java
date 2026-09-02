package br.com.finai.dto.goal;

import br.com.finai.domain.entity.Goal;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.UUID;

public record GoalResponse(
        UUID id,
        String name,
        BigDecimal targetAmount,
        BigDecimal currentAmount,
        BigDecimal remainingAmount,
        BigDecimal progressPercentage,
        LocalDate deadline,
        UUID userId
) {
    public static GoalResponse from(Goal goal) {
        BigDecimal remaining = goal.getTargetAmount().subtract(goal.getCurrentAmount()).max(BigDecimal.ZERO);
        BigDecimal progress = goal.getCurrentAmount()
                .multiply(BigDecimal.valueOf(100))
                .divide(goal.getTargetAmount(), 2, RoundingMode.HALF_UP)
                .min(BigDecimal.valueOf(100));

        return new GoalResponse(goal.getId(), goal.getName(), goal.getTargetAmount(),
                goal.getCurrentAmount(), remaining, progress, goal.getDeadline(), goal.getUser().getId());
    }
}
