package br.com.finai.service;

import br.com.finai.domain.entity.User;
import br.com.finai.dto.user.UserRequest;
import br.com.finai.dto.user.UserResponse;
import br.com.finai.exception.BusinessRuleException;
import br.com.finai.exception.ResourceNotFoundException;
import br.com.finai.repository.AccountRepository;
import br.com.finai.repository.CategoryRepository;
import br.com.finai.repository.FinancialTransactionRepository;
import br.com.finai.repository.GoalRepository;
import br.com.finai.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class UserService {

    private final UserRepository repository;
    private final CategoryRepository categoryRepository;
    private final AccountRepository accountRepository;
    private final FinancialTransactionRepository transactionRepository;
    private final GoalRepository goalRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository repository, CategoryRepository categoryRepository,
                       AccountRepository accountRepository, FinancialTransactionRepository transactionRepository,
                       GoalRepository goalRepository, PasswordEncoder passwordEncoder) {
        this.repository = repository;
        this.categoryRepository = categoryRepository;
        this.accountRepository = accountRepository;
        this.transactionRepository = transactionRepository;
        this.goalRepository = goalRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Transactional(readOnly = true)
    public List<UserResponse> findAll() {
        return repository.findAll().stream().map(UserResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public UserResponse findById(UUID id) {
        return UserResponse.from(findEntity(id));
    }

    @Transactional
    public UserResponse create(UserRequest request) {
        String email = normalizeEmail(request.email());
        if (repository.existsByEmailIgnoreCase(email)) {
            throw new BusinessRuleException("Já existe um usuário cadastrado com este e-mail");
        }
        User user = new User(request.name().trim(), email, passwordEncoder.encode(request.password()));
        return UserResponse.from(repository.save(user));
    }

    @Transactional
    public UserResponse update(UUID id, UserRequest request) {
        User user = findEntity(id);
        String email = normalizeEmail(request.email());
        if (!user.getEmail().equalsIgnoreCase(email) && repository.existsByEmailIgnoreCase(email)) {
            throw new BusinessRuleException("Já existe um usuário cadastrado com este e-mail");
        }
        user.setName(request.name().trim());
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(request.password()));
        return UserResponse.from(user);
    }

    @Transactional
    public void delete(UUID id) {
        User user = findEntity(id);
        if (categoryRepository.existsByUserId(id) || accountRepository.existsByUserId(id)
                || transactionRepository.existsByUserId(id) || goalRepository.existsByUserId(id)) {
            throw new BusinessRuleException("O usuário possui dados financeiros e não pode ser excluído");
        }
        repository.delete(user);
    }

    @Transactional(readOnly = true)
    public User findEntity(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Usuário não encontrado"));
    }

    private String normalizeEmail(String email) {
        return email.trim().toLowerCase();
    }
}
