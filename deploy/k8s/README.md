# LifeOS Kubernetes Manifests

Kubernetes deployment manifests for LifeOS application.

## Directory Structure

```
k8s/
├── staging/           # Staging environment manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml    # Template only - use sealed-secrets or external-secrets
│   ├── deployment.yaml
│   ├── service.yaml
│   └── kustomization.yaml
└── production/        # Production environment manifests
    ├── namespace.yaml
    ├── configmap.yaml
    ├── secret.yaml    # Template only - use external secrets operator
    ├── deployment.yaml
    ├── service.yaml
    └── kustomization.yaml
```

## Quick Start

### Prerequisites

- `kubectl` configured with cluster access
- `kustomize` (or `kubectl` v1.14+)
- Secrets configured (see [Secrets Management](#secrets-management))

### Deploy to Staging

```bash
# Preview what will be applied
kubectl kustomize deploy/k8s/staging

# Apply to cluster
kubectl apply -k deploy/k8s/staging
```

### Deploy to Production

```bash
# Preview what will be applied
kubectl kustomize deploy/k8s/production

# Apply to cluster (requires appropriate RBAC)
kubectl apply -k deploy/k8s/production
```

## Secrets Management

**⚠️ WARNING: Never commit real secrets to git.**

The `secret.yaml` files are templates only. For actual deployments:

### Option 1: kubectl (development/initial setup only)

```bash
kubectl create secret generic lifeos-secrets \
  --namespace=lifeos-staging \
  --from-literal=DATABASE_URL='postgresql://user:pass@host:5432/db' \
  --from-literal=SECRET_KEY='your-secret-key' \
  --from-literal=REDIS_URL='redis://redis:6379/0'
```

### Option 2: Sealed Secrets (Bitnami)

```bash
# Install kubeseal
brew install kubeseal

# Create sealed secret
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml
```

### Option 3: External Secrets Operator (Recommended for Production)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: lifeos-secrets
  namespace: lifeos-production
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: lifeos-secrets
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: lifeos/production/database
```

## Environment Differences

| Aspect | Staging | Production |
|--------|---------|------------|
| Replicas | 2 | 3 |
| Min HPA | 2 | 3 |
| Max HPA | 5 | 10 |
| CPU Request | 250m | 500m |
| Memory Request | 512Mi | 1Gi |
| CPU Limit | 1000m | 2000m |
| Memory Limit | 1Gi | 2Gi |
| Log Level | INFO | WARNING |
| Rate Limit | 200/min | 100/min |
| PDB | None | minAvailable: 2 |
| Network Policy | None | Restricted |
| Pod Anti-Affinity | Preferred | Required |

## Migrations

Migrations run as a Kubernetes Job before deployment:

```bash
# Run migrations manually
kubectl apply -f deploy/k8s/staging/deployment.yaml

# Or use the job directly
kubectl create job --from=job/lifeos-migrate lifeos-migrate-manual \
  -n lifeos-staging
```

For ArgoCD, the Job has pre-sync hooks configured.

## Monitoring

Both environments expose Prometheus metrics:

- **Endpoint**: `/metrics`
- **Port**: 8000
- **Annotations**: `prometheus.io/scrape: "true"`

### Health Checks

| Probe | Path | Purpose |
|-------|------|---------|
| Liveness | `/health/live` | Restart if unhealthy |
| Readiness | `/health/ready` | Remove from LB if not ready |
| Startup | `/health/ready` | Initial startup validation |

## Troubleshooting

### Pod Not Starting

```bash
# Check events
kubectl describe pod -l app.kubernetes.io/name=lifeos -n lifeos-staging

# Check logs
kubectl logs -l app.kubernetes.io/name=lifeos -n lifeos-staging --tail=100
```

### Migration Failed

```bash
# Check migration job logs
kubectl logs job/lifeos-migrate -n lifeos-staging

# Restart migration
kubectl delete job lifeos-migrate -n lifeos-staging
kubectl apply -f deploy/k8s/staging/deployment.yaml
```

### Scaling Issues

```bash
# Check HPA status
kubectl get hpa lifeos-web-hpa -n lifeos-staging

# Describe for events
kubectl describe hpa lifeos-web-hpa -n lifeos-staging
```

## Updating Image Tag

```bash
# Update staging to specific tag
cd deploy/k8s/staging
kustomize edit set image ghcr.io/your-org/lifeos:staging-abc1234

# Update production to release tag
cd deploy/k8s/production
kustomize edit set image ghcr.io/your-org/lifeos:v1.2.3
```

## ArgoCD Integration

For GitOps deployment, create ArgoCD Applications:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: lifeos-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/lifeos.git
    targetRevision: develop
    path: deploy/k8s/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: lifeos-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Contact

- **DevOps Team**: #devops-team (Slack)
- **On-call**: See PagerDuty escalation policy
