# Contributing

Contributions are welcome. Please open an issue or pull request.

## How to contribute

- **Bug reports:** Open an issue with steps to reproduce and your environment (Python version, OS).
- **Features:** Open an issue first to discuss; then submit a PR.
- **Code:** Use type hints, follow the existing style (OOP, logging, Pydantic where applicable), and add or update tests in `run_tests.py` if you change tools or config.

## Setup for development

1. Clone the repo.
2. Create a virtual environment: `python -m venv .venv` and activate it.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set `OPENAI_API_KEY` (or Anthropic) for full flow tests.
5. Run quick tests: `python run_tests.py`. Run full flow: `python main.py`.

## License

By contributing, you agree that your contributions will be used under the same terms as the project license.
