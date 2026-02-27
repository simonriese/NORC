# Contributing to NORC

Thank you for your interest in contributing to **NORC**! Whether you are fixing a bug, adding a feature, or improving documentation, your help is appreciated.

## Contribution Workflow

1.  **Fork the Repository:** Fork the repository to your own GitHub account.
2.  **Base Branch:** All development must be based on the **`development`** branch. Please ensure your Pull Requests target the `development` branch of the main repository.
3.  **Create a Feature Branch:** Work on a descriptive branch name (e.g., `fix/noise-calculation` or `feature/new-plot-type`).
4.  **Adhere to Coding Standards:** 
    - For Python code (Analysis), use **`ruff`** for linting and formatting. 
    - Run `make lint` and `make format` in the `analysis/` directory before committing.
5.  **Add Tests:** If you are adding a new feature or fixing a bug in the Python package, please add corresponding tests in `analysis/tests/`.
6.  **Submit a Pull Request:** Open a PR against the `development` branch. Provide a clear description of your changes and reference any relevant issues.

## Guidelines for Students

If you are a student working on NORC for a thesis or a university project, please follow the specialized guidelines in the [Student Contribution Guide](doc/students_contribute.md).

## Licensing

By contributing to NORC, you agree that your contributions will be licensed under the BSD 3-Clause License. Every new file must include the standard project license header.

For more information, see the [LICENSE](LICENSE) file in the project root.
