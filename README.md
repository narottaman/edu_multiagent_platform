# Edu Multi-Agent Learning & Research Platform

Production-oriented starter repository for a LangGraph supervisor with four bounded specialist capabilities: **QA**, **Learning/Teaching**, **Canvas-only Quiz**, and **Research Project Ideation**. It is designed to sit above an existing multimodal RAG service backed by Neo4j + Chroma + Qdrant.

## Architecture

```text
Streamlit/React -> FastAPI -> LangGraph Supervisor
                            |-> QA Agent       -> RAG + Tavily
                            |-> Learning Agent -> RAG + Canvas + arXiv + YouTube + Tavily
                            |-> Quiz Agent     -> Canvas ONLY
                            `-> Research Agent -> deep RAG + arXiv + Tavily

Existing RAG Service -> Neo4j / Chroma / Qdrant / S3
Application state    -> PostgreSQL / Redis
Platform             -> Docker / Kubernetes / Terraform / GitHub Actions
```

The repository intentionally keeps agents in one runtime initially. Split them into independent services only when security or scaling data justifies it. Tool permissions are enforced in `app/tools/registry.py`; the Quiz agent cannot call web/arXiv/RAG tools.

## Repository layout

```text
app/agents/            specialist agents
app/graphs/            LangGraph supervisor
app/tools/             tool clients + authorization registry
app/api/               FastAPI
frontend/              Streamlit prototype UI
infra/k8s/             portable Kubernetes manifests
infra/terraform/       AWS/EKS reference infrastructure
.github/workflows/     CI + Kubernetes deployment
```

## Required APIs / credentials

Only configure integrations you intend to use. `MOCK_MODE=true` lets the service boot and tests run without external credentials.

| Variable | Needed for |
|---|---|
| `GOOGLE_API_KEY` | Gemini agent generation |
| `TAVILY_API_KEY` | external web discovery |
| `YOUTUBE_API_KEY` | learning-resource video discovery |
| `CANVAS_BASE_URL`, `CANVAS_ACCESS_TOKEN` | LMS material; mandatory for real Canvas-only quizzes |
| `RAG_SERVICE_URL`, optional `RAG_SERVICE_API_KEY` | your existing RAG |
| PostgreSQL/Redis variables | durable app state/checkpoints as you add persistence |
| Neo4j/Qdrant/S3 variables | normally consumed by the RAG service, not agents directly |
| OIDC variables | production identity verification |

**Never commit `.env`, Canvas tokens, cloud keys, kubeconfigs, or LLM API keys.** `.env.example` contains empty/template values only.

## Local quick start

Requirements: Python 3.11+, or Docker + Docker Compose.

```bash
cp .env.example .env
# Keep MOCK_MODE=true for the first run.
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,ui]'
pytest -q
uvicorn app.api.main:app --reload
```

In another terminal:

```bash
API_URL=http://localhost:8000 streamlit run frontend/streamlit_app.py
```

Or run infrastructure locally:

```bash
cp .env.example .env
docker compose up --build
```

API: `http://localhost:8000`; UI: `http://localhost:8501`; OpenAPI: `http://localhost:8000/docs`.

## Connect your existing RAG

Set `RAG_SERVICE_URL`. The starter expects:

```http
POST /retrieve
Content-Type: application/json

{"query":"...", "mode":"auto|deep"}
```

Expected response:

```json
{"evidence":[{"source":"rag","title":"Paper title","content":"...","url":null,"citation":"paper:section:paragraph","metadata":{}}]}
```

Keep Neo4j/Chroma/Qdrant traversal inside that service. Add `/graph`, `/visual-search`, etc. later and extend `app/tools/clients.py`.

## Canvas warning

The included Canvas client is a **minimal adapter** demonstrating authentication, course allow-listing, and module lookup. A production Canvas connector should index/fetch pages, module items, files, assignments, and PDFs and preserve Canvas provenance. The Quiz agent must remain Canvas-only at both tool-policy and data layers.

## Production authentication

The starter exposes request identity headers for local development. Before production, replace this with OIDC JWT verification using your university IdP/Auth0/Entra/Keycloak and derive `user_id`, course membership, and scopes server-side. Never trust client-provided scopes. Set `DEV_AUTH_BYPASS=false`.

## Kubernetes

`infra/k8s` contains Deployment, Service, ConfigMap, HPA and an optional Gateway API example. First create a real secret through your cloud secret manager/External Secrets or manually for development; do **not** apply `secret.example.yaml` with real values committed to Git.

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl -n edu-ai create secret generic edu-ai-secrets \
  --from-literal=GOOGLE_API_KEY='...' \
  --from-literal=TAVILY_API_KEY='...' \
  --from-literal=CANVAS_ACCESS_TOKEN='...'
kubectl apply -k infra/k8s
```

Replace image names or let the deployment workflow set immutable SHA tags. Install a Gateway API controller before enabling `gateway.yaml`.

## Terraform / AWS EKS reference

Terraform provisions a VPC, EKS cluster, managed node group, S3 bucket and ECR repositories. It intentionally does **not** provision Neo4j/Chroma/Qdrant/PostgreSQL in this starter because production topology depends on whether you use managed databases or Kubernetes stateful workloads.

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply
aws eks update-kubeconfig --name <terraform-output-cluster-name> --region <region>
```

For Azure/GCP, keep the Kubernetes layer and replace the Terraform provider/modules with AKS/GKE equivalents.

## CI/CD

`ci.yml` runs linting, tests, Docker build smoke test, and Terraform validation. `deploy.yml` builds API/UI images, pushes to GHCR, and deploys immutable SHA tags to Kubernetes.

For the provided generic deploy workflow, create GitHub Environments (`dev`, `staging`, `production`) and add `KUBE_CONFIG_DATA`, a base64-encoded kubeconfig. **For production, prefer GitHub OIDC federation to AWS/Azure/GCP rather than storing a long-lived kubeconfig** and replace that step with the cloud provider's authentication action.

Protect production with required reviewers and branch/tag rules.

## Security checklist before production

- Replace development identity headers with verified OIDC/JWT claims.
- Enforce course ACLs server-side against authoritative enrollment data.
- Store secrets in AWS Secrets Manager/Azure Key Vault/GCP Secret Manager + External Secrets.
- Add egress NetworkPolicies so Quiz cannot reach the public internet.
- Treat retrieved PDF/web text as untrusted data, never instructions.
- Add request/tool budgets, audit logs, PII policy, rate limits, WAF and abuse controls.
- Run code only in ephemeral non-root sandbox workloads with CPU/RAM/time/filesystem limits and network off by default.
- Add TLS, certificate automation and a supported Gateway controller.
- Pin/scan images and dependencies; use non-root containers for hardened production images.

## Evaluation roadmap

Create golden sets for routing, retrieval, QA faithfulness/citations, learning-path quality, Canvas-only quiz grounding, and research-gap false positives. CI should eventually block deployments when these regress. Research ideas should always be presented as **candidate gaps** until independently verified by literature review.

## MCP

Do not make MCP a prerequisite for v1. The current Python/HTTP tool adapters are deliberately narrow. Once contracts stabilize, expose RAG, Canvas, research discovery, and sandbox capabilities through separate MCP servers while retaining the same tool authorization policy.

## What is intentionally a starter vs institution-specific

This repository is runnable in mock mode and contains the full scaffolding, but no generic repository can safely pre-fill university Canvas credentials, IdP settings, your existing RAG schema/endpoints, DNS/TLS, cloud account IDs, or production database topology. Those integration seams are explicit rather than hidden behind fake credentials.

## License

Choose a license appropriate for your institution before publishing publicly (MIT/Apache-2.0 are common for open-source code).
