# Contributing to AI Medical Assistant Web App

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests Process

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## 🏗️ Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Local Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/AI-Medical-Assistant-Web-App.git
   cd AI-Medical-Assistant-Web-App
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd my-app
   npm install
   ```

4. **Start Development Environment**
   ```bash
   # Terminal 1 - Backend
   cd backend && python main.py
   
   # Terminal 2 - Frontend
   cd my-app && npm start
   ```

## 📝 Coding Standards

### Python (Backend)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints where possible
- Add docstrings to all public functions and classes
- Maximum line length: 88 characters (Black formatter)

Example:
```python
async def generate_diagnosis(self, symptoms: str, context: Optional[str] = None) -> str:
    """Generate medical diagnosis from symptoms.
    
    Args:
        symptoms: Patient's symptom description
        context: Additional medical context (optional)
        
    Returns:
        Generated diagnosis text
        
    Raises:
        ModelNotLoadedError: If model is not initialized
    """
    pass
```

### TypeScript (Frontend)
- Use strict TypeScript configuration
- Prefer functional components with hooks
- Use meaningful component and variable names
- Add JSDoc comments for complex functions

Example:
```typescript
interface DiagnosisResult {
  diagnosis: string;
  confidence: number;
}

/**
 * Submit symptoms for analysis
 * @param symptoms - Patient's symptom description
 * @returns Promise resolving to diagnosis result
 */
const submitSymptoms = async (symptoms: string): Promise<DiagnosisResult> => {
  // Implementation
};
```

### General Guidelines
- Write self-documenting code
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic
- Include error handling

## 🧪 Testing

### Running Tests

**Backend Tests**
```bash
cd backend
python -m pytest tests/
python test_script1.py  # Integration tests
```

**Frontend Tests**
```bash
cd my-app
npm test
npm run test:coverage
```

### Writing Tests

**Backend Test Example**
```python
import pytest
from adapters.local_model_adapter import LocalModelAdapter

@pytest.mark.asyncio
async def test_diagnosis_generation():
    adapter = LocalModelAdapter("path/to/model")
    await adapter.load_model()
    
    result = await adapter.generate_diagnosis("headache and fever")
    
    assert result is not None
    assert len(result) > 0
```

**Frontend Test Example**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import DiagnosisForm from './DiagnosisForm';

test('submits symptoms correctly', () => {
  const mockSubmit = jest.fn();
  render(<DiagnosisForm onSubmit={mockSubmit} />);
  
  fireEvent.change(screen.getByLabelText(/symptoms/i), {
    target: { value: 'headache and fever' }
  });
  fireEvent.click(screen.getByText(/submit/i));
  
  expect(mockSubmit).toHaveBeenCalledWith('headache and fever');
});
```

## 🐛 Bug Reports

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/Jwongjs/AI-Medical-Assistant-Web-App/issues).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening)

### Bug Report Template
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
 - OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
 - Python Version: [e.g. 3.9.0]
 - Node.js Version: [e.g. 16.14.0]
 - Browser: [e.g. Chrome 96, Firefox 95]

**Additional context**
Add any other context about the problem here.
```

## 💡 Feature Requests

We welcome feature requests! Please provide:

- **Problem Statement**: What problem does this solve?
- **Proposed Solution**: How should it work?
- **Alternatives**: What other approaches did you consider?
- **Additional Context**: Screenshots, mockups, etc.

## 🏷️ Project Structure for Contributors

### Backend Architecture
```
backend/
├── adapters/          # Model integration layer
├── api/              # REST API endpoints
├── graphs/           # LangGraph workflow definitions
├── managers/         # Singleton managers
├── nodes/            # Workflow node implementations
├── schemas/          # Pydantic data models
└── models/           # Database models (future)
```

### Frontend Architecture
```
my-app/src/
├── components/       # Reusable UI components
├── pages/           # Main application pages
├── hooks/           # Custom React hooks
├── services/        # API integration
├── workflow/        # Workflow routing logic
└── types/           # TypeScript definitions
```

## 🎯 Areas for Contribution

### High Priority
- [ ] Unit test coverage improvement
- [ ] Performance optimization
- [ ] Accessibility improvements
- [ ] Mobile responsive design
- [ ] Error handling enhancement

### Medium Priority
- [ ] Additional AI model integrations
- [ ] Advanced analytics and reporting
- [ ] User authentication system
- [ ] Multi-language support
- [ ] Progressive Web App features

### Low Priority
- [ ] Dark mode theme
- [ ] Voice input integration
- [ ] Offline mode support
- [ ] Advanced visualization features

## 🔒 Security Guidelines

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Report security vulnerabilities privately

## 📋 Code Review Process

1. **Self Review**: Review your own code before submitting
2. **Automated Checks**: Ensure all CI checks pass
3. **Peer Review**: At least one maintainer review required
4. **Testing**: All tests must pass
5. **Documentation**: Update docs if needed

### Review Checklist
- [ ] Code follows project conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data exposed
- [ ] Performance impact considered
- [ ] Accessibility guidelines followed

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md)
- Ask questions if something is unclear

## 📞 Getting Help

- 📖 Check existing [documentation](./README.md)
- 🔍 Search [existing issues](https://github.com/Jwongjs/AI-Medical-Assistant-Web-App/issues)
- 💬 Join [discussions](https://github.com/Jwongjs/AI-Medical-Assistant-Web-App/discussions)
- 📧 Contact maintainers for sensitive issues

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI Medical Assistant Web App! 🙏
