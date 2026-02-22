# Production checklist

Use this before deploying or sharing the orchestrator in a production setting.

## Secrets & environment

- [ ] **Never commit `.env`** — It's in `.gitignore`. Use your platform's secret manager (e.g. Azure Key Vault, AWS Secrets Manager) or env vars for API keys.
- [ ] **Rotate keys** if they were ever exposed (e.g. pasted in chat or committed). Rotate in [OpenAI API keys](https://platform.openai.com/api-keys) or your provider.
- [ ] **Separate dev/prod keys** — Use different API keys and (if applicable) different SMTP and DB for production.

## Email (SMTP)

- [ ] **Real SMTP only when ready** — Set `SMTP_MOCK_MODE=false` in prod only after testing. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_USE_TLS` in `.env`.
- [ ] **Use a transactional provider** (e.g. SendGrid, Mailgun, AWS SES) for deliverability and logging.

## Database

- [ ] **SQLite is for demo** — For production, consider PostgreSQL or another DB. Update `DatabaseTool` (and optionally `tools/database_tool.py`) to use a proper driver and connection string from env.
- [ ] **Backups** — Ensure DB backups and retention if you rely on ERP data.

## Logging & monitoring

- [ ] **Log level** — Set `LOG_LEVEL=INFO` or `WARNING` in production; avoid `DEBUG` in prod.
- [ ] **Log destination** — Send logs to a file or log aggregator (e.g. CloudWatch, Datadog) instead of only console.

## Rate limits & reliability

- [ ] **LLM rate limits** — If you hit OpenAI/Anthropic limits, add retries or backoff in your code or use a queue for runs.
- [ ] **Idempotency** — For execution (emails, price updates), consider idempotency keys or checks so duplicate runs don’t double-send or double-update.

## Optional

- [ ] **Pinecone RAG** — If using business-document RAG, set `PINECONE_*` in env and implement embedding + indexing in `config/pinecone_rag.py`.
- [ ] **Virtual environment** — Use a venv (e.g. `.venv`) in production and install only from `requirements.txt` for reproducible runs.
