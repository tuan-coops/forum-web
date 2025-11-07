## Goal — what an AI helper should know

This repository contains multiple small projects. Be precise: identify which subproject you will modify before changing code.

- Jollibee/Backend — Python FastAPI service (SQLAlchemy models in `Jollibee/Backend/models.py`, DB connection in `Jollibee/Backend/database.py`, routes in `Jollibee/Backend/main.py`). The service expects a MySQL DB and currently creates tables at startup via `Base.metadata.create_all(bind=engine)` in `main.py`.
- BTL/sepolia-test — Hardhat Solidity project. See `hardhat.config.js` (uses `dotenv` and expects `SEPOLIA_URL` and `PRIVATE_KEY`), `scripts/deploy.js`, and `contracts/` for contracts/artifacts.
- Blog — small Express app (`Blog/index.js`, `Blog/package.json`) used for demo/utility purposes.

## Important patterns / conventions (actionable)

- FastAPI + SQLAlchemy: database setup uses `SessionLocal`, `get_db()` dependency (in `Jollibee/Backend/database.py`). Use `db: Session = Depends(get_db)` in route handlers and call `db.commit()` / `db.refresh()` after writes. Example: `create_forum` in `Jollibee/Backend/main.py`.
- Models live in `Jollibee/Backend/models.py`; they use SQLAlchemy `declarative_base()` and relationships (e.g., `Forum.creator` -> `User`). Keep migrations in mind (there is no Alembic configured — schema changes are applied with `Base.metadata.create_all`).
- Hardhat: `hardhat.config.js` specifies `solidity: "0.8.28"` and a `sepolia` network using env vars. Use `npx hardhat test` to run tests and `npx hardhat run scripts/deploy.js --network sepolia` to deploy.

## Developer workflows and commands

- Python backend (run locally):
  - Install deps (if not present): `pip install fastapi uvicorn sqlalchemy pymysql` (project lacks a pinned requirements file).
  - Start dev server: `uvicorn main:app --reload --port 8000` from `Jollibee/Backend`.
  - DB: `Jollibee/Backend/database.py` currently points at `mysql+pymysql://root:123456@localhost:3306/forum_app` — update to env vars or the target DB before running.

- Hardhat / Solidity:
  - Install: `npm install` in `BTL/sepolia-test`.
  - Test: `npx hardhat test`.
  - Deploy to Sepolia: set `.env` with `SEPOLIA_URL` and `PRIVATE_KEY`, then `npx hardhat run scripts/deploy.js --network sepolia`.

- Blog (node):
  - `npm install` in `Blog` then `npm run start` (uses `nodemon` and `--inspect` in `package.json`).

## What an AI should do before code edits

1. Identify the target subproject and open its `package.json` / `requirements` and config files.
2. For backend DB changes, confirm whether to update raw `database.py` connection string to use env vars (prefer this) — do not assume credentials.
3. For Solidity changes, check `hardhat.config.js` and `scripts/` for deployment steps and update `.env` keys only when asked to handle secrets (do not write secrets to the repo).

## Files to inspect for common tasks (examples)

- FastAPI endpoints: `Jollibee/Backend/main.py` (create/update/get/delete forum examples).
- DB models: `Jollibee/Backend/models.py` (User, Forum).
- DB config: `Jollibee/Backend/database.py` (SQLAlchemy engine and `get_db`).
- Hardhat config: `BTL/sepolia-test/hardhat.config.js` (env var driven, solidity version `0.8.28`).
- Deployment script: `BTL/sepolia-test/scripts/deploy.js` (check accounts and network usage before running).

## Safety and repo-specific rules

- Never insert plaintext secrets (private keys, RPC URLs) into the repository. Suggest adding or modifying `.env` and document how to set it in the PR description.
- Avoid adding heavy dependency upgrades without CI/tests — this repo contains small demo projects; call out which subproject you changed in the PR title and description.

## Example quick tasks (how-to snippets)

- Run the FastAPI server locally (from `Jollibee/Backend`):

```powershell
pip install fastapi uvicorn sqlalchemy pymysql
uvicorn main:app --reload --port 8000
```

- Run Hardhat tests / deploy (from `BTL/sepolia-test`):

```powershell
npm install
npx hardhat test
# set .env: SEPOLIA_URL and PRIVATE_KEY
npx hardhat run scripts/deploy.js --network sepolia
```

## If something is missing

- If a subproject needs a requirements.txt / package.json updates, list the minimal packages and where to place them. Ask the repo owner before committing large dependency changes.

---
If any section needs more detail (example: missing scripts/deploy.js contents or test patterns), tell me which subproject you want more detail on and I will expand the file with concrete examples or merge into an existing guidance file.
