# How to Contribute for Students

Welcome to the **NORC** project! As a student working on this repository (e.g., for a thesis or project), your contributions are highly valued. To ensure a smooth collaboration and maintain code quality, please follow these guidelines.

---

## 1. Getting Started

### Forking the Repository
- **Forking:** Instead of working directly on the main repository, you should **fork** the NORC repository to your own GitHub account.
- **Base Branch:** All development should be based on the **`development`** branch. Ensure your PRs are targeted at the `development` branch of the main repository.
- **Issues:** Every feature, bug fix, or task should be tracked with an [Issue](https://github.com/tuda-parallel/NORC/issues). Before starting, ensure an issue exists and assign yourself to it.

### Local Development Environment
NORC consists of two main parts: 
1. **Acquisition:** Located in the `acquisition/` directory. It uses **C++**, **Bash**, and **Spack** for performance measurements.
2. **Analysis:** Located in the `analysis/` directory. It is a **Python** package for evaluating results.

#### Setup for Analysis (Python)
We recommend using an editable installation with development dependencies:

```bash
cd analysis
# It is recommended to use a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with development tools (ruff, pytest, etc.)
pip install -e ".[development-libs]"
```

#### Setup for Acquisition (C++/Bash)
Acquisition requires a more complex setup involving dependencies like Score-P and PAPI. Follow the instructions in the [main README](../README.md#setup-for-data-acquisition) or run the interactive install script:
```bash
cd acquisition
./install.sh
```

---

## 2. Git Lifecycle

### Keep Your Fork Updated
To avoid complex merge conflicts, regularly sync your fork with the `development` branch of the upstream repository:

```bash
# Add upstream remote if you haven't already
git remote add upstream https://github.com/tuda-parallel/NORC.git

# Update your local development branch
git checkout development
git pull upstream development

# Update your feature branch
git checkout feature/your-feature-name
git merge development
```

### Committing Your Changes
- **Frequency:** Commit early and often. Small, atomic commits are easier to review.
- **Messages:** Use clear, descriptive commit messages.
- **Style:** Before committing, ensure your code follows the project's style guidelines.

---

## 3. Testing

### Python (Analysis)
We use `pytest` for testing the Python code in the `analysis/` directory.

#### Running Tests
To run all tests, navigate to the `analysis` directory and execute:
```bash
cd analysis
source .venv/bin/activate
make test
```

#### Adding New Tests
- Place your test files in `analysis/tests/`.
- Name your test files starting with `test_` (e.g., `test_my_feature.py`).
- Every new feature or bug fix should include corresponding tests.

### Acquisition (C++/Bash)
- For the acquisition part, verify your changes by running a small-scale experiment using `acquisition/run.sh`.
- Ensure that the generated `.cubex` files can be correctly parsed by the analysis tool.

---

## 4. Coding Standards & Style

### Python (Analysis)
NORC uses **`ruff`** for both linting and formatting. Configuration is located in `analysis/pyproject.toml`.

You can run ruff manually:
```bash
cd analysis
ruff check . --fix  # Lint and fix common issues
ruff format .        # Format code
```

#### Recommended: Pre-commit Hook
You can automate this by creating a `.git/hooks/pre-commit` file in the repository root:

```bash
#!/bin/bash
# Pre-commit hook to format Python code in the analysis directory

# Check if ruff is installed
if ! command -v ruff &> /dev/null
then
    echo "ruff could not be found, skipping formatting."
    exit 0
fi

echo "Running ruff check..."
ruff check analysis/norc --fix

echo "Running ruff format..."
ruff format analysis/norc

# Add changed files back to the commit
git add analysis/norc
```
*Note: Make the script executable with `chmod +x .git/hooks/pre-commit`.*

### Acquisition (C++/Bash)
- **C++:** Follow a consistent coding style (e.g., LLVM or Google style). Ensure code is well-commented.
- **Bash:** Use `shellcheck` to verify your scripts if possible. Follow best practices for shell scripting (e.g., using `set -e`, proper quoting).

### Licensing & Headers
Every new file **must** include a license header at the top. 

**Header Template:**
```python
"""
<Top level description of the file>

Copyright (c) 2026 TU Darmstadt, Germany
Version: v0.2
Date: <Creation Date>

Licensed under the BSD 3-Clause License.
For more information, see the LICENSE file in the project root:
https://github.com/tuda-parallel/NORC/blob/main/LICENSE
"""
```
*Note: For shell scripts use `#` and for C++ use `//` for comments instead of triple quotes.*

---

## 5. Code Quality & Best Practices

### Modularization
- Organize your code into cohesive modules and classes. 
- Avoid monolithic scripts; if a function is too long, break it down.
- Place core logic in `analysis/norc/core/` and UI-related code in `analysis/norc/ui/`.

### External Dependencies
- **Be Conservative:** Avoid adding new libraries unless absolutely necessary.
- **Optional Dependencies:** If a feature requires a heavy library that isn't needed for the core functionality, consider making it an optional dependency.
- **Import Check:** For Python, use `try-except ImportError` to handle missing optional libraries gracefully.

---

## 6. Definition of Done

Your contribution is considered "done" when it meets the following criteria:

1.  **Functionality:** The feature works as expected and has been verified.
2.  **Tests:** Tests have been added and all tests (old and new) pass.
3.  **Linting:** `ruff check` passes without errors.
4.  **Documentation:** 
    - Update the `README.md` if your changes affect the installation or usage.
    - Add/update Markdown files in the `doc/` directory for significant features.
    - Use Docstrings (Google style) for new functions and classes.
5.  **No Regressions:** Ensure existing tools (`norc_gui`, `norc_analyze`, `acquisition/run.sh`) still function correctly.
6.  **Clean Code:** Code is modular, readable, and follows the styling rules.

---

## 7. Submitting Your Work

Once your task is complete:
1.  **PR Creation Deadline:** You must create a Pull Request to merge your work into the `development` branch **at least two weeks before the end of your thesis**. This allows for early feedback and review.
2.  **Continuous Updates:** You can (and should) continue to update your Pull Request with new commits until the final submission of your thesis.
3.  Ensure your branch is synced with the upstream `development` branch.
4.  Open a **Pull Request (PR)** from your fork's branch to the **`development`** branch of the main repository.
5.  Tag your supervisor or a maintainer for review.
6.  Address any feedback provided during the review process.

---

## 8. Conduct & Communication

- **Language:** Use English for all code, comments, issues, and PRs.
- **Respect:** Maintain professional and respectful communication.
- **Questions:** Don't hesitate to ask questions via GitHub Issues or your internal communication channels.

Happy coding!
