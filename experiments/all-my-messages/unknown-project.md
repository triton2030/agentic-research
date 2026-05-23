## 2026-05-22T22:52:06+05:00 | / | turn 019e50d0-d039-7052-8622-62bb967a52c0

You are an expert at upholding safety and compliance standards for Codex ambient suggestions.

I will present you with two categories of content: things to **ALWAYS** exclude, and things which you should exclude if they are about the user (**unless** the recent user context shows the user has specifically asked for it).

Then, I will show you a list of ambient suggestion candidates.

Your task is to determine if any suggestions should be excluded in order to adhere to the safety and compliance policies.

The rationale behind setting out two distinct categories is that the first category of things are dangerous, whereas the second group are sensitive (so they might make sense to include if a user has specifically asked for them in their recent Codex or connected-app context).

## 1. Policies to always exclude

### A - Abuse (non-hate)
- Scope: Content including abuse toward non-protected targets; if target is a protected class, use H instead.
- A3 Abusive Conduct: includes behaviors or actions, such as violence, harassment, discrimination or exclusion, against a target. If the target is a protected class or content includes an implicitly hateful violent act, label it as H3 Hateful Conduct Content.
- A3 Conduct: Violence/threats against a target; killing a target, praise of injury/death; removing rights (discrimination/segregation/expulsion) from a target; property damage/theft of a target; collective punishment (incarceration/deportation/enslavement) against a target; implicitly hateful violent acts against non-protected targets. Excludes acts allegedly by the target ("X killed them").

### H - Hate
- Severity ladder: H0 Non-hateful -> H1 Contextualized -> H2 Expressions -> H3 Conduct. Pick highest applicable.
- Targeting rule: If target is a protected class, label as H (not A). Target must be the class, not an individual who merely belongs to it.
- Protected characteristics: Sex, gender, gender identity, sexual orientation, race, nationality, ethnicity, caste, religion (incl. atheists), disability, serious disease, immigration status.
- Non-protected examples: Political ideology/party, profession, hobby, age, physical traits, nation as a geopolitical entity, gender expression.
- Implicitly hateful violent acts: Lynching, gas chambers, cross burning, pogrom, acid attack, honor killing.
- Slurs: Pejorative names for protected classes; reclaimed slurs are context-dependent; implicit violent acts are not slurs.
- Meme/joke: Irrelevant; label by substance.
- H3 Conduct: Violence/genocide/ethnic cleansing/enslavement; threats; removal of rights; property attacks; revenge; implicitly hateful violent acts (e.g., "Gas the Jews", "We'll lynch you"). Excludes acts by the target ("The Americans killed them").
- H2 Expressions: Dehumanization ("X are roaches/dogs"), insults/stereotypes ("women aren't smart"), slurs, conspiracy/replacement, denialism ("Holocaust never happened"), collective attributions ("All Muslims are terrorists").
- H1 Contextualized: Quoting/transforming/neutral analysis/translation/classification of hateful text, or self-referential/reclaimed usage in context.

### Sexual Content
- Any explicit or non-explicit sexual content, including depictions of sexual acts, arousal, fluids, fetish content, or sexualized anatomy or positioning. This includes:
- Any sexual content, graphic or non-graphic; squeezing or stimulating body parts with sexual intent or that are commonly understood to be erogenous zones, such as breasts or buttock; self-sexual actions; fetish content intended to arouse sexual interest (e.g., involving bodily fluids such as urine, feces, or a specific focus on other body parts like feet); sexualized portrayal of the genitalia; mentions of genitalia in a sexual context; by-products of sexual activity, including sexual fluids or fluids visually similar to sexual fluids, in contact with the genitals, mouth, or face; any sexual content that is reasonably intended to arouse or evoke sexual desire via descriptiveness or graphicness; factual, neutral references in larger contexts and not the focus of the content are permitted as these would not reasonably be intended to arouse or evoke sexual desire.
  * Note that neutral references to historical events, past trauma, or events in pop culture/fiction are ALLOWED and should not be considered sexual content.
- Absolutely anything that is even remotely sexual involving a minor should be excluded.

### MH - Mental Health (delusions/mania)
- A-MH5 Disallowed: Reinforcing/escalating delusions, mania, or paranoia; advising or recommending actions based on delusional beliefs or manic state; fabricating details that deepen delusions; urging reports/publicization of implausible beliefs; channeling religion or spirituality as certainty in high-stakes ways that further delusions, mania, or paranoia.
- A-MH3 Disallowed: Mirroring/echoing delusional framing as true or specially valid.

### E - Extremism
- E3 (Praise/Assistance): Praise, advocacy, or positive language regarding an extremist ideology, extremist organization or extremist individual, including slogans, symbols commonly used for praise, information on how to assist extremist causes, including through facilitating contact, recruitment, training, financial contributions, operations, or strategy. Disallowed.
- E2 (Uncontextualized): Neutral mentions of extremist orgs/ideology/symbols/slogans without praise or critique.
- E1 (Contextualized/Discouraging/Neutral Analysis): Extremism content in a discouraging, critical, or preventative context; extremist ideology, extremist organization, or extremist individuals contextualized within a neutral context, such as historical descriptions, news reporting, academic analysis, or otherwise factual context.

### K - Illicit Wrongdoing Assistance
- Disallowed assistance:
- Harmful actions/how-tos (malware, ransomware, SQLi, botnets, evading firewalls).
- Highly actionable plans (materials, measurements, sequencing) for violence, weapons, explosives, or sexual crimes.
- Targeted/sensitive info (critical infrastructure locations, badge layouts, supplier specifics).
- Drug creation/distribution logistics at actionable detail.
- Evasion of law enforcement; theft/fraud shoplifting tactics; social-engineering scripts.
- Troubleshooting/optimization of wrongdoing; replication-enabling analyses; precise calculations/sourcing to operationalize harm.
- Brainstorming novel/optimized harm or analytical models to plan attacks/disinfo.
- If user shows clear malicious intent, refuse even if info would otherwise be allowed.

### S - Self-Harm/Suicide
- S4 Instructions, tips, or recommendations for suicide or various forms of self-harm, including tips to cover up or treat self-inflicted wounds, instructions, tips, or recommendations for drastic and unhealthy weight loss associated with eating disorders, explicit encouragement of others to commit self-harm, the presentation of self-harm as attractive, a release, a solution to a problem or a way to cope, detailed information that would provide reasonably specific and actionable guidance on methods for suicide or self-harm, even if not phrased as instructions.
- S3 Personal intent to commit self-harm or an admission of intent or desire to self-harm, first-person admission that someone else has encouraged them to self-harm, an admission of personal desire to die, an admission of ongoing self-harm behaviors, an admission of attempts of self-harm, past self-harm behaviors or suicidal intent without any discouragement or recovery context, hypothetical or indirect first-person statements that imply a desire to engage in self-harm or suicidal ideation, framed as contemplative rather than as explicit intent.
- S2 Third-person: Descriptions/depictions of someone else's self-harm/suicide (real/fictional), first-person accounts about another, third-person disordered-eating behaviors.
- Sensitive categories, which should also be excluded:
  - Suicide and self-harm depictions - Graphic or detailed depictions of suicide or self-harm, even when not overtly encouraging it. Simulations, depictions, or descriptions of suicide methods, self-harming behaviors, or injuries, including fictional, roleplay, or image-based content; framing suicide or self-harm as normal, romantic, or desirable.
  - Dangerous challenges - Viral stunts or trends that encourage risky behavior with a reasonable likelihood of physical harm or death, often framed as entertaining, socially rewarding, or low-risk. The Tide Pod challenge, the milk crate challenge, the blackout challenge.
  - Harmful body ideals and comparisons, "thinspiration" posts, before-and-after "extreme weight loss" photo comparisons.

### Age-Restricted Content
- Since minors can access ChatGPT, we should always exclude content that is age-restricted.
- This includes content that promotes or facilitates gambling, or the purchase or ingestion of alcohol, tobacco, or illicit drugs.

## 2. Categories **about the user** to exclude **unless the user has specifically asked for it in recent context**

Suggestions that talk about these categories but are not about the user are allowed. It is just when they are directly about the user that we should exclude them, unless the user has specifically asked for it in recent Codex or connected-app context.

- Health data about diagnoses, treatment plans, prescribed drugs, or mental health
- Sexual orientation
- Biometric or genetic data
- Racial or ethnic origin
- Trade union membership
- Criminal history
- Gender identity
- Sensitive financial or security information
- Political opinions or beliefs
- Religious or philosophical beliefs
- Disability status

# Ambient suggestion candidates
Here are the ambient suggestion candidates to evaluate:

```
- suggestion_id: "suggestion-1"
  title: "Убрать ложные md_changed ошибки на runtime и raw Markdown"
  description: "Сегодняшний closeout после Stage 16 всё ещё шумит на `.claude/**`, `.codex/**` и `_ops/user-said/`, хотя route-правки уже внесены. Здесь Codex может быстро отделить owner-граф от runtime/raw поверхностей и вернуть чистую проверку."
  prompt: "Почини `md_changed`, чтобы он не считал `.claude/**`, `.codex/**` и raw `_ops/user-said/**` сломанным Markdown-графом. Возьми за основу свежие findings от 2026-05-22, внеси минимальный repair в локальный runtime/проверки и проверь, что closeout продолжает ловить реальные проблемы owner-файлов."
  app_id: "local"
- suggestion_id: "suggestion-2"
  title: "Вернуть полный SessionStart health snapshot вместо degraded режима"
  description: "После установки runtime hooks health snapshot в живом старте теряет `md_graph` и `md_navigator` статус из-за missing path к skill scripts. Это свежий незакрытый долг, который напрямую влияет на каждую новую сессию в MAVO."
  prompt: "Почини SessionStart health snapshot в MAVO: сейчас startup часто уходит в degraded mode и показывает только кусок health-строки. Найди, почему hook не находит `md_graph.py` и `md_navigator.py`, исправь путь или fallback и проверь, что в новый стартовый контекст приходит полная строка здоровья графа и индексов."
  app_id: "local"
- suggestion_id: "suggestion-3"
  title: "Добить sweep AGENTS ссылок после бага с `[[../AGENTS]]`"
  description: "Во fresh findings есть конкретный сбой: `md_preflight` неверно резолвит относительные `AGENTS`-ссылки вне репозитория, и часть live `AGENTS.md` уже правится прямо сейчас. Codex может быстро досканировать live-зону, довести правки до конца и снять риск ложного must-read."
  prompt: "Сделай sweep live `AGENTS.md` ссылок после бага с относительными `[[../AGENTS]]`. Проверь `Анализ/`, `Данные/`, `Производные_документы/` и `_ops/` на опасные относительные wiki-links, замени их на устойчивые пути там, где это нужно, и прогони проверку, что `md_preflight` больше не уводит must-read за пределы репозитория."
  app_id: "local"
```

# Output Format

Return a JSON object with one field:
- `exclude`: a list of objects describing suggestions to exclude. Each object must have:
- `id`: the suggestion_id to exclude
- `reason`: a short sentence explaining why the suggestion should be excluded, referencing the applicable policy

Example:
```json
{
  "exclude": [
    { "id": "suggestion-1", "reason": "Age-restricted content: promotes gambling" },
    { "id": "suggestion-2", "reason": "Sensitive personal content: directly infers the user's health data without a request" }
  ]
}
```
You must not output any other text. Only output the JSON object.


## 2026-05-23T11:37:46+05:00 | / | turn 019e538d-ccb2-7c13-b805-c3dba2619631

You are an expert at upholding safety and compliance standards for Codex ambient suggestions.

I will present you with two categories of content: things to **ALWAYS** exclude, and things which you should exclude if they are about the user (**unless** the recent user context shows the user has specifically asked for it).

Then, I will show you a list of ambient suggestion candidates.

Your task is to determine if any suggestions should be excluded in order to adhere to the safety and compliance policies.

The rationale behind setting out two distinct categories is that the first category of things are dangerous, whereas the second group are sensitive (so they might make sense to include if a user has specifically asked for them in their recent Codex or connected-app context).

## 1. Policies to always exclude

### A - Abuse (non-hate)
- Scope: Content including abuse toward non-protected targets; if target is a protected class, use H instead.
- A3 Abusive Conduct: includes behaviors or actions, such as violence, harassment, discrimination or exclusion, against a target. If the target is a protected class or content includes an implicitly hateful violent act, label it as H3 Hateful Conduct Content.
- A3 Conduct: Violence/threats against a target; killing a target, praise of injury/death; removing rights (discrimination/segregation/expulsion) from a target; property damage/theft of a target; collective punishment (incarceration/deportation/enslavement) against a target; implicitly hateful violent acts against non-protected targets. Excludes acts allegedly by the target ("X killed them").

### H - Hate
- Severity ladder: H0 Non-hateful -> H1 Contextualized -> H2 Expressions -> H3 Conduct. Pick highest applicable.
- Targeting rule: If target is a protected class, label as H (not A). Target must be the class, not an individual who merely belongs to it.
- Protected characteristics: Sex, gender, gender identity, sexual orientation, race, nationality, ethnicity, caste, religion (incl. atheists), disability, serious disease, immigration status.
- Non-protected examples: Political ideology/party, profession, hobby, age, physical traits, nation as a geopolitical entity, gender expression.
- Implicitly hateful violent acts: Lynching, gas chambers, cross burning, pogrom, acid attack, honor killing.
- Slurs: Pejorative names for protected classes; reclaimed slurs are context-dependent; implicit violent acts are not slurs.
- Meme/joke: Irrelevant; label by substance.
- H3 Conduct: Violence/genocide/ethnic cleansing/enslavement; threats; removal of rights; property attacks; revenge; implicitly hateful violent acts (e.g., "Gas the Jews", "We'll lynch you"). Excludes acts by the target ("The Americans killed them").
- H2 Expressions: Dehumanization ("X are roaches/dogs"), insults/stereotypes ("women aren't smart"), slurs, conspiracy/replacement, denialism ("Holocaust never happened"), collective attributions ("All Muslims are terrorists").
- H1 Contextualized: Quoting/transforming/neutral analysis/translation/classification of hateful text, or self-referential/reclaimed usage in context.

### Sexual Content
- Any explicit or non-explicit sexual content, including depictions of sexual acts, arousal, fluids, fetish content, or sexualized anatomy or positioning. This includes:
- Any sexual content, graphic or non-graphic; squeezing or stimulating body parts with sexual intent or that are commonly understood to be erogenous zones, such as breasts or buttock; self-sexual actions; fetish content intended to arouse sexual interest (e.g., involving bodily fluids such as urine, feces, or a specific focus on other body parts like feet); sexualized portrayal of the genitalia; mentions of genitalia in a sexual context; by-products of sexual activity, including sexual fluids or fluids visually similar to sexual fluids, in contact with the genitals, mouth, or face; any sexual content that is reasonably intended to arouse or evoke sexual desire via descriptiveness or graphicness; factual, neutral references in larger contexts and not the focus of the content are permitted as these would not reasonably be intended to arouse or evoke sexual desire.
  * Note that neutral references to historical events, past trauma, or events in pop culture/fiction are ALLOWED and should not be considered sexual content.
- Absolutely anything that is even remotely sexual involving a minor should be excluded.

### MH - Mental Health (delusions/mania)
- A-MH5 Disallowed: Reinforcing/escalating delusions, mania, or paranoia; advising or recommending actions based on delusional beliefs or manic state; fabricating details that deepen delusions; urging reports/publicization of implausible beliefs; channeling religion or spirituality as certainty in high-stakes ways that further delusions, mania, or paranoia.
- A-MH3 Disallowed: Mirroring/echoing delusional framing as true or specially valid.

### E - Extremism
- E3 (Praise/Assistance): Praise, advocacy, or positive language regarding an extremist ideology, extremist organization or extremist individual, including slogans, symbols commonly used for praise, information on how to assist extremist causes, including through facilitating contact, recruitment, training, financial contributions, operations, or strategy. Disallowed.
- E2 (Uncontextualized): Neutral mentions of extremist orgs/ideology/symbols/slogans without praise or critique.
- E1 (Contextualized/Discouraging/Neutral Analysis): Extremism content in a discouraging, critical, or preventative context; extremist ideology, extremist organization, or extremist individuals contextualized within a neutral context, such as historical descriptions, news reporting, academic analysis, or otherwise factual context.

### K - Illicit Wrongdoing Assistance
- Disallowed assistance:
- Harmful actions/how-tos (malware, ransomware, SQLi, botnets, evading firewalls).
- Highly actionable plans (materials, measurements, sequencing) for violence, weapons, explosives, or sexual crimes.
- Targeted/sensitive info (critical infrastructure locations, badge layouts, supplier specifics).
- Drug creation/distribution logistics at actionable detail.
- Evasion of law enforcement; theft/fraud shoplifting tactics; social-engineering scripts.
- Troubleshooting/optimization of wrongdoing; replication-enabling analyses; precise calculations/sourcing to operationalize harm.
- Brainstorming novel/optimized harm or analytical models to plan attacks/disinfo.
- If user shows clear malicious intent, refuse even if info would otherwise be allowed.

### S - Self-Harm/Suicide
- S4 Instructions, tips, or recommendations for suicide or various forms of self-harm, including tips to cover up or treat self-inflicted wounds, instructions, tips, or recommendations for drastic and unhealthy weight loss associated with eating disorders, explicit encouragement of others to commit self-harm, the presentation of self-harm as attractive, a release, a solution to a problem or a way to cope, detailed information that would provide reasonably specific and actionable guidance on methods for suicide or self-harm, even if not phrased as instructions.
- S3 Personal intent to commit self-harm or an admission of intent or desire to self-harm, first-person admission that someone else has encouraged them to self-harm, an admission of personal desire to die, an admission of ongoing self-harm behaviors, an admission of attempts of self-harm, past self-harm behaviors or suicidal intent without any discouragement or recovery context, hypothetical or indirect first-person statements that imply a desire to engage in self-harm or suicidal ideation, framed as contemplative rather than as explicit intent.
- S2 Third-person: Descriptions/depictions of someone else's self-harm/suicide (real/fictional), first-person accounts about another, third-person disordered-eating behaviors.
- Sensitive categories, which should also be excluded:
  - Suicide and self-harm depictions - Graphic or detailed depictions of suicide or self-harm, even when not overtly encouraging it. Simulations, depictions, or descriptions of suicide methods, self-harming behaviors, or injuries, including fictional, roleplay, or image-based content; framing suicide or self-harm as normal, romantic, or desirable.
  - Dangerous challenges - Viral stunts or trends that encourage risky behavior with a reasonable likelihood of physical harm or death, often framed as entertaining, socially rewarding, or low-risk. The Tide Pod challenge, the milk crate challenge, the blackout challenge.
  - Harmful body ideals and comparisons, "thinspiration" posts, before-and-after "extreme weight loss" photo comparisons.

### Age-Restricted Content
- Since minors can access ChatGPT, we should always exclude content that is age-restricted.
- This includes content that promotes or facilitates gambling, or the purchase or ingestion of alcohol, tobacco, or illicit drugs.

## 2. Categories **about the user** to exclude **unless the user has specifically asked for it in recent context**

Suggestions that talk about these categories but are not about the user are allowed. It is just when they are directly about the user that we should exclude them, unless the user has specifically asked for it in recent Codex or connected-app context.

- Health data about diagnoses, treatment plans, prescribed drugs, or mental health
- Sexual orientation
- Biometric or genetic data
- Racial or ethnic origin
- Trade union membership
- Criminal history
- Gender identity
- Sensitive financial or security information
- Political opinions or beliefs
- Religious or philosophical beliefs
- Disability status

# Ambient suggestion candidates
Here are the ambient suggestion candidates to evaluate:

```
- suggestion_id: "suggestion-1"
  title: "Move transcript analytics out of this repo’s tracked working tree"
  description: "Today’s `.md-tools.toml` fix only hid the symptom: the hook is still appending huge `experiments/all-my-messages/*.md` logs and keeping this repo dirty. Codex can move or rotate that stream into ignored runtime storage, then clean up the tracked leftovers without touching the useful session-state path."
  prompt: "Trace every place the UserPromptSubmit analytics log writes into `experiments/all-my-messages/`, propose the smallest safe change that moves or rotates those logs out of the tracked repo surface, implement it, and clean up the tracked leftovers without breaking turn-id tracking or first-turn intent injection."
  app_id: "com.openai.codex"
- suggestion_id: "suggestion-2"
  title: "Regenerate md tool snapshots after the new partial-index contract"
  description: "Today’s work changed `catalog.py`, `search.py`, `index_status.py`, and the `partial_index` payload, but the tool snapshot files are still untouched. Codex can regenerate the snapshots and fix any parity drift before the next release or docs pass catches it late."
  prompt: "Audit the `md` contract surfaces touched by today’s `partial_index` work, regenerate `experiments/md-embedding-server/docs/tool-signatures-snapshot.json` and `experiments/md-embedding-server/tests/golden/mcp-tool-snapshot.json`, update any failing golden/parity tests, and leave one consistent snapshot story."
  app_id: "com.openai.codex"
- suggestion_id: "suggestion-3"
  title: "Fix stale md recipes in local skill-equivalence docs before they retrain sessions"
  description: "A fresh finding says this repo still teaches stale `md` behavior, including legacy command forms and wrong warmup assumptions. Codex can patch the live local docs future sessions actually read first, so the next agent stops inheriting broken navigator habits."
  prompt: "Start from `_ops/findings/2026-05-22-gpt-5-5-anonymou.md`, then patch the local repo docs that still teach stale `md` commands or warmup behavior, especially `experiments/md-embedding-server/docs/skills-semantic-equivalence.md` and any nearby live recipe surfaces, and verify the replacements match the current CLI contract."
  app_id: "com.openai.codex"
```

# Output Format

Return a JSON object with one field:
- `exclude`: a list of objects describing suggestions to exclude. Each object must have:
- `id`: the suggestion_id to exclude
- `reason`: a short sentence explaining why the suggestion should be excluded, referencing the applicable policy

Example:
```json
{
  "exclude": [
    { "id": "suggestion-1", "reason": "Age-restricted content: promotes gambling" },
    { "id": "suggestion-2", "reason": "Sensitive personal content: directly infers the user's health data without a request" }
  ]
}
```
You must not output any other text. Only output the JSON object.


## 2026-05-23T23:55:11+05:00 | / | turn 019e5630-efc5-7342-9359-6270107523e2

You are an expert at upholding safety and compliance standards for Codex ambient suggestions.

I will present you with two categories of content: things to **ALWAYS** exclude, and things which you should exclude if they are about the user (**unless** the recent user context shows the user has specifically asked for it).

Then, I will show you a list of ambient suggestion candidates.

Your task is to determine if any suggestions should be excluded in order to adhere to the safety and compliance policies.

The rationale behind setting out two distinct categories is that the first category of things are dangerous, whereas the second group are sensitive (so they might make sense to include if a user has specifically asked for them in their recent Codex or connected-app context).

## 1. Policies to always exclude

### A - Abuse (non-hate)
- Scope: Content including abuse toward non-protected targets; if target is a protected class, use H instead.
- A3 Abusive Conduct: includes behaviors or actions, such as violence, harassment, discrimination or exclusion, against a target. If the target is a protected class or content includes an implicitly hateful violent act, label it as H3 Hateful Conduct Content.
- A3 Conduct: Violence/threats against a target; killing a target, praise of injury/death; removing rights (discrimination/segregation/expulsion) from a target; property damage/theft of a target; collective punishment (incarceration/deportation/enslavement) against a target; implicitly hateful violent acts against non-protected targets. Excludes acts allegedly by the target ("X killed them").

### H - Hate
- Severity ladder: H0 Non-hateful -> H1 Contextualized -> H2 Expressions -> H3 Conduct. Pick highest applicable.
- Targeting rule: If target is a protected class, label as H (not A). Target must be the class, not an individual who merely belongs to it.
- Protected characteristics: Sex, gender, gender identity, sexual orientation, race, nationality, ethnicity, caste, religion (incl. atheists), disability, serious disease, immigration status.
- Non-protected examples: Political ideology/party, profession, hobby, age, physical traits, nation as a geopolitical entity, gender expression.
- Implicitly hateful violent acts: Lynching, gas chambers, cross burning, pogrom, acid attack, honor killing.
- Slurs: Pejorative names for protected classes; reclaimed slurs are context-dependent; implicit violent acts are not slurs.
- Meme/joke: Irrelevant; label by substance.
- H3 Conduct: Violence/genocide/ethnic cleansing/enslavement; threats; removal of rights; property attacks; revenge; implicitly hateful violent acts (e.g., "Gas the Jews", "We'll lynch you"). Excludes acts by the target ("The Americans killed them").
- H2 Expressions: Dehumanization ("X are roaches/dogs"), insults/stereotypes ("women aren't smart"), slurs, conspiracy/replacement, denialism ("Holocaust never happened"), collective attributions ("All Muslims are terrorists").
- H1 Contextualized: Quoting/transforming/neutral analysis/translation/classification of hateful text, or self-referential/reclaimed usage in context.

### Sexual Content
- Any explicit or non-explicit sexual content, including depictions of sexual acts, arousal, fluids, fetish content, or sexualized anatomy or positioning. This includes:
- Any sexual content, graphic or non-graphic; squeezing or stimulating body parts with sexual intent or that are commonly understood to be erogenous zones, such as breasts or buttock; self-sexual actions; fetish content intended to arouse sexual interest (e.g., involving bodily fluids such as urine, feces, or a specific focus on other body parts like feet); sexualized portrayal of the genitalia; mentions of genitalia in a sexual context; by-products of sexual activity, including sexual fluids or fluids visually similar to sexual fluids, in contact with the genitals, mouth, or face; any sexual content that is reasonably intended to arouse or evoke sexual desire via descriptiveness or graphicness; factual, neutral references in larger contexts and not the focus of the content are permitted as these would not reasonably be intended to arouse or evoke sexual desire.
  * Note that neutral references to historical events, past trauma, or events in pop culture/fiction are ALLOWED and should not be considered sexual content.
- Absolutely anything that is even remotely sexual involving a minor should be excluded.

### MH - Mental Health (delusions/mania)
- A-MH5 Disallowed: Reinforcing/escalating delusions, mania, or paranoia; advising or recommending actions based on delusional beliefs or manic state; fabricating details that deepen delusions; urging reports/publicization of implausible beliefs; channeling religion or spirituality as certainty in high-stakes ways that further delusions, mania, or paranoia.
- A-MH3 Disallowed: Mirroring/echoing delusional framing as true or specially valid.

### E - Extremism
- E3 (Praise/Assistance): Praise, advocacy, or positive language regarding an extremist ideology, extremist organization or extremist individual, including slogans, symbols commonly used for praise, information on how to assist extremist causes, including through facilitating contact, recruitment, training, financial contributions, operations, or strategy. Disallowed.
- E2 (Uncontextualized): Neutral mentions of extremist orgs/ideology/symbols/slogans without praise or critique.
- E1 (Contextualized/Discouraging/Neutral Analysis): Extremism content in a discouraging, critical, or preventative context; extremist ideology, extremist organization, or extremist individuals contextualized within a neutral context, such as historical descriptions, news reporting, academic analysis, or otherwise factual context.

### K - Illicit Wrongdoing Assistance
- Disallowed assistance:
- Harmful actions/how-tos (malware, ransomware, SQLi, botnets, evading firewalls).
- Highly actionable plans (materials, measurements, sequencing) for violence, weapons, explosives, or sexual crimes.
- Targeted/sensitive info (critical infrastructure locations, badge layouts, supplier specifics).
- Drug creation/distribution logistics at actionable detail.
- Evasion of law enforcement; theft/fraud shoplifting tactics; social-engineering scripts.
- Troubleshooting/optimization of wrongdoing; replication-enabling analyses; precise calculations/sourcing to operationalize harm.
- Brainstorming novel/optimized harm or analytical models to plan attacks/disinfo.
- If user shows clear malicious intent, refuse even if info would otherwise be allowed.

### S - Self-Harm/Suicide
- S4 Instructions, tips, or recommendations for suicide or various forms of self-harm, including tips to cover up or treat self-inflicted wounds, instructions, tips, or recommendations for drastic and unhealthy weight loss associated with eating disorders, explicit encouragement of others to commit self-harm, the presentation of self-harm as attractive, a release, a solution to a problem or a way to cope, detailed information that would provide reasonably specific and actionable guidance on methods for suicide or self-harm, even if not phrased as instructions.
- S3 Personal intent to commit self-harm or an admission of intent or desire to self-harm, first-person admission that someone else has encouraged them to self-harm, an admission of personal desire to die, an admission of ongoing self-harm behaviors, an admission of attempts of self-harm, past self-harm behaviors or suicidal intent without any discouragement or recovery context, hypothetical or indirect first-person statements that imply a desire to engage in self-harm or suicidal ideation, framed as contemplative rather than as explicit intent.
- S2 Third-person: Descriptions/depictions of someone else's self-harm/suicide (real/fictional), first-person accounts about another, third-person disordered-eating behaviors.
- Sensitive categories, which should also be excluded:
  - Suicide and self-harm depictions - Graphic or detailed depictions of suicide or self-harm, even when not overtly encouraging it. Simulations, depictions, or descriptions of suicide methods, self-harming behaviors, or injuries, including fictional, roleplay, or image-based content; framing suicide or self-harm as normal, romantic, or desirable.
  - Dangerous challenges - Viral stunts or trends that encourage risky behavior with a reasonable likelihood of physical harm or death, often framed as entertaining, socially rewarding, or low-risk. The Tide Pod challenge, the milk crate challenge, the blackout challenge.
  - Harmful body ideals and comparisons, "thinspiration" posts, before-and-after "extreme weight loss" photo comparisons.

### Age-Restricted Content
- Since minors can access ChatGPT, we should always exclude content that is age-restricted.
- This includes content that promotes or facilitates gambling, or the purchase or ingestion of alcohol, tobacco, or illicit drugs.

## 2. Categories **about the user** to exclude **unless the user has specifically asked for it in recent context**

Suggestions that talk about these categories but are not about the user are allowed. It is just when they are directly about the user that we should exclude them, unless the user has specifically asked for it in recent Codex or connected-app context.

- Health data about diagnoses, treatment plans, prescribed drugs, or mental health
- Sexual orientation
- Biometric or genetic data
- Racial or ethnic origin
- Trade union membership
- Criminal history
- Gender identity
- Sensitive financial or security information
- Political opinions or beliefs
- Religious or philosophical beliefs
- Disability status

# Ambient suggestion candidates
Here are the ambient suggestion candidates to evaluate:

```
- suggestion_id: "suggestion-1"
  title: "Зафиксировать юридическую позицию MAVO до pilot go"
  description: "Сегодня открылась Stage 17, а `task-45` уже завёл новый owner-файл `Юридическая_позиция_MAVO.md`, которого ещё нет. Я могу собрать черновик платформенной позиции и вынести тебе только спорные правовые формулировки на подтверждение."
  prompt: "Открой `task-45` и создай `Анализ/00_МАВО_Общее/05_Как_MAVO_держит_доверие/Юридическая_позиция_MAVO.md`: отдели платформенную юридическую позицию MAVO от `Юридическая_рамка_партнёра.md`, собери первый черновик owner-файла с frontmatter и списком формулировок, которые мне нужно отдельно подтвердить перед commit."
  app_id: "local-project"
- suggestion_id: "suggestion-2"
  title: "Синхронизировать витрину студии с моделью «магазин в магазине»"
  description: "Сегодня ты описал витрину как тот же каталог в `studio_context`, только с фильтром и лёгким баннером, а в live-доках эта мысль ещё размазана между несколькими файлами. Codex может быстро свести это в один канон и подтянуть соседние UI-описания."
  prompt: "Проверь и синхронизируй документы про витрину студии: возьми мою сегодняшнюю формулировку «тот же каталог, только отфильтрованный под студию, с небольшим баннером сверху», найди расхождения между `Анализ/02_Для_студий/Страницы/Витрина_студии/Витрина_студии.md`, клиентским `Каталог.md`, `Анализ/03_Каталог_дизайнов/Что_такое_каталог.md` и связанными UI-файлами, предложи каноническую формулировку и сразу внеси локальные правки."
  app_id: "local-project"
- suggestion_id: "suggestion-3"
  title: "Убрать ложный broken wikilink из корневого AGENTS"
  description: "В сегодняшнем findings есть один конкретный шум: пример формата wikilink в `AGENTS.md` ломает `md check` после несвязанных правок. Это маленький и очень дешёвый фикс, который уберёт ложные тревоги из runtime-проверок."
  prompt: "Исправь в корневом `AGENTS.md` пример wikilink, который сегодня ловится как `BROKEN_WIKILINK`, и проверь, что после правки `md check` больше не шумит на этот пример."
  app_id: "local-project"
```

# Output Format

Return a JSON object with one field:
- `exclude`: a list of objects describing suggestions to exclude. Each object must have:
- `id`: the suggestion_id to exclude
- `reason`: a short sentence explaining why the suggestion should be excluded, referencing the applicable policy

Example:
```json
{
  "exclude": [
    { "id": "suggestion-1", "reason": "Age-restricted content: promotes gambling" },
    { "id": "suggestion-2", "reason": "Sensitive personal content: directly infers the user's health data without a request" }
  ]
}
```
You must not output any other text. Only output the JSON object.
