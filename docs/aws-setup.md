# AWS challenge setup

Prepared October 10, 2026. This records local preparation, not a deployed application or prize-eligibility approval.

## Target

The [official Hack Midwest challenge](https://hackmidwest.com/) awards $2,500 for best use of Strands Agents SDK. The stated judging questions concern actual SDK integration and creative use. The published brief does not mandate a particular AWS hosting service, telemetry service, model, or evaluation tool.

Use the Python SDK to stay aligned with the event's stated Python brief. Current documentation calls it the Strands Harness SDK; its Python installation package remains `strands-agents`.

## Local environment

- Python 3.12 in the project `.venv`.
- `requirements.in` declares Strands SDK with OpenTelemetry support and the Strands tools library.
- `requirements.txt` pins the resolved dependency versions and package hashes.
- AWS CLI v2 is installed through Homebrew for Apple Silicon. The older Intel executable under `/usr/local/bin` was left in place; the working CLI resolves to `/opt/homebrew/bin/aws`.
- The Strands documentation connector is already available in this Codex chat.
- The research move preserved 460 files, totaling 134,470,440 bytes, with identical SHA-256 checksums before and after the move. This includes the original hidden files. The supplied archive is local and excluded from Git pending publication review.

Reproduce Python installation with the README commands. No model call is necessary to check package installation.

## Event account readiness

Daniel supplied an AWS Workshop Studio event sign-in link. Its access code and authentication URLs are intentionally omitted from this repository. Workshop Studio's URL region alone does not establish the region assigned to the event's AWS account.

Daniel subsequently supplied the event's temporary AWS credentials and region. They are configured locally in the `open-oracle-event` profile under `~/.aws/`, outside the repository, with file permissions `0600`. Existing profiles are preserved. No credentials are embedded in project files.

The assigned region is `us-east-1`. Read-only identity verification succeeded as an assumed role. Recheck after refreshing expired event credentials with:

```sh
aws sts get-caller-identity --profile open-oracle-event
```

Bedrock `ListFoundationModels` succeeded and returned 96 text-output catalog entries. The catalog includes Claude and Amazon Nova models. Listing models does not establish invocation permission, quota, subscription status, or credit coverage. Model selection, applicable inference profile, and any supplied knowledge base or runtime remain to be confirmed before the first model call.

No cloud resources, IAM changes, corpus uploads, model subscriptions, or billable model calls are part of this local setup.

## Supporting tools: proposed roles

These serve different purposes and can be combined if the build needs them:

| Component | Purpose | Initial position |
| --- | --- | --- |
| Strands Agents SDK | Agent orchestration and selected tool calls | Required challenge integration; installed locally |
| Amazon Bedrock | Hosted model inference and optional retrieval | Candidate AWS model/retrieval provider; verify event access |
| CloudWatch / OpenTelemetry | Application logs, timings, errors, and agent traces | Leading option for observing an AWS backend; local OTel support included |
| CloudTrail | Audit trail of AWS account and API activity | Account audit layer; not an answer-quality evaluator |
| Promptfoo | Repeatable evaluation of prompts, models, and grounded answers | Consider when the first agent path and its failure cases exist; not installed or configured yet |
| Bedrock AgentCore starter toolkit | Optional deployment/runtime tooling | Defer until the hosting choice; not required by the published challenge |

Recommendation for discussion: Strands plus an event-approved Bedrock model, with local traces first. Add CloudWatch if using an AWS runtime. Use Promptfoo for repeatable answer-quality checks once the evidence flow exists. Treat CloudTrail as account auditing. The runtime reviewer, retrieval store, deployment target, and voice interface remain owner decisions.

## Verification boundaries

Completed locally: AWS CLI `2.37.12` runs as ARM64; Strands SDK `1.59.0`, tools `0.8.9`, Boto3 `1.43.111`, and OpenTelemetry SDK `1.45.1` import successfully. A local Strands-decorated tool returned the expected value, and a Bedrock runtime client was constructed with dummy credentials without making a request. All 82 installed packages passed the dependency compatibility check. Git ignore checks cover the environment, credentials, local state, and research archive; `git diff --check` passed.

Event credentials now pass the live STS identity and Bedrock catalog checks in `us-east-1`. Earlier local connection checks to both the workshop host and PyPI timed out, while package downloads eventually completed. This supports intermittent connectivity as a possible cause of the earlier login delay; it does not establish the cause of the email-code issue. Model invocation permissions, quotas, subscriptions, credit coverage, and end-to-end operation remain unverified.

Installation checks must avoid paid inference, credentials in output, and changes to the workshop account. Package consistency, imports, construction of a regional Bedrock client with explicitly supplied dummy credentials, and direct invocation of a local Strands-decorated tool can validate local setup without cloud access. They do not verify model/tool orchestration end to end.

The global test-audit skill was used to choose narrow setup checks. No redundant test suite was added to an empty application. Evals routing was consulted; no synthetic evaluation cases or product prompts were created because this request is environment preparation and the agent process is still to be discussed.

## Official references

- [Hack Midwest challenge and rules](https://hackmidwest.com/)
- [Strands Python quickstart](https://strandsagents.com/docs/user-guide/sdk/quickstart/python/)
- [Strands tools library](https://github.com/strands-agents/tools)
- [Strands traces](https://strandsagents.com/docs/user-guide/sdk/observability-evaluation/traces/)
- [AWS CLI installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [CloudWatch OpenTelemetry](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-OpenTelemetry-Sections.html)
- [CloudTrail overview](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html)
- [Promptfoo introduction](https://www.promptfoo.dev/docs/intro/)
