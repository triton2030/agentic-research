---
description: "Maintainer contract for keeping Claude advisor calls on the Claude.ai subscription route without hidden paid fallbacks"
---

# Subscription Billing Boundary

This document owns the billing-route contract for maintainers. Task-time Codex
agents do not need to read it before routine calls because the runtime enforces
the machine-verifiable part on every request.

## Zero-overage setup

To make additional paid usage unavailable:

1. Disable **Usage credits** in Claude Settings.
2. Log Claude Code in only with the Claude.ai Pro/Max account.
3. Do not add Anthropic Console credentials or choose API-credit billing during
   login or limit recovery.

Usage credits are an account-level setting and can fund Claude Code after the
included plan allocation is exhausted. They do not require an
`ANTHROPIC_API_KEY` in the SDK query environment. `claude auth status` does not
expose their enabled state, so this setup item is an external owner invariant.

Official sources:

- [Manage usage credits for paid Claude plans](https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans)
- [Use Claude Code with a Pro or Max plan](https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan)
- [Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [Claude Code legal and authentication boundary](https://code.claude.com/docs/en/legal-and-compliance)
- [Manage API key environment variables in Claude Code](https://support.claude.com/en/articles/12304248-manage-api-key-environment-variables-in-claude-code)
- [Claude Code authentication](https://code.claude.com/docs/en/authentication)

As of the June 16, 2026 update, Anthropic has paused the announced separate
Agent SDK credit: ordinary Agent SDK use, `claude -p`, and third-party apps still
draw from subscription usage limits. Anthropic's legal guidance says advertised
Pro/Max limits assume ordinary individual Agent SDK use, while developers who
offer a product or route Claude.ai credentials on behalf of other users should
use API-key authentication. This bridge is a personal local workflow; distributing
it as a service would require a new billing/auth decision.

## What the bridge proves

Before the SDK query starts, `src/claude-policy.js`:

- removes explicit API keys, bearer/OAuth tokens, custom base URLs, and
  cloud-provider selectors from the query environment;
- runs `claude auth status` in the same sanitized environment;
- requires `loggedIn: true`, `authMethod: "claude.ai"`,
  `apiProvider: "firstParty"`, and a non-empty subscription type.

The bridge exposes no key, provider, base URL, or paid fallback parameter. SDK
init currently reports `apiKeySource: "none"` for this OAuth session; that is
corroborating evidence only, because it is outside the SDK's declared type
union. The same-environment auth receipt remains the pre-inference owner.

## What the bridge cannot prove

The bridge cannot inspect or change the account-level Usage credits switch. It
does not scan native Claude settings and cannot promise that macOS Keychain,
organization policy, or a future Claude/SDK version has no route Anthropic has
not documented. This is an intentional personal-tool boundary: native settings,
skills, hooks, and MCP integrations remain Claude-owned.

Do not add charge estimation, balance scraping, a budget flag, or a local spend
ledger. None proves that money cannot be charged. Keep the runtime claim narrow:
it removes explicit ambient provider variables, offers no alternate route, and
verifies the observed Claude.ai subscription identity.

## Failure policy

- Explicit API/provider route variables are removed and reported in warnings;
  the query still starts only after the sanitized subscription receipt passes.
- Missing or non-first-party subscription: fail before launching the advisor.
- Expired login: ask the owner to log in again with Claude.ai; never recover
  with an API key.
- Subscription limit: stop and wait for reset. Never switch automatically to a
  paid route.
- Unknown Claude/SDK auth behavior: fail closed and update this owner document,
  focused tests, exact version pin, and live evidence together.
