# Create PR Skill

Orchestrate a complete GitHub Pull Request workflow with code quality checks, documentation, and review preparation.

## PR Creation Workflow

### Step 1: Verify Branch Status

- Ensure you're on a feature/fix branch (not main/master)
- Verify all changes are committed
- Check branch is up-to-date with upstream

**Reference**: Use the **Git・GitHub Assistant** Agent for branch operations and git commands

### Step 2: Generate Commit Messages

- Review all commits in your branch
- Ensure each commit follows Conventional Commits format
- Rebase/squash if needed for clean history

**Reference**: Use the **commit-message** Skill for proper formatting following:

- type(scope): description
- Types: feat, fix, docs, style, refactor, perf, test, chore
- Max 72 characters in subject line

### Step 3: Code Quality Check

- Run the code quality checklist before PR submission
- Verify tests pass locally
- Check for security issues and best practices

**Reference**: Use the **code-checklist** Skill to validate:

- Code Quality (type hints, no bare except, no mutable defaults)
- Input Validation (edge cases, error handling)
- Testing Coverage (pytest tests, descriptive names)

### Step 4: Create PR Title and Description

**Title Format**:

```
type(scope): description
```

Example: `feat(book-app): add search functionality by title`

**Description Template**:

```markdown
## Description

Brief explanation of what this PR changes and why.

## Type of Change

- [ ] New feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentation update

## Testing

- How was this tested?
- What edge cases were considered?

## Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
```

### Step 5: Pre-Submission Review

- Run the **pr-review** Skill checklist to validate PR readiness
- Verify all CI/CD checks will pass
- Check for merge conflicts with base branch

**Reference**: Use the **pr-review** Skill to check:

- Code quality standards
- Test coverage
- Documentation completeness
- CHANGELOG updates

### Step 6: Create and Configure PR

- Push branch to remote
- Create PR with prepared title and description
- Link related issues (if any)
- Set reviewers and labels
- Request reviews from team members

**Reference**: Use the **Git・GitHub Assistant** Agent for:

- `git push` commands
- GitHub CLI commands to create PR
- Setting up PR templates and automation

## Output Format

When ready to submit, present:

```
## PR Summary
- **Title**: [Title following conventions]
- **Base Branch**: main/master
- **Compare Branch**: feature-branch-name
- **Description**: [Clear explanation of changes]

## Pre-submission Checklist
✅ Code quality checks passed
✅ Tests passing locally
✅ Commit messages follow conventions
✅ Documentation updated
✅ No security issues identified

## Ready to Create PR
Use Git・GitHub Assistant to push and create PR
```

## Tips

- Keep PRs focused on a single feature/fix
- Reference related issues with #issue-number
- Respond to review feedback promptly
- Keep commit history clean and understandable
- Consider draft PRs for work-in-progress

## Related Skills & Agents

| Reference                       | Usage                                  |
| ------------------------------- | -------------------------------------- |
| **commit-message** Skill        | Format individual commits properly     |
| **code-checklist** Skill        | Validate code quality before PR        |
| **pr-review** Skill             | Final readiness check                  |
| **Git・GitHub Assistant** Agent | Git operations and GitHub CLI commands |
| **python-reviewer** Agent       | Optional: Request code review analysis |
