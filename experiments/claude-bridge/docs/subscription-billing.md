# Subscription Billing Guard

This is maintainer documentation for the runtime guard. Task-time Codex agents
do not need to read it: every managed run enforces the guard before launch.

Official sources:

- https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- https://code.claude.com/docs/en/authentication
- https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans

## What The Bridge Proves

`claude_doctor` and every run execute `claude auth status` after removing all
higher-precedence credential routes. A run starts only when the result has:

- `loggedIn: true`;
- `authMethod: "claude.ai"`;
- `apiProvider: "firstParty"`;
- a non-empty `subscriptionType`.

The runner removes API and bearer credentials, custom base URLs, Bedrock,
Vertex, Foundry, and environment OAuth tokens from direct and tmux children. It
refuses `apiKeyHelper` and auth/provider keys reintroduced through settings.
Removing the environment OAuth token binds the run to this machine's current
`/login` identity rather than an ambient token from an unknown account.

It also removes model-family and subagent alias redirects. Stream-derived model
history remains the final routing evidence because managed or account settings
may still affect resolution.

The report records `billing.mode: subscription_oauth`, auth method,
subscription type, stripped overrides, and helper sources. A successful model
response alone does not prove the billing route.

## What The Bridge Cannot Prove

Claude Code can offer optional API credits after the included plan allocation
is exhausted. That user/account decision is not exposed by `claude auth status`,
so the bridge cannot inspect or disable it.

For strictly subscription-only use:

1. Log in only with the Claude.ai Pro/Max account.
2. Decline API credits when Claude Code offers them.
3. Do not add Console credentials during login.
4. Inspect `/status` near the plan limit and wait for reset.

Do not describe `--max-budget-usd` or a displayed dollar estimate as charge
protection. The credential gate proves the request route; the user's credit
choice governs what happens after the included allocation is exhausted.

## Failure Policy

- Refuse Console/PAYG, cloud, gateway, missing subscription, or
  `apiKeyHelper` before launch and report the exact source.
- On a subscription rate limit, wait for reset unless the user explicitly
  authorizes a different paid route. Never switch automatically.
- On expired login, ask the user to run `/login`; never recover with an API key.
