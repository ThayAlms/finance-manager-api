package br.com.finai.service;

import br.com.finai.domain.entity.Category;
import br.com.finai.domain.entity.User;
import br.com.finai.dto.category.CategoryRequest;
import br.com.finai.dto.category.CategoryResponse;
import br.com.finai.exception.BusinessRuleException;
import br.com.finai.exception.ResourceNotFoundException;
import br.com.finai.repository.CategoryRepository;
import br.com.finai.repository.FinancialTransactionRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class CategoryService {

    private final CategoryRepository repository;
    private final FinancialTransactionRepository transactionRepository;
    private final UserService userService;

    public CategoryService(CategoryRepository repository,
                           FinancialTransactionRepository transactionRepository,
                           UserService userService) {
        this.repository = repository;
        this.transactionRepository = transactionRepository;
        this.userService = userService;
    }

    @Transactional(readOnly = true)
    public List<CategoryResponse> findAllByUser(UUID userId) {
        userService.findEntity(userId);
        return repository.findAllByUserIdOrderByName(userId).stream().map(CategoryResponse::from).toList();
    }

    @Transactional(readOnly = true)
    public CategoryResponse findById(UUID id) { return CategoryResponse.from(findEntity(id)); }

    @Transactional
    public CategoryResponse create(CategoryRequest request) {
        User user = userService.findEntity(request.userId());
        validateDuplicate(request, null);
        return CategoryResponse.from(repository.save(
                new Category(request.name().trim(), request.type(), user)));
    }

    @Transactional
    public CategoryResponse update(UUID id, CategoryRequest request) {
        Category category = findEntity(id);
        ensureOwner(category, request.userId());
        validateDuplicate(request, id);
        category.setName(request.name().trim());
        category.setType(request.type());
        return CategoryResponse.from(category);
    }

    @Transactional
    public void delete(UUID id) {
        Category category = findEntity(id);
        if (transactionRepository.existsByCategoryId(id)) {
            throw new BusinessRuleException("A categoria possui transações e não pode ser excluída");
        }
        repository.delete(category);
    }

    @Transactional(readOnly = true)
    public Category findEntity(UUID id) {
        return repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Categoria não encontrada"));
    }

    private void validateDuplicate(CategoryRequest request, UUID currentId) {
        boolean duplicate = currentId == null
                ? repository.existsByNameIgnoreCaseAndTypeAndUserId(
                        request.name().trim(), request.type(), request.userId())
                : repository.existsByNameIgnoreCaseAndTypeAndUserIdAndIdNot(
                        request.name().trim(), request.type(), request.userId(), currentId);
        if (duplicate) throw new BusinessRuleException("Já existe uma categoria com este nome e tipo");
    }

    private void ensureOwner(Category category, UUID userId) {
        if (!category.getUser().getId().equals(userId)) {
            throw new BusinessRuleException("Não é permitido transferir uma categoria para outro usuário");
        }
    }
}
