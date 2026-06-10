CONTRIBUTING.md

--
## Branch naming convention

All branches must adhere to the proposed naming convention. The branch name must match this pattern:

```
^(main|development|(feature|(bug|hot)fix)(\/[a-zA-Z0-9]+([-_][a-zA-Z0-9]+)*){1,2}|release\/[0-9]+(\.[0-9]+)*(-(alpha|beta|rc)[0-9]*)?)$
```

### Allowed Branch Types

**Main branches**
- `main` - prodcution-ready code
- `development` - development branch

**Feature branches**
- `feature/feature-name` - new features
- `feature/feature-name/sub-feature` - new feature with sub-feature

**Bug fix branches:**
- `bugfix/bug-description` - bug fix
- `bugfix/bug-description/sub-fix` - bug fix with sub-fix

**Hotfix branches:**
- `hotfix/issue-description` - critical production fixes
- `hotfix/issue-description/sub-fix` - hotfix with sub-fix

**Release branches:**
- `release/1.0.0` - release versions
- `release/1.0.0-alpha` - alpha releases
- `release/1.0.0-beta1` - beta releases
- `release/1.0.0-rc1` - release candidates

### Examples

**Valid branch names:**
```bash
main
development
feature/user-auth
feature/user-auth/google-login
bugfix/null-pointer-exception
bugfix/login-error/token-refresh
hotfix/payment-gateway-crash
hotfix/db-connection/timeout-fix
release/1.0.0
release/2.1.0-alpha
release/3.0.0-beta1
release/1.5.0-rc2
```

**Invalid branch names:**
```bash
Feature/user-auth          # uppercase in type
feature/user auth          # space in name
feature/user_Auth          # uppercase after separator
fix/my-bug                 # 'fix' is not an allowed type, use 'bugfix'
feature/auth/login/oauth   # too many levels (max 2)
release/1.0.0-gamma1       # 'gamma' is not an allowed tag (use alpha/beta/rc)
hotfix/                    # missing description
random-branch-name         # no type prefix
```

-- 

## Commit Guidelines

 Follows the **Conventional Commits* versioning style: [https://www.conventionalcommits.org/en/v1.0.0/]

### Format

```bash
<type>[optional socpe]: <description>

[optional body]

[optional footer(s)]
```
type = change category (feat,fix,docs,etc)
scope = which part of the proiect is changed/affected (auth,api,readme)

### Commit Types

- **`feat`** - a new feature
- **`fix`** - a buf fix
- **`fix`** - a buf fix
- **`docs`** - documentation only changes
- **`style`** - code style changes (formatting, missing semicolongs,etc.)
- **`refactor`** - code refactoring without feature changes or bug fixes
- **`test`** - adding or updating tests
- **`chore`** - maintenace tasks, dependency updates, etc.
- **`perf`** - performance improvements
- **`ci`** - CI/CD changes

### Examples

**Good commit messages:**
```bash
feat(auth): add useAwesome hook
fix(api): resolve validation issue with nested schemas
docs(inventory): update API documentation
refactor(workflow): simplify vendor workflow execution
test(catalog): add unit tests for schema validation
```

**Bad commit messages:**
```bash
fix bug
update code
feat(caching): adding data models
bugfix(auth): removed bugs in /auth/vendors/auth_flow.py
changes
WIP
```

### Breaking Changes

Add `!` after the type and a `BREAKING CHANGE:` footer:

```bash
[scope]!:

[optional body]

BREAKING CHANGE:
```

**Example:**
```bash
feat(api)!: remove /v1/users endpoint

Migrated all user operations to /v2/users.
The old endpoint will no longer be supported.

BREAKING CHANGE: /v1/users has been removed.
Update all API calls to use /v2/users instead.
```

### Commit Messages Best Practices

1. Use the impeartive mood ("add" not "added" or "adds")
2. Keep the description concise but descriptive
3. Reference issue numbers if applicable: `feat(auth): add OAuth2+OIDC auth (#123)`
4. Use the body for detailed explanations if needed 

--