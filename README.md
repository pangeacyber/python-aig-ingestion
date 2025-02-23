# AI Guard Data Ingestion in Python

An example Python app that demonstrates integrating Pangea's [AI Guard][]
service to protect data ingestion.

In this case, the data to be ingested consists of articles about authentication
from our [Secure by Design Hub][] included in `data/`.

## Prerequisites

- Python v3.12 or greater.
- pip v24.2 or [uv][] v0.5.26.
- A [Pangea account][Pangea signup] with AI Guard enabled.
- An [OpenAI API key][OpenAI API keys].

## Setup

```shell
git clone https://github.com/pangeacyber/python-aig-ingestion.git
cd python-aig-ingestion
```

If using pip:

```shell
python -m venv .venv
source .venv/bin/activate
pip install .
```

Or, if using uv:

```shell
uv sync
source .venv/bin/activate
```

Then the app can be executed with:

```shell
python aig_ingestion.py "What do you know about OAuth?"
```

_Note:_ Because our context is limited to the authentication articles mentioned
above, if you ask a question outside that context, you will get some variation
of "I don't know."

## Usage

```
Usage: aig_ingestion.py [OPTIONS] PROMPT

Options:
  --model TEXT           OpenAI model.  [default: gpt-4o-mini; required]
  --ai-guard-token TEXT  Pangea AI Guard API token. May also be set via the
                         `PANGEA_AI_GUARD_TOKEN` environment variable.
                         [required]
  --pangea-domain TEXT   Pangea API domain. May also be set via the
                         `PANGEA_DOMAIN` environment variable.  [default:
                         aws.us.pangea.cloud; required]
  --openai-api-key TEXT  OpenAI API key. May also be set via the
                         `OPENAI_API_KEY` environment variable.  [required]
  --help                 Show this message and exit.
```

## Example

```shell
python aig_ingestion.py "What do you know about OAuth?"
```

```
OAuth 2.0 is a widely used protocol primarily concerned with authorization and
resource access control. It allows third-party applications to grant limited
access to user accounts on an HTTP service without exposing user credentials.
OAuth focuses on granting access to resources rather than user authentication.
OpenID Connect (OIDC) builds on OAuth 2.0, adding a layer of user
authentication, which makes them complementary. While OAuth allows apps to
access resources on behalf of users, OIDC enables apps to securely verify a
user's identity.
```

Audit logs can be viewed at the [Secure Audit Log Viewer][].

[AI Guard]: https://pangea.cloud/docs/ai-guard/
[Pangea signup]: https://pangea.cloud/signup
[Secure by Design Hub]: https://pangea.cloud/securebydesign/
[OpenAI API keys]: https://platform.openai.com/api-keys
[uv]: https://docs.astral.sh/uv/
