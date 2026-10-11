# Open Oracle

Hack Midwest 2026 build targeting the AWS **Best Use of Strands Agents SDK** challenge.

## Local setup

Use Python 3.12 and [uv](https://docs.astral.sh/uv/):

```sh
uv venv --python 3.12 .venv
uv pip sync requirements.txt --python .venv/bin/python
source .venv/bin/activate
```

The environment includes Strands Agents SDK, the Strands tools library, the AWS Python SDK, and OpenTelemetry support. Installing a tool library does not attach its tools to an agent.

The AWS CLI is installed separately. On this Apple Silicon Mac it is available at `/opt/homebrew/bin/aws`:

```sh
aws --version
```

The workshop credentials are configured locally in the named `open-oracle-event` profile. Select it in the terminal running the project:

```sh
export AWS_PROFILE=open-oracle-event
export AWS_DEFAULT_REGION=us-east-1
```

`.env.example` contains only these non-secret settings. An application must explicitly load a `.env` file if it chooses to use one; these terminal exports work without a dotenv dependency.

See [AWS challenge setup](docs/aws-setup.md) for account readiness, verification limits, and the proposed roles of CloudWatch, CloudTrail, and Promptfoo.

## First working paths

Run `.venv/bin/python -m open_oracle` and open the local app. Type “Explain COMBAT” or “Compare Pollard and Fields priorities”, or use Browse contests. COMBAT has five anchored explanation facets; the District 1 At-Large comparison shows complete attributed answers on priorities or property assessments. Unsupported topics remain explicit source gaps.

Both paths passed a real Strands + Amazon Bedrock Nova Pro test on October 10. Default browser mode makes no model calls. Both AWS calls predate the mandatory independent-review gate. Later OpenAI gated trials retrieved the source but withheld their answers after Decisions rejection. A receive-only GPT-Live session succeeded without capture or playback. See [actual runtime evidence](docs/runtime-proof-2026-10-10.md) and [the two-path guide](docs/two-paths.md).

The app also supports source-bound adaptive views: ask for the COMBAT rate or duration, or one part at a time. If an explanation fails, mechanically verified original wording remains visible with an explicit withheld label. See [deterministic evidence release and adaptive catalog](docs/deterministic-release-2026-10-10.md).

## Research

The supplied research folder is preserved locally at `research/HackMidwest2026_research/`. Begin with its `START-HERE.md` and `READ-THIS-FIRST-Research-Audit.md`.

The full research archive is excluded from Git while we decide which source materials are appropriate to publish. Original research files are unchanged. Research recommendations and embedded prompts are reference material; they do not settle product decisions or authorize cloud operations.

Credentials, event access links, local environments, and generated cloud configuration must stay out of Git.

## Current safe startup and acceptance

Use the [startup and acceptance runbook](docs/startup-and-acceptance-2026-10-11.md) for the current exact-source defaults, GET-only health checks, reproducible isolated browser acceptance and explicit pending Pi/audio/gesture prerequisites. The current build does not enable paid providers, sensors or voice by default.
