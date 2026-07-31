# Serverless

**[reference]** — from roadmap.sh and vendor docs.

## What serverless means

"Serverless" doesn't mean no servers — it means *you* don't manage them. You hand the provider a function (or a container), and it runs, scales, and bills per-invocation, scaling to **zero** when idle. The name is marketing; the real properties are: no server management, automatic scaling, and pay-per-use with no idle cost.

The two main flavors:

- **FaaS (Functions as a Service)** — deploy a single function triggered by an event. AWS Lambda, Azure Functions, Google Cloud Functions.
- **Serverless containers** — deploy a container that scales to zero. AWS Fargate, Google Cloud Run, Azure Container Apps. More flexible than FaaS (any language/runtime, longer runtimes) without managing the orchestrator.

## The FaaS model

A function is bound to an **event trigger** and runs only when the event fires:

```
HTTP request  ─┐
S3 upload      ├─►  your function runs  ─►  scales automatically with event rate  ─►  bills per ms
queue message  ┘
```

```python
# AWS Lambda handler — runs per invocation, no server, no scaling code
def handler(event, context):
    record = event["Records"][0]
    process(record)
    return {"statusCode": 200}
```

You write the handler; the platform owns everything else — provisioning, scaling from 0 to thousands of concurrent executions, patching, availability.

## The cold-start tradeoff

The defining FaaS gotcha: when a function hasn't run recently, the platform must spin up a fresh execution environment — a **cold start** — adding latency (tens of ms to seconds, depending on runtime and package size). A "warm" instance reused for a follow-up invocation skips it. Consequences:

- Latency-sensitive, steady-traffic workloads suffer from cold starts and cost more than a warm VM — serverless is *not* automatically the low-latency choice.
- Heavy runtimes (a fat JVM) cold-start slower than light ones (Go, Node, Python) — which is exactly why the [[languages/01-java/05-web-and-api/02-web-frameworks|Quarkus/Micronaut + GraalVM native-image]] push exists: to make Java viable in FaaS.
- Mitigations: provisioned concurrency (pay to keep instances warm — but that's no longer scaling to zero), smaller packages, lighter runtimes.

## When serverless fits — and when it doesn't

**Fits:** spiky or unpredictable traffic (scale-to-zero saves money when idle), event-driven glue (respond to an upload, a queue message, a webhook), cron-style jobs, and rapid prototyping where you don't want to run infrastructure.

**Doesn't fit:** sustained high-throughput workloads (a busy VM/container is cheaper), latency-critical paths that can't tolerate cold starts, long-running or stateful processing (FaaS functions have execution time limits and are stateless), and anything needing fine-grained control over the runtime environment.

The honest framing: serverless optimizes for *operational simplicity and idle cost*, trading away *latency predictability and cost-at-sustained-scale* — the mirror image of the tradeoff behind the batch pipeline's choice to run long-lived tuned processes ([[languages/01-java/06-applied-systems/03-batch-processing-and-performance|Batch Processing]]).

## Related
- [[devops/03-cloud/01-cloud-fundamentals|Cloud Fundamentals]] — the service-model spectrum FaaS sits at the end of
- [[languages/01-java/05-web-and-api/02-web-frameworks|Web Frameworks (Java)]] — why native-image compilation matters for FaaS
- [[devops/05-orchestration/README|Orchestration]] — the "run containers yourself" alternative to serverless containers
