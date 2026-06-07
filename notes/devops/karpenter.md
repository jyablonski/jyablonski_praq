# EC2 Cost, Autoscaling, Karpenter, and Spot Handling

## Cost Mental Model

In k8s you pay for nodes, not pods. Karpenter bin-packs all unschedulable pods' resource requests onto the cheapest set of nodes. Cost is roughly:

```
(total requested CPU/mem) / (bin-packing efficiency) * node hourly rate
```

A node is shared capacity, not "the box for service X."

### t3 on-demand baseline (us-east-1, Linux)

| Instance | vCPU | Mem | $/hr | $/mo (24/7) |
| --------- | ---- | ----- | ------- | ----------- |
| t3.small | 2 | 2 GiB | $0.0208 | ~$15 |
| t3.medium | 2 | 4 GiB | $0.0416 | ~$30 |
| t3.large | 2 | 8 GiB | $0.0832 | ~$61 |

All have 2 vCPU; you pay for memory going up the ladder. t4g (Graviton/ARM) is ~10-20% cheaper if images are ARM-compatible. us-west runs a few % higher.

### Pricing models (commitment/risk axis)

- On-demand: full price, no commitment. Baseline.
- Spot: ~60-70% off for t3, but 2-minute reclaim notice. Stateless pods only.
- Savings Plans: 1yr Compute SP ~28% off, 3yr ~50%; EC2 SP (family-locked) 37%/57%; 3yr all-upfront standard RI hits ~65-72%.

Common pattern: cover steady-state floor (minReplicas baseline) with a Compute Savings Plan, run scale-out replicas on Spot. Karpenter handles the split.

### Hidden costs not on the EC2 line

- NAT gateway: ~$32/mo + $0.045/GB processed (pod egress).
- EBS volumes per node: ~$0.08/GB-mo gp3.
- For small clusters these can rival compute cost.

### t3 burstable caveat

t3 is CPU-credit burstable (20-30% baseline). Sustained-CPU work (FastAPI/LLM) burns credits and throttles or charges surplus credits. Let Karpenter pick across families (m/c) rather than locking to t3 for steady compute.

## Autoscaling

Two layers:

1. HPA scales pods 1 to 10 based on CPU utilization (pod count).
1. Karpenter scales nodes to fit the pods (capacity).

When HPA adds pods and nothing can schedule them, Karpenter provisions node capacity. When pods scale back down, Karpenter consolidates: repacks pods and terminates underused nodes. Consolidation is the main win over Cluster Autoscaler.

## Karpenter and Spot

- Give Karpenter a broad instance pool (t3/t4g/m, multiple sizes/AZs) and it picks the cheapest fit.
- Weight Spot with on-demand fallback; it diversifies across types/AZs to limit interruption blast radius.
- It bin-packs and rightsizes automatically instead of you guessing sizes.

## SQS Interruption Queue

Team creates an SQS queue. EventBridge rules forward these events into it:

- Spot interruption warning (the 2-minute notice)
- Rebalance recommendation (earlier, softer risk signal)
- Instance state-change
- Scheduled maintenance

Karpenter polls the queue and acts on messages for nodes it manages. This replaced the standalone AWS Node Termination Handler for Karpenter nodes.

```yaml
    settings:
      interruptionQueue: my-cluster-karpenter-interruption
```

## Interruption Flow

1. AWS signals interruption (or earlier, a rebalance recommendation).
1. Karpenter cordons the node and starts draining.
1. Scheduler reschedules evicted pods onto existing spare capacity, or
   Karpenter provisions a replacement node if none fits.
1. Old node terminates.

Timing: the 2-minute warning is a ceiling, not a floor. Reclaim happens in 2 minutes or less, often less. The rebalance recommendation is the signal that can fire earlier and give extra runway; it does not always precede a reclaim. Design for graceful-if-possible, survivable-if-not.

## Drain Sequence (what hits the pod)

Draining evicts pods respecting PodDisruptionBudgets, via the standard k8s termination sequence:

1. Pod removed from Service endpoints (stops new traffic, eventually).
1. preStop hook runs if defined.
1. SIGTERM sent to PID 1.
1. k8s waits terminationGracePeriodSeconds (default 30).
1. SIGKILL if still alive.

Keep terminationGracePeriodSeconds well under 120 (60-90s) to leave buffer.

## Handling in Code

The job on SIGTERM: stop accepting new work, finish in-flight, close, exit.

### Go graceful shutdown

```go
    func main() {
        srv := &http.Server{Addr: ":8080", Handler: router}
        go func() {
            if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
                log.Fatal(err)
            }
        }()

        ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGTERM)
        defer stop()
        <-ctx.Done()

        shutdownCtx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
        defer cancel()
        if err := srv.Shutdown(shutdownCtx); err != nil {
            log.Printf("forced shutdown: %v", err)
        }
    }
```

Set the shutdown deadline below the grace period. FastAPI/uvicorn handles SIGTERM similarly for short calls.

### Endpoint-propagation race fix

SIGTERM and endpoint removal happen concurrently, so a pod can get new traffic briefly after shutdown starts. Add a preStop sleep so endpoint removal propagates before SIGTERM:

```
lifecycle:
  preStop:
    exec:
      command: ["sleep", "10"]
terminationGracePeriodSeconds: 60
```

### PodDisruptionBudget

```
spec:
  minAvailable: 1
  selector:
    matchLabels: { app: go-backend }
```

Protects the cooperative drain. It cannot stop AWS hard-reclaiming hardware.

## Spot-Safety Rule

Not "all requests finish in 90s." It is: every request either finishes within the grace period, or survives being killed mid-flight via retry, idempotency, or checkpointing.

- Stateless idempotent/retryable (Next.js, Go reads): Spot freely.
- FastAPI short calls: fine.
- Long LLM inference: cannot finish in any spot window. Restructure to stream tokens, checkpoint/resume, or move off the request path to an async queue consumer (don't ack until done, so interruption means redelivery). Otherwise pin only that path to on-demand.

Audit tell: check each endpoint's p99 latency vs grace period, and ask "if this dies halfway, what is the blast radius?" Retry-fixable means spot-safe.
