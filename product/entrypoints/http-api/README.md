# HTTP API composition root

Wiring only. Start: `python product/entrypoints/http-api/serve.py` (or `uvicorn main:create_app --factory --app-dir product/entrypoints/http-api`).
First time: `python product/entrypoints/http-api/seed.py` prints generated demo passwords once.

Env: `DATA_DIR` (default ./data), `CRUCIBLE_HOST`, `CRUCIBLE_PORT`, `CRUCIBLE_COOKIE_SECURE` (true behind HTTPS),
`CRUCIBLE_ALLOWED_ORIGINS` (CORS/CSRF allow-list), `RUNNER_ALLOW_FALLBACK=true` (process fallback when Docker is not usable),
`CRUCIBLE_ALLOW_MISSING_MODULES=true` (development only), `ANTHROPIC_API_KEY` / `CRUCIBLE_MODEL` (optional AI provider).
Serves `product/entrypoints/web/dist` at `/` when built. Install: `pip install -r product/entrypoints/http-api/requirements.txt`.
