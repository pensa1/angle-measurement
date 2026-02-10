# CI/CD Setup Documentation

## Overview

This project uses GitHub Actions for automated testing, code quality checks, and continuous integration. The CI/CD pipeline ensures code quality, maintains test coverage, and catches issues early in the development process.

## Workflows

### 1. CI Workflow (`ci.yml`)

**Triggers:**
- Push to `main` branch
- Push to any `claude/*` branch
- Pull requests targeting `main` branch

**Jobs:**

#### Test Matrix
Runs tests across multiple Python versions to ensure compatibility:
- Python 3.9
- Python 3.10
- Python 3.11

#### Steps:
1. **Checkout code**: Gets the latest code from the repository
2. **Setup Python**: Installs the specified Python version with pip caching
3. **Install system dependencies**: Installs OpenCV system requirements (libgl1-mesa-glx, libglib2.0-0)
4. **Install Python dependencies**: Installs all packages from requirements.txt
5. **Run tests with coverage**: Executes pytest with coverage reporting
6. **Check coverage threshold**: Fails if coverage drops below 80%
7. **Upload to Codecov**: Sends coverage data to Codecov (Python 3.11 only)
8. **Archive reports**: Saves HTML coverage reports and test results as artifacts

**Coverage Threshold:**
- Minimum: 80%
- Build fails if coverage is below threshold
- Calculated from XML coverage report

**Artifacts:**
- `coverage-report`: HTML coverage report (30-day retention)
- `test-results-{version}`: Coverage XML and raw data (30-day retention)

### 2. Lint Workflow (`lint.yml`)

**Triggers:**
- Push to `main` branch
- Push to any `claude/*` branch
- Pull requests targeting `main` branch

**Jobs:**

#### Lint Job
Checks code quality and formatting:

1. **flake8**: Python linting
   - Fails on syntax errors and undefined names
   - Warns on complexity and style issues
   - Max line length: 127 characters
   - Max complexity: 10

2. **black**: Code formatting
   - Ensures consistent code style
   - Fails if code is not formatted

3. **mypy**: Type checking
   - Optional static type checking
   - Runs but doesn't fail build (informational)

#### Security Job
Scans for security vulnerabilities:

1. **bandit**: Security linter for Python
   - Scans for common security issues
   - Generates JSON report

2. **safety**: Checks for known vulnerabilities
   - Scans installed packages against vulnerability database
   - Informational only (doesn't fail build)

**Artifacts:**
- `security-reports`: Bandit security scan results (30-day retention)

## Status Badges

The README.md includes status badges for:

1. **CI Status**: Shows if tests are passing
   ```markdown
   [![CI](https://github.com/pensa1/angle-measurement/workflows/CI/badge.svg)](https://github.com/pensa1/angle-measurement/actions/workflows/ci.yml)
   ```

2. **Lint Status**: Shows if linting passes
   ```markdown
   [![Lint](https://github.com/pensa1/angle-measurement/workflows/Lint/badge.svg)](https://github.com/pensa1/angle-measurement/actions/workflows/lint.yml)
   ```

3. **Code Coverage**: Shows current test coverage
   ```markdown
   [![codecov](https://codecov.io/gh/pensa1/angle-measurement/branch/main/graph/badge.svg)](https://codecov.io/gh/pensa1/angle-measurement)
   ```

4. **Python Versions**: Supported Python versions
   ```markdown
   [![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)
   ```

5. **License**: Project license
   ```markdown
   [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
   ```

6. **Code Style**: Black formatter
   ```markdown
   [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
   ```

## Pull Request Template

Located at `.github/pull_request_template.md`, this template ensures PRs include:

- Clear description of changes
- Issue reference
- Type of change (bug fix, feature, etc.)
- Testing performed
- Coverage information
- Screenshots for visual changes
- Comprehensive checklist
- Documentation updates

**Usage:** Automatically applied when creating a new PR

## Issue Templates

### Bug Report (`ISSUE_TEMPLATE/bug_report.md`)

Structured template for reporting bugs with:
- Clear bug description
- Reproduction steps
- Expected vs actual behavior
- Environment details
- Error messages/stack traces
- Affected module
- Priority level

### Feature Request (`ISSUE_TEMPLATE/feature_request.md`)

Structured template for proposing features with:
- Feature summary
- Problem statement
- Proposed solution
- Use cases
- Implementation details
- Affected modules
- Testing requirements
- Priority level

## Dependabot Configuration

Located at `.github/dependabot.yml`, automatically:

**Python Dependencies:**
- Weekly checks every Monday at 9:00 AM
- Groups related updates (pytest, opencv)
- Auto-labels PRs with `dependencies` and `python`
- Limits to 5 open PRs
- Ignores major version updates for opencv-python

**GitHub Actions:**
- Weekly checks for action updates
- Auto-labels with `dependencies` and `github-actions`
- Limits to 3 open PRs

## Local Development

### Running Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Running Linting Locally

```bash
# Run flake8
flake8 . --max-line-length=127

# Check formatting with black
black --check .

# Format code with black
black .

# Run type checking
mypy . --ignore-missing-imports

# Run security scan
bandit -r . -ll
```

### Pre-commit Setup (Optional)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run black
black --check . || exit 1

# Run flake8
flake8 . --max-line-length=127 --exclude=venv,.venv || exit 1

# Run tests
pytest tests/ -v || exit 1

echo "All checks passed!"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Coverage Requirements

### Current Threshold: 80%

The CI enforces a minimum coverage threshold of 80%. If coverage drops below this:
- CI build fails
- PR cannot be merged
- Coverage report shows uncovered lines

### Improving Coverage

To improve coverage:
1. Check HTML coverage report: `htmlcov/index.html`
2. Identify uncovered lines (highlighted in red)
3. Add tests for uncovered code paths
4. Run coverage locally to verify
5. Push changes and check CI

### Coverage Exclusions

To exclude code from coverage (use sparingly):

```python
# pragma: no cover
def debug_only_function():  # pragma: no cover
    """This function is excluded from coverage"""
    pass
```

## Troubleshooting

### CI Fails on Coverage Threshold

**Problem:** Build fails with "Coverage X% is below 80% threshold"

**Solution:**
1. Run coverage locally: `pytest --cov=. --cov-report=html`
2. Open `htmlcov/index.html` to see uncovered lines
3. Add tests for uncovered code
4. Re-run and verify coverage increased

### Linting Failures

**Problem:** Black formatting check fails

**Solution:**
```bash
# Format all Python files
black .

# Commit formatted files
git add .
git commit -m "style: Apply black formatting"
```

**Problem:** flake8 reports errors

**Solution:**
1. Review the specific errors
2. Fix code issues
3. For legitimate exceptions, add `# noqa: ERROR_CODE` comment

### OpenCV Import Errors in CI

**Problem:** `ImportError: libGL.so.1: cannot open shared object file`

**Solution:** Already handled by installing system dependencies:
```yaml
- name: Install system dependencies
  run: |
    sudo apt-get update
    sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

### Codecov Upload Failures

**Problem:** Coverage upload fails with authentication error

**Solution:**
1. Ensure `CODECOV_TOKEN` is set in GitHub repository secrets
2. Check Codecov service status
3. Note: Upload failure doesn't fail the build (`fail_ci_if_error: false`)

## Best Practices

1. **Before Pushing:**
   - Run tests locally
   - Check formatting with black
   - Run flake8 to catch lint errors
   - Ensure coverage is above 80%

2. **When Creating PRs:**
   - Fill out the PR template completely
   - Reference related issues
   - Wait for all CI checks to pass
   - Address any failures before requesting review

3. **When Reviewing PRs:**
   - Check that all CI checks pass
   - Review coverage report artifact
   - Verify new code has tests
   - Check that documentation is updated

4. **Maintaining High Coverage:**
   - Write tests for all new code
   - Aim for >90% coverage when possible
   - Test edge cases and error paths
   - Keep tests fast and focused

## Future Enhancements

Planned improvements for CI/CD:

1. **Release Workflow** (Phase 4):
   - Automated versioning
   - Changelog generation
   - PyPI package publishing
   - GitHub release creation

2. **Performance Testing**:
   - Benchmark tests for algorithms
   - Performance regression detection
   - Memory usage tracking

3. **Integration Tests**:
   - End-to-end workflow tests
   - Multi-platform testing (Windows, macOS)
   - Docker-based testing

4. **Documentation Generation**:
   - Auto-generate API docs
   - Deploy docs to GitHub Pages
   - Keep docs in sync with code

## Maintenance

### Updating Workflows

When modifying workflows:
1. Test changes on a feature branch first
2. Use workflow dispatch for manual testing
3. Check workflow syntax with [Action Validator](https://rhysd.github.io/actionlint/)
4. Monitor first run after changes

### Dependency Updates

Dependabot will automatically create PRs for updates:
1. Review the changelog for breaking changes
2. Check CI status on the dependabot PR
3. Merge if all checks pass
4. For major updates, test locally first

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [flake8 Documentation](https://flake8.pycqa.org/)
- [black Documentation](https://black.readthedocs.io/)
- [Codecov Documentation](https://docs.codecov.com/)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)

## Contact

For questions about CI/CD setup:
- Review this documentation
- Check existing GitHub Actions runs
- Create an issue with the `ci/cd` label
- Contact the DevOps & Release Agent team

---

Last updated: 2026-02-10
