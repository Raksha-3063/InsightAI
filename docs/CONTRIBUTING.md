# Contributing to InsightAI

We welcome contributions to InsightAI! Follow these steps to submit your work.

---

## Contribution Workflow

1. **Fork & Branch**:
   Fork the repository and create a descriptive branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Develop**:
   Make edits adhering to PEP 8 (Python) and ESLint (TypeScript) coding standards.

3. **Verify**:
   Ensure all tests pass before submitting code:
   ```bash
   $env:PYTHONPATH="."; $env:TESTING="true"; pytest
   ```

4. **Document**:
   Update architecture and API docs under `docs/` if modifying core endpoints.

5. **Submit PR**:
   Create a Pull Request to `main`. Detail your changes, testing verified, and issues fixed.
