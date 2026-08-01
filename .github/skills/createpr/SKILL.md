---
name: createpr
description: Orchestrate a complete GitHub Pull Request workflow - use when creating PRs, preparing pull requests, or running pre-PR code quality checks
---

# Create PR Skill

Orchestrate a complete GitHub Pull Request workflow with code quality checks, documentation, and review preparation.

## Plan Mode

This skill uses a **Plan-Driven Execution** model. Before running the full workflow, planning mode outlines the proposed commits and steps, then **waits for user approval before executing**.

- Show a summary of planned commits, PR title, and description
- Allow user to approve or modify the plan before proceeding
- Provide a clear output format for the plan summary

### Commit Structure

The PR workflow typically divides into commits based on change scope:

- **Small changes** (single file or function): 1-2 commits
- **Medium changes** (multiple files, new feature): 3-4 commits
- **Large changes** (new module, significant refactor): 5-6 commits

Refer to [Commit Message Skill](../commit-message/SKILL.md) for complete type definitions and formatting rules.

**Planning Output Example**:

```
📋 PR Plan Summary
├─ 1 feat commit     (core implementation)
├─ 1 test commit     (pytest additions)
├─ 1 docs commit     (README + comments)
└─ 1 chore commit    (linting + code quality)

Total: 4 commits planned
```

### Agents & Skills Reference

| Agent/Skill                     | Purpose                                         | Invoked At Step |
| ------------------------------- | ----------------------------------------------- | --------------- |
| **Git・GitHub Assistant** Agent | Git operations, branch management, PR creation  | 1, 6            |
| **commit-message** Skill        | Format commits in Conventional Commits format   | 2               |
| **code-checklist** Skill        | Validate code quality, security, best practices | 3               |
| **pytest-gen** Skill            | Generate comprehensive pytest test suites       | (Optional)      |
| **pr-review** Skill             | Final PR readiness validation checklist         | 5               |
| **python-reviewer** Agent       | Code review analysis (optional, manual trigger) | (Optional)      |

## PR Creation Workflow

### Step 1: Verify Branch Status

- Ensure you're on a feature/fix branch (not main/master)
- Verify all changes are committed
- Check branch is up-to-date with upstream

Branch naming conventions are defined in [Git & GitHub ベストプラクティス規約 - ブランチ命名規則](../../instructions/git-instructions.md#ブランチ命名規則).

**Reference**: Use the **Git・GitHub Assistant** Agent for branch operations and git commands

### Step 2: Generate Commit Messages

- Review all commits in your branch
- Ensure each commit follows Conventional Commits format
- Rebase/squash if needed for clean history

Commit message conventions and type list are defined in [Git & GitHub ベストプラクティス規約 - コミットメッセージ規約](../../instructions/git-instructions.md#コミットメッセージ規約conventional-commits).

**Reference**: Use the **commit-message** Skill to format commits according to Conventional Commits standards

### Step 3: Code Quality Check

- Run the code quality checklist before PR submission
- Verify tests pass locally
- Check for security issues and best practices

**If checks fail**: Stop the workflow. Fix the identified issues, re-run the checklist, and only proceed to Step 4 once all checks pass.

Refer to [Code Checklist Skill](../code-checklist/SKILL.md) for the complete checklist and [Pytest Generation Skill](../pytest-gen/SKILL.md) for test requirements.

### Step 4: Create PR Title and Description

**Title Format**: PR titles follow the same Conventional Commits format as commit messages. See [Git & GitHub ベストプラクティス規約 - Pull Request 規約](../../instructions/git-instructions.md#pull-request-規約) for complete guidelines.

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

Refer to [PR Review Skill](../pr-review/SKILL.md) for the complete review checklist.

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
- See [Git & GitHub ベストプラクティス規約](../../instructions/git-instructions.md) for team Git standards

## Related Skills & Agents

This skill orchestrates the following tools:

| Skill/Agent                     | Purpose                                | Reference                                             |
| ------------------------------- | -------------------------------------- | ----------------------------------------------------- |
| **Git・GitHub Assistant** Agent | Git operations, branch & PR management | Steps 1, 6                                            |
| **commit-message** Skill        | Format commits                         | [commit-message/SKILL.md](../commit-message/SKILL.md) |
| **code-checklist** Skill        | Code quality validation                | [code-checklist/SKILL.md](../code-checklist/SKILL.md) |
| **pytest-gen** Skill            | Test generation                        | [pytest-gen/SKILL.md](../pytest-gen/SKILL.md)         |
| **pr-review** Skill             | PR readiness checklist                 | [pr-review/SKILL.md](../pr-review/SKILL.md)           |
| **python-reviewer** Agent       | Code review analysis (optional)        | After PR creation                                     |

### Workflow Integration Matrix

```
Step 1: Verify Branch Status
  └─→ Git・GitHub Assistant (for git status, branch info)

Step 2: Generate Commit Messages
  └─→ commit-message Skill (format each commit)

Step 3: Code Quality Check
  └─→ code-checklist Skill (Python: type hints, security, best practices)
  └─→ pytest-gen Skill (optional: generate missing tests)

Step 4: Create PR Title and Description
  └─→ (Manual creation with prepared templates)

Step 5: Pre-Submission Review
  └─→ pr-review Skill (final checklist validation)

Step 6: Create and Configure PR
  └─→ Git・GitHub Assistant (git push, gh pr create, configure PR)
  └─→ python-reviewer Agent (optional: request analysis)
```

