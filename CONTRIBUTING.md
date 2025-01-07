# Contributing to NEAR Swarm Intelligence

We welcome contributions to make this template more useful for NEAR developers! Here's how you can help:

## Getting Started

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/near_swarm_intelligence
cd near_swarm_intelligence
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Create a branch:
```bash
git checkout -b feature/your-feature-name
```

## Development Setup

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

2. Install pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
pytest tests/
```

## Code Style

We follow Google's Python Style Guide with these additions:

1. **Type Hints**
```python
def process_data(data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Process market data and return metrics."""
```

2. **Docstrings**
```python
def analyze_market(symbol: str) -> MarketAnalysis:
    """Analyze market conditions for a given token.
    
    Args:
        symbol: Token symbol to analyze
        
    Returns:
        MarketAnalysis object with results
        
    Raises:
        MarketDataError: If market data cannot be fetched
    """
```

3. **Error Handling**
```python
try:
    result = await agent.evaluate_proposal(proposal)
except MarketDataError as e:
    logger.error(f"Market data error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise SwarmError(f"Evaluation failed: {e}")
```

## Testing

1. **Unit Tests**
```python
def test_market_analysis():
    """Test market analysis functionality."""
    analyzer = MarketAnalyzer()
    result = analyzer.analyze("NEAR")
    assert result.symbol == "NEAR"
    assert 0 <= result.confidence <= 1
```

2. **Integration Tests**
```python
@pytest.mark.asyncio
async def test_swarm_consensus():
    """Test swarm consensus mechanism."""
    agents = setup_test_swarm()
    result = await agents[0].propose_action(test_proposal)
    assert result["consensus"] is True
```

3. **Test Coverage**
```bash
pytest --cov=near_swarm tests/
```

## Pull Request Process

1. **Before Submitting**
- Run all tests
- Update documentation
- Add test cases
- Follow code style

2. **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing

## Documentation
- [ ] Documentation updated
- [ ] Examples added/updated
```

3. **Review Process**
- Two approvals required
- All tests must pass
- Documentation must be updated

## Documentation

1. **Code Documentation**
- Clear docstrings
- Type hints
- Inline comments for complex logic

2. **API Documentation**
- Update api-reference.md
- Add examples
- Document breaking changes

3. **Examples**
- Add example code
- Update existing examples
- Include test cases

## Issue Reporting

1. **Bug Reports**
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
- Python version:
- OS:
- Package version:
```

2. **Feature Requests**
```markdown
## Feature Description
Clear description of the feature

## Use Case
Why this feature is needed

## Proposed Solution
How it could be implemented

## Alternatives Considered
Other approaches considered
```

## Security

1. **Reporting Security Issues**
- Email: security@near.org
- Subject: "NEAR SWARM SECURITY"
- Do not disclose publicly

2. **Security Best Practices**
- No secrets in code
- Input validation
- Rate limiting
- Error handling

## Release Process

1. **Version Numbering**
- Follow semantic versioning
- Document breaking changes

2. **Release Checklist**
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Release notes prepared

3. **Release Notes**
```markdown
## [1.0.0] - YYYY-MM-DD

### Added
- New feature X
- New feature Y

### Changed
- Modified behavior of Z

### Fixed
- Bug in feature A
- Performance issue in B
```

## Community

- Join our [Discord](https://discord.gg/near)
- Follow us on [Twitter](https://twitter.com/nearprotocol)
- Read our [Blog](https://near.org/blog)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the MIT License. 