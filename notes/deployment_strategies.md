# Deployment Strategies

## Common Deployment Strategies in SDLC

### 1. Recreate In Place

* What: Stop the old version and deploy the new one in its place.
* Use case: Simple apps, early-stage products, low user impact.
* Pros: Easy to implement.
* Cons: Downtime during deployment; no rollback safety.

---

### 2. Rolling Deployment

* What: Gradually replace old instances with new ones (e.g., 1 pod at a time in Kubernetes).
* Use case: Apps behind a load balancer, with multiple instances.
* Pros: No downtime, lower resource usage.
* Cons: Can be slow, hard to rollback instantly if bugs are discovered.

---

### 3. Blue-Green Deployment

* What: Maintain two production environments (blue & green). You deploy to the *inactive* one, then switch traffic.
* Use case: Web apps, services where zero-downtime is critical.
* Pros: Zero downtime, fast rollback (just switch traffic back).
* Cons: Doubles infrastructure temporarily; requires good traffic control.

- Typically best solution for monothlic apps where you need tightly coupled all-or-nothing rollback capability
- Also preferred when it's tricky to split traffic cleanly without affecting user sessions or database state
- Safer for big changes, allows a clear separation between old and new
- Better for when you deploy less frequently and have larger changes

---

### 4. Canary Deployment

Canary Deployments are generally the most well-rounded strategy. They allow you to deploy changes to a small % of traffic and observe real metrics like error %, latency, user behavior after a release. If anything goes wrong, you can revert.

* What: Release the new version to a small % of users, then gradually ramp up.
* Use case: Ship user-facing changes with more confidence that if you have to rollback, only a subset of users are affected
* Pros: Reduces blast radius; controlled exposure.
* Cons: More complexity (routing, monitoring); may need feature toggles.

- Typically best for microservices where you can deploy and route a small % of traffic (1-5%) to new version of the service, and limit the blast radius
- Better when you're deploying frequently and want fast feedback on small, incremental changes

Companies tune their canary deploy schedule based on risk and traffic volume.

- Common ramp patterns include scaling traffic up from 1% -> 5% -> 10% -> 25% -> 50% -> 100% and only scale up if their SLOs are all green
- Typically takes 30 mins to 2 hours if everything goes well
- Critical systems like payments, auth, or storage layers get slower ramps than non-critical ones

Tools like ArgoCD allow you to define these rollout parameters in a dedicated object rather than manually managing it yourself


``` yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:v2
        ports:
        - containerPort: 8080
  strategy:
    canary:
      steps:
      - setWeight: 10          # send 10% of traffic to new version
      - pause: {duration: 10m} # wait 10 minutes before bumping
      - setWeight: 25          # if healthy, bump up to 25%
      - pause: {duration: 20m}
      - setWeight: 50
      - pause: {}

```

- You can either manually update the docker images you're using, or use a service like Argo CD Image Updater which basically polls for new ECR changes for the docker image you specify


``` yaml
metadata:
  name: my-app
  annotations:
    argocd-image-updater.argoproj.io/image-list: my-app=ACCOUNT.dkr.ecr.REGION.amazonaws.com/my-app
    argocd-image-updater.argoproj.io/write-back-method: git:pull-request
    argocd-image-updater.argoproj.io/my-app.update-strategy: semver
    argocd-image-updater.argoproj.io/my-app.allow-tags: regexp:^v[0-9]+\.[0-9]+\.[0-9]+$
```
---

### 5. Feature Flags / Toggles

Feature flags can be used standalone, or alongside blue green or canary deployment strategies

* What: Deploy code with features hidden behind runtime-configurable switches.
* Use case: Safe releases, toggling features for users/teams.
* Pros: Decouple deployment from release; rollback instantly.
* Cons: Requires strong discipline to manage flags over time.

- Can be combined with blue green or canary strategies
- Feature Flags are managed through a remote config service
- Feature flags are pulled from a 3rd party or database and then typically stored in a cache, or even in memory

``` py
if feature_flags["new_checkout_flow"]:
    show_new_checkout()
else:
    show_old_checkout()
```

- There are multiple strategies to effectively using them:

1. Load Feature Flags on Startup
    - Simple, but requires restart or refresh to update flags
2. Poll for Feature Flag Updates
    - Simpler than websocket implementation, but might have slightly stale flags
3. Have Websocket or SSE connections to update flags in real time as they're changed
    - More Complex to manage and requires reconnection logic

---

## Choosing the Right Strategy

| Criteria                | Best Strategies                    |
| ----------------------- | ---------------------------------- |
| Zero downtime           | Rolling, Blue-Green, Canary        |
| Fast rollback           | Blue-Green, Feature Flags          |
| Gradual exposure        | Canary, A/B Testing                |
| Experimental features   | Feature Flags, Shadow, A/B Testing |
| Simplicity              | Recreate, Rolling                  |
| Real-user safety checks | Canary, Shadow                     |

