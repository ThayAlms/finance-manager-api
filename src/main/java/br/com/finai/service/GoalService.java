package br.com.finai.service;

import br.com.finai.domain.entity.Goal;
import br.com.finai.domain.entity.User;
import br.com.finai.dto.goal.GoalRequest;
import br.com.finai.dto.goal.GoalResponse;
import br.com.finai.exception.BusinessRuleException;
import br.com.finai.exception.ResourceNotFoundException;
import br.com.finai.repository.GoalRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Service
public class GoalService {

    private final GoalRepository repository;
    private final UserService userService;

    public GoalService(GoalRepository repository, UserService userService) {
        this.repository = repository;
        this.userService = userService;
    }

    @Transactional(readOnly = true)
    public List<GoalResponse> findAllByUser(UUID userId) {
        userService.findEntity(userId);
        return repository.findAllByUserIdOrderByDeadlineAsc(userId).stream().map(GoalResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public GoalResponse findById(UUID id) { return GoalResponse.from(findEntity(id)); }

    @Transactional
    public GoalResponse create(GoalRequest request) {
        User user = userService.findEntity(request.userId());
        validate(request);
        Goal goal = new Goal(request.name().trim(), request.targetAmount(), request.currentAmount(),
                request.deadline(), user);
        return GoalResponse.from(repository.save(goal));
    }

    @Transactional
    public GoalResponse update(UUID id, GoalRequest request) {
        Goal goal = findEntity(id);
        if (!goal.getUser().getId().equals(request.userId())) {
            throw new BusinessRuleException("Não é permitido transferir uma meta para outro usuário");
        }
        validate(request);
        goal.setName(request.name().trim());
        goal.setTargetAmount(request.targetAmount());
        goal.setCurrentAmount(request.currentAmount());
        goal.setDeadline(request.deadline());
        return GoalResponse.from(goal);
    }

    @Transactional
    public void delete(UUID id) { repository.delete(findEntity(id)); }

    @Transactional(readOnly = true)
    public Goal findEntity(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Meta não encontrada"));
    }

    private void validate(GoalRequest request) {
        if (request.currentAmount().compareTo(request.targetAmount()) > 0) {
            throw new BusinessRuleException("O valor atual não pode ser maior que o valor da meta");
        }
        if (request.deadline() != null && request.deadline().isBefore(LocalDate.now())) {
            throw new BusinessRuleException("O prazo da meta não pode estar no passado");
        }
    }
}
