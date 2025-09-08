# 🤝 Contributing to ACTORS

Thank you for your interest in contributing to ACTORS! This document provides guidelines and information for contributors.

## 🎯 How to Contribute

### **🎯 Ways to Contribute**
- **🐛 Bug Reports**: Report bugs and issues
- **💡 Feature Requests**: Suggest new features
- **💻 Code Contributions**: Submit code improvements
- **📚 Documentation**: Improve documentation
- **🧪 Testing**: Add or improve tests
- **💡 Examples**: Create example implementations

### **🚀 Getting Started**

1. **🍴 Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/ACTORS.git
   cd ACTORS
   ```

2. **⚙️ Set Up Development Environment**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   
   # Install Go dependencies
   cd GOS && go mod tidy && cd ..
   
   # Install Rust dependencies
   cd RUSTS && cargo build && cd ..
   ```

3. **🌿 Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📋 Development Guidelines

### **Code Style**

#### **Python**
- Follow PEP 8 style guidelines
- Use type hints where possible
- Write docstrings for all functions and classes
- Use meaningful variable and function names

```python
def calculate_portfolio_risk(portfolio: Dict[str, float], 
                           market_data: pd.DataFrame) -> float:
    """
    Calculate portfolio risk using VaR methodology.
    
    Args:
        portfolio: Dictionary of asset weights
        market_data: Historical market data
        
    Returns:
        Portfolio risk as a float
    """
    # Implementation here
    pass
```

#### **Go**
- Follow Go standard formatting (`gofmt`)
- Use meaningful variable names
- Write comprehensive comments
- Follow Go naming conventions

```go
// CalculatePortfolioRisk computes the risk of a portfolio
func CalculatePortfolioRisk(portfolio map[string]float64, 
                          marketData []MarketData) float64 {
    // Implementation here
    return risk
}
```

#### **Rust**
- Follow Rust formatting (`rustfmt`)
- Use meaningful variable names
- Write comprehensive documentation
- Follow Rust naming conventions

```rust
/// Calculate portfolio risk using VaR methodology
pub fn calculate_portfolio_risk(
    portfolio: &HashMap<String, f64>,
    market_data: &[MarketData]
) -> f64 {
    // Implementation here
    risk
}
```

### **Testing**

#### **Python Testing**
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_portfolio.py

# Run with coverage
pytest --cov=core --cov-report=html
```

#### **Go Testing**
```bash
cd GOS
go test ./...
go test -v ./...
```

#### **Rust Testing**
```bash
cd RUSTS
cargo test
cargo test --verbose
```

### **Documentation**

- Update README.md for significant changes
- Add docstrings to all new functions
- Update API documentation
- Include examples for new features

## 🚀 Pull Request Process

### **Before Submitting**

1. **Run Tests**
   ```bash
   # Python
   pytest
   
   # Go
   cd GOS && go test ./...
   
   # Rust
   cd RUSTS && cargo test
   ```

2. **Check Code Style**
   ```bash
   # Python
   black .
   flake8 .
   mypy .
   
   # Go
   cd GOS && gofmt -w .
   
   # Rust
   cd RUSTS && cargo fmt
   ```

3. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions
   - Update API documentation

### **Pull Request Template**

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 🏗️ Project Structure

### **Directory Organization**
```
ACTORS/
├── docs/           # Documentation
├── apis/           # API implementations
├── core/           # Core system components
├── GOS/            # Go implementations
├── RUSTS/          # Rust implementations
├── scripts/        # Utility scripts
├── examples/       # Example implementations
├── data/           # Data files
├── tests/          # Test files
└── open-batch-transcription/  # Speech processing
```

### **File Naming Conventions**
- **Python**: `snake_case.py`
- **Go**: `snake_case.go`
- **Rust**: `snake_case.rs`
- **Documentation**: `UPPER_CASE.md`

## 🐛 Bug Reports

### **Bug Report Template**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS, Linux, Windows]
- Python version: [e.g., 3.8.10]
- Go version: [e.g., 1.19.5]
- Rust version: [e.g., 1.70.0]

## Additional Context
Any other relevant information
```

## 💡 Feature Requests

### **Feature Request Template**
```markdown
## Feature Description
Clear description of the feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other solutions you've considered

## Additional Context
Any other relevant information
```

## 🔧 Development Setup

### **IDE Configuration**

#### **VS Code**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "go.formatTool": "goimports",
    "rust-analyzer.checkOnSave.command": "clippy"
}
```

#### **PyCharm**
- Enable type checking
- Configure Black formatter
- Set up pytest integration

### **Pre-commit Hooks**
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## 📚 Resources

### **Documentation**
- [Python Style Guide](https://pep8.org/)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)

### **Tools**
- **Python**: Black, Flake8, MyPy, Pytest
- **Go**: gofmt, goimports, golint
- **Rust**: rustfmt, clippy, cargo

## 🤝 Community Guidelines

### **Code of Conduct**
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the golden rule

### **Communication**
- Use clear, descriptive commit messages
- Provide context in pull requests
- Ask questions when unsure
- Share knowledge and insights

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: dev@actors-finance.com
- **Discord**: [Join our community](https://discord.gg/actors)

## 🎉 Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Community highlights

Thank you for contributing to ACTORS! Together, we're building the future of financial automation. 🦞🚀
