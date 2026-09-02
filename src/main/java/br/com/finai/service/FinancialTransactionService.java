package br.com.finai.service;

import br.com.finai.domain.entity.Account;
import br.com.finai.domain.entity.Category;
import br.com.finai.domain.entity.FinancialTransaction;
import br.com.finai.domain.entity.User;
import br.com.finai.domain.enums.TransactionStatus;
import br.com.finai.domain.enums.TransactionType;
import br.com.finai.dto.transaction.TransactionRequest;
import br.com.finai.dto.transaction.TransactionResponse;
import br.com.finai.exception.BusinessRuleException;
import br.com.finai.exception.ResourceNotFoundException;
import br.com.finai.repository.FinancialTransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

@Service
public class FinancialTransactionService {

    private final FinancialTransactionRepository repository;
    private final UserService userService;
    private final CategoryService categoryService;
    private final AccountService accountService;

    public FinancialTransactionService(FinancialTransactionRepository repository,
                                       UserService userService,
                                       CategoryService categoryService,
                                       AccountService accountService) {
        this.repository = repository;
        this.userService = userService;
        this.categoryService = categoryService;
        this.accountService = accountService;
    }

    @Transactional(readOnly = true)
    public List<TransactionResponse> findAll(UUID userId, LocalDate startDate, LocalDate endDate) {
        userService.findEntity(userId);
        if (startDate.isAfter(endDate)) {
            throw new BusinessRuleException("A data inicial não pode ser posterior à data final");
        }
        return repository.findAllByUserIdAndDateBetweenOrderByDateDesc(userId, startDate, endDate)
                .stream().map(TransactionResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public TransactionResponse findById(UUID id) { return TransactionResponse.from(findEntity(id)); }

    @Transactional
    public TransactionResponse create(TransactionRequest request) {
        User user = userService.findEntity(request.userId());
        Category category = categoryService.findEntity(request.categoryId());
        Account account = accountService.findEntity(request.accountId());
        validateRelationships(request, category, account);

        FinancialTransaction transaction = new FinancialTransaction(
                request.description().trim(), request.amount(), request.date(), request.type(),
                request.status(), category, account, user);
        applyBalance(transaction);
        return TransactionResponse.from(repository.save(transaction));
    }

    @Transactional
    public TransactionResponse update(UUID id, TransactionRequest request) {
        FinancialTransaction transaction = findEntity(id);
        if (!transaction.getUser().getId().equals(request.userId())) {
            throw new BusinessRuleException("Não é permitido transferir uma transação para outro usuário");
        }

        reverseBalance(transaction);
        Category category = categoryService.findEntity(request.categoryId());
        Account account = accountService.findEntity(request.accountId());
        validateRelationships(request, category, account);

        transaction.setDescription(request.description().trim());
        transaction.setAmount(request.amount());
        transaction.setDate(request.date());
        transaction.setType(request.type());
        transaction.setStatus(request.status());
        transaction.setCategory(category);
        transaction.setAccount(account);
        applyBalance(transaction);
        return TransactionResponse.from(transaction);
    }

    @Transactional
    public void delete(UUID id) {
        FinancialTransaction transaction = findEntity(id);
        reverseBalance(transaction);
        repository.delete(transaction);
    }

    @Transactional(readOnly = true)
    public FinancialTransaction findEntity(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Transação não encontrada"));
    }

    private void validateRelationships(TransactionRequest request, Category category, Account account) {
        if (!category.getUser().getId().equals(request.userId())
                || !account.getUser().getId().equals(request.userId())) {
            throw new BusinessRuleException("Conta, categoria e transação devem pertencer ao mesmo usuário");
        }
        if (category.getType() != request.type()) {
            throw new BusinessRuleException("O tipo da transação deve ser igual ao tipo da categoria");
        }
    }

    private void applyBalance(FinancialTransaction transaction) {
        if (transaction.getStatus() != TransactionStatus.COMPLETED) return;
        moveBalance(transaction.getAccount(), transaction.getType(), transaction.getAmount(), false);
    }

    private void reverseBalance(FinancialTransaction transaction) {
        if (transaction.getStatus() != TransactionStatus.COMPLETED) return;
        moveBalance(transaction.getAccount(), transaction.getType(), transaction.getAmount(), true);
    }

    private void moveBalance(Account account, TransactionType type, BigDecimal amount, boolean reverse) {
        boolean credit = type == TransactionType.INCOME;
        if (reverse) credit = !credit;
        if (credit) account.credit(amount); else account.debit(amount);
    }
}
