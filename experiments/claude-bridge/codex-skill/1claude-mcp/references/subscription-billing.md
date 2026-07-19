# Subscription Billing Guard

Use this reference before any live Claude run. The bridge is intentionally
subscription-only; it must never choose Claude Console, an API key, a gateway,
or a cloud provider as a silent fallback.

Official sources:

- https://support.claude.com/en/articles/11145838-use-claude-code-with-your-pro-or-max-plan
- https://code.claude.com/docs/en/authentication
- https://support.claude.com/en/articles/12429409-manage-usage-credits-for-paid-claude-plans

## What The Bridge Proves

`claude_doctor` and every run execute `claude auth status` after removing all
higher-precedence credential routes. A run starts only when the result has:

- `loggedIn: true`;
- `authMethod: "claude.ai"`;
- `apiProvider: "firstParty"` (not a signed-in gateway provider);
- a non-empty `subscriptionType`.

The runner removes API and bearer credentials, custom base URLs, Bedrock,
Vertex, Foundry, and environment OAuth tokens from both direct and tmux child
environments. It refuses any detected `apiKeyHelper` in user, project, managed,
or explicit settings. It also refuses the same auth/provider keys when settings
would reintroduce them through an `env` block. Removing the environment OAuth
token intentionally binds the run to this machine's current `/login` identity
rather than an ambient token owned by an unknown account.

It also removes model-family and subagent alias redirects so ambient shell state
cannot silently pin `opus`, `fable`, or Claude subagents to another model, and
refuses equivalent redirects found in settings. The
stream-derived model history remains the final routing evidence because managed
or account settings may still affect resolution.

The run report records `billing.mode: subscription_oauth`, auth method,
subscription type, stripped override names, and helper sources. Never infer the
billing route only from a successful model response.

## What The Bridge Cannot Prove

Claude Code can offer optional API credits after the included plan allocation
is exhausted. That user/account decision is not exposed by `claude auth status`,
so the bridge cannot inspect or disable it.

For strictly subscription-only use:

1. log in only with the Claude.ai Pro/Max account;
2. decline API credits when Claude Code offers them;
3. do not add Console credentials during login;
4. inspect `/status` when nearing the plan limit and wait for reset.

Do not describe `--max-budget-usd` or a displayed dollar estimate as protection
from charges. The credential gate proves the request route; the user's credit
choice governs what happens after the included allocation is exhausted.

## Failure Policy

- Console/PAYG, cloud, gateway, missing subscription, or `apiKeyHelper`: refuse
  before launch and explain the exact source.
- Subscription rate limit: wait for reset unless the user explicitly authorizes
  a different paid route. Never switch automatically.
- Expired login: ask the user to run `/login`; do not use an API key as recovery.
