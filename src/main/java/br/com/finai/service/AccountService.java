package br.com.finai.service;

import br.com.finai.domain.entity.Account;
import br.com.finai.domain.entity.User;
import br.com.finai.dto.account.AccountRequest;
import br.com.finai.dto.account.AccountResponse;
import br.com.finai.dto.account.AccountUpdateRequest;
import br.com.finai.exception.BusinessRuleException;
import br.com.finai.exception.ResourceNotFoundException;
import br.com.finai.repository.AccountRepository;
import br.com.finai.repository.FinancialTransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class AccountService {

    private final AccountRepository repository;
    private final FinancialTransactionRepository transactionRepository;
    private final UserService userService;

    public AccountService(AccountRepository repository,
                          FinancialTransactionRepository transactionRepository,
                          UserService userService) {
        this.repository = repository;
        this.transactionRepository = transactionRepository;
        this.userService = userService;
    }

    @Transactional(readOnly = true)
    public List<AccountResponse> findAllByUser(UUID userId) {
        userService.findEntity(userId);
        return repository.findAllByUserIdOrderByName(userId).stream().map(AccountResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public AccountResponse findById(UUID id) { return AccountResponse.from(findEntity(id)); }

    @Transactional
    public AccountResponse create(AccountRequest request) {
        User user = userService.findEntity(request.userId());
        if (repository.existsByNameIgnoreCaseAndUserId(request.name().trim(), request.userId())) {
            throw new BusinessRuleException("Já existe uma conta com este nome para o usuário");
        }
        Account account = new Account(request.name().trim(), request.type(),
                request.initialBalance(), user);
        return AccountResponse.from(repository.save(account));
    }

    @Transactional
    public AccountResponse update(UUID id, AccountUpdateRequest request) {
        Account account = findEntity(id);
        if (repository.existsByNameIgnoreCaseAndUserIdAndIdNot(
                request.name().trim(), account.getUser().getId(), id)) {
            throw new BusinessRuleException("Já existe uma conta com este nome para o usuário");
        }
        account.setName(request.name().trim());
        account.setType(request.type());
        return AccountResponse.from(account);
    }

    @Transactional
    public void delete(UUID id) {
        Account account = findEntity(id);
        if (transactionRepository.existsByAccountId(id)) {
            throw new BusinessRuleException("A conta possui transações e não pode ser excluída");
        }
        repository.delete(account);
    }

    @Transactional(readOnly = true)
    public Account findEntity(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Conta não encontrada"));
    }
}
