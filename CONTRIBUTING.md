# 🤝 Contributing to ACTORS

Thank you for your interest in contributing to ACTORS! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### 🐛 Reporting Bugs
- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
- Include detailed steps to reproduce the issue
- Provide environment information and logs
- Check existing issues before creating a new one

### ✨ Suggesting Features
- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
- Describe the problem and proposed solution
- Include use cases and technical considerations
- Consider the impact on existing components

### 🔧 Code Contributions
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following our coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to your branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request** using our [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- Go 1.19+
- Node.js 16+
- Rust 1.70+
- Clojure 1.11+
- Git

### Local Development
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Actors.git
cd Actors

# Add upstream remote
git remote add upstream https://github.com/sosloan/Actors.git

# Install dependencies
pip install -r requirements.txt
cd apis/server && npm install && cd ../..
cd GOS && go mod download && cd ..
cd RUSTS && cargo build && cd ..
```

### Running Tests
```bash
# Python tests
pytest

# Go tests
cd GOS && go test ./... && cd ..

# Node.js tests
cd apis/server && npm test && cd ../..

# Rust tests
cd RUSTS && cargo test && cd ..

# Clojure tests
cd CLOJURE && lein test && cd ..
```

## 📋 Coding Standards

### 🐍 Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Use meaningful variable and function names
- Maximum line length: 88 characters (Black formatter)

### 🔵 Go
- Follow standard Go formatting (`gofmt`)
- Use meaningful variable and function names
- Write comprehensive comments for exported functions
- Follow Go naming conventions
- Use `golangci-lint` for additional checks

### 🟨 Node.js/JavaScript
- Use ESLint configuration
- Follow Airbnb JavaScript Style Guide
- Use meaningful variable and function names
- Write JSDoc comments for functions
- Use async/await over callbacks

### 🦀 Rust
- Follow standard Rust formatting (`rustfmt`)
- Use `clippy` for additional linting
- Write comprehensive documentation comments
- Follow Rust naming conventions
- Use meaningful variable and function names

### 🧠 Clojure
- Follow Clojure style guidelines
- Use meaningful function and variable names
- Write docstrings for functions
- Follow functional programming principles
- Use consistent indentation (2 spaces)

## 🧪 Testing Guidelines

### Test Coverage
- Aim for >80% test coverage
- Write unit tests for new functions
- Write integration tests for new features
- Test edge cases and error conditions

### Test Structure
```python
# Python example
def test_function_name():
    """Test description."""
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output
```

```go
// Go example
func TestFunctionName(t *testing.T) {
    // Arrange
    input := "test"
    expected := "expected"
    
    // Act
    result := FunctionUnderTest(input)
    
    // Assert
    if result != expected {
        t.Errorf("Expected %s, got %s", expected, result)
    }
}
```

## 📚 Documentation

### Code Documentation
- Write clear docstrings/comments
- Explain complex algorithms
- Document API endpoints
- Include usage examples

### README Updates
- Update relevant sections when adding features
- Include installation instructions for new dependencies
- Add examples for new functionality
- Keep the quick start guide current

### API Documentation
- Document all public APIs
- Include parameter descriptions
- Provide example requests/responses
- Document error conditions

## 🔄 Pull Request Process

### Before Submitting
- [ ] Run all tests locally
- [ ] Check code formatting
- [ ] Update documentation
- [ ] Add tests for new functionality
- [ ] Ensure no breaking changes (or document them)

### PR Requirements
- [ ] Clear description of changes
- [ ] Link to related issues
- [ ] Screenshots for UI changes
- [ ] Updated documentation
- [ ] Passing CI/CD pipeline

### Review Process
1. **Automated checks** must pass
2. **Code review** by maintainers
3. **Testing** in staging environment
4. **Approval** from at least one maintainer
5. **Merge** to main branch

## 🏷️ Issue Labels

### Bug Reports
- `bug` - Something isn't working
- `priority: critical` - Blocks core functionality
- `priority: high` - Important issue
- `priority: medium` - Moderate impact
- `priority: low` - Minor issue

### Feature Requests
- `enhancement` - New feature or improvement
- `component: [name]` - Specific component affected
- `area: frontend` - Frontend changes
- `area: backend` - Backend changes
- `area: infrastructure` - Infrastructure changes

### Pull Requests
- `ready for review` - Ready for maintainer review
- `needs testing` - Requires additional testing
- `breaking change` - Contains breaking changes
- `documentation` - Documentation updates

## 🚀 Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps
1. **Create release branch** from main
2. **Update version numbers** in relevant files
3. **Update CHANGELOG.md** with new features/fixes
4. **Create pull request** for release
5. **Merge to main** after approval
6. **Create GitHub release** with tag
7. **Deploy** to production

## 🤔 Questions?

- **GitHub Discussions**: For general questions and ideas
- **GitHub Issues**: For bugs and feature requests
- **Pull Requests**: For code contributions

## 📜 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior
- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

### Unacceptable Behavior
- Harassment, trolling, or inflammatory comments
- Personal attacks or political discussions
- Public or private harassment
- Publishing private information without permission
- Any conduct inappropriate in a professional setting

## 🎉 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to ACTORS! 🚀