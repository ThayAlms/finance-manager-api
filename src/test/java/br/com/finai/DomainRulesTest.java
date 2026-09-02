package br.com.finai;

import br.com.finai.domain.entity.Account;
import br.com.finai.domain.entity.Goal;
import br.com.finai.domain.entity.User;
import br.com.finai.domain.enums.AccountType;
import br.com.finai.dto.goal.GoalResponse;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;

class DomainRulesTest {

    @Test
    void shouldCreditAndDebitAccountBalance() {
        User user = new User("Maria", "maria@email.com", "hash");
        Account account = new Account("Principal", AccountType.CHECKING,
                new BigDecimal("1000.00"), user);

        account.credit(new BigDecimal("250.00"));
        account.debit(new BigDecimal("100.00"));

        assertThat(account.getBalance()).isEqualByComparingTo("1150.00");
    }

    @Test
    void shouldCalculateGoalProgressAndRemainingAmount() {
        User user = new User("Maria", "maria@email.com", "hash");
        Goal goal = new Goal("Reserva", new BigDecimal("10000.00"),
                new BigDecimal("2500.00"), LocalDate.now().plusYears(1), user);

        GoalResponse response = GoalResponse.from(goal);

        assertThat(response.progressPercentage()).isEqualByComparingTo("25.00");
        assertThat(response.remainingAmount()).isEqualByComparingTo("7500.00");
    }
}
