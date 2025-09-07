# GitHub Actions CI/CD Configuration

This directory contains the GitHub Actions workflows and configuration for the OpenMCP project.

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers**: Push to main/develop, Pull requests, Manual dispatch

**Jobs**:
- **Code Quality**: Black formatting, isort import sorting, flake8 linting, mypy type checking
- **Testing**: Multi-platform (Ubuntu, Windows, macOS) and multi-Python version (3.9-3.12) testing
- **Browser Tests**: Dedicated Selenium/Chrome testing with xvfb for headless operation
- **Security Scan**: Bandit security analysis and Safety vulnerability checking
- **Build & Package**: Package building and validation
- **Coverage**: Test coverage reporting with Codecov integration

**Features**:
- Matrix testing across OS and Python versions
- Separate browser testing with Chrome installation
- Comprehensive test coverage reporting
- Security scanning with multiple tools
- Build artifact generation

### 2. Release Pipeline (`release.yml`)

**Triggers**: Git tags (`v*`), Manual dispatch

**Jobs**:
- **Validation**: Full test suite before release
- **Build**: Create distribution packages
- **GitHub Release**: Automated changelog generation and release creation
- **PyPI Publishing**: Automatic publishing to PyPI (stable) and Test PyPI (pre-release)

**Features**:
- Version validation against tags
- Automated changelog from git history
- Conditional publishing based on version type
- Secure publishing with OIDC

### 3. Nightly Testing (`nightly.yml`)

**Triggers**: Daily at 2 AM UTC, Manual dispatch

**Jobs**:
- **Extended Browser Tests**: Multi-browser (Chrome, Firefox) testing with both headless and display modes
- **Performance Benchmarks**: Observe function performance monitoring
- **Dependency Security**: Enhanced security scanning with multiple tools

**Features**:
- Comprehensive browser compatibility testing
- Performance regression detection  
- Daily security vulnerability scanning
- Stress testing with real websites

### 4. Documentation (`docs.yml`)

**Triggers**: Changes to docs/, src/, README.md, or mkdocs config

**Jobs**:
- **Build Docs**: MkDocs documentation building with API auto-generation
- **Deploy**: GitHub Pages deployment for documentation

**Features**:
- Automatic API documentation from docstrings
- Material Design theme
- GitHub Pages integration

## Configuration Files

### Dependabot (`dependabot.yml`)

- **Python Dependencies**: Weekly updates on Mondays
- **GitHub Actions**: Weekly updates  
- **Grouped Updates**: Related dependencies grouped together
- **Auto-assignment**: Maintainers automatically assigned

### Pre-commit (`pre-commit-config.yaml`)

Local development hooks for:
- Code formatting (Black, isort)
- Linting (flake8)
- Type checking (mypy) 
- Security scanning (bandit)
- Test validation (pytest)

## Setup Instructions

### For Repository Maintainers

1. **Enable GitHub Pages** in repository settings
2. **Configure Secrets**:
   ```
   PYPI_API_TOKEN          # For PyPI publishing
   TEST_PYPI_API_TOKEN     # For Test PyPI publishing  
   CODECOV_TOKEN           # For coverage reporting
   ```

3. **Create Environments**:
   - `pypi` - For production PyPI publishing
   - `test-pypi` - For test PyPI publishing
   - `github-pages` - For documentation deployment

4. **Branch Protection**:
   - Require PR reviews for main branch
   - Require CI checks to pass
   - Enable auto-merge after checks

### For Contributors

1. **Install pre-commit**:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Run tests locally**:
   ```bash
   pip install -e ".[dev]"
   pytest tests/
   ```

3. **Check formatting**:
   ```bash
   black --check src/ tests/
   isort --check-only src/ tests/
   flake8 src/ tests/
   ```

## CI Status Badges

Add these badges to your main README.md:

```markdown
![CI](https://github.com/openmcp/openmcp/workflows/CI/badge.svg)
![Release](https://github.com/openmcp/openmcp/workflows/Release/badge.svg)
![Documentation](https://github.com/openmcp/openmcp/workflows/Documentation/badge.svg)
[![codecov](https://codecov.io/gh/openmcp/openmcp/branch/main/graph/badge.svg)](https://codecov.io/gh/openmcp/openmcp)
[![PyPI version](https://badge.fury.io/py/openmcp.svg)](https://badge.fury.io/py/openmcp)
```

## Performance Monitoring

The nightly workflow includes performance benchmarks for the observe function:

- **Acceptable Performance**: < 5 seconds average response time
- **Alert Threshold**: > 5 seconds triggers failure
- **Metrics Tracked**: Average, min, max response times across 10 runs

## Security

- **Bandit**: Static security analysis
- **Safety**: Known vulnerability checking
- **pip-audit**: Dependency vulnerability scanning
- **Dependabot**: Automated security updates

## Browser Testing

The CI includes comprehensive browser testing:

- **Chrome**: Latest stable version
- **Cross-platform**: Ubuntu (primary), Windows, macOS
- **Headless**: Default mode for CI
- **Display**: Xvfb for non-headless testing when needed

## Troubleshooting

### Common Issues

1. **Chrome installation fails**: 
   - Check if Chrome repositories are accessible
   - Verify GPG key installation

2. **Tests timeout**:
   - Increase timeout values in pytest configuration
   - Check if websites used in tests are accessible

3. **Coverage reports missing**:
   - Ensure pytest-cov is installed
   - Check if CODECOV_TOKEN is configured

4. **Release workflow fails**:
   - Verify version in pyproject.toml matches git tag
   - Check if PyPI tokens are correctly configured

### Debug Tips

- Use `workflow_dispatch` to manually trigger workflows
- Check Actions tab for detailed logs
- Use `continue-on-error: true` for non-critical steps during debugging