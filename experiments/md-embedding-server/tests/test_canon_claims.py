from __future__ import annotations

from navigator.canon.claims import extract_claims, split_into_claims


def test_claims_do_not_split_common_abbreviations_or_backticks() -> None:
    text = "# Правило\n\nСтудия должна нажать `Принять`, см. т.д. только после проверки."

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert "`Принять`" in claims[0].text
    assert "т.д." in claims[0].text


def test_list_items_are_separate_claims() -> None:
    text = "# Критерии\n\n- Заявка должна содержать телефон клиента.\n- Нельзя списывать деньги до Принять.\n"

    claims = split_into_claims(text)

    assert [claim.line for claim in claims] == [3, 4]
    assert "телефон" in claims[0].text
    assert "списывать" in claims[1].text


def test_condition_heading_makes_list_item_claim() -> None:
    text = "# Условия качественной заявки\n\n- закреплена конкретная студия и канал входа;\n"

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert claims[0].text == "закреплена конкретная студия и канал входа;"
    assert "heading:условия" in claims[0].signals


def test_neutral_prose_is_ignored() -> None:
    text = "# Notes\n\nThis paragraph describes a calm observation without rules."

    assert split_into_claims(text) == []


def test_process_dispute_sentence_is_claim_candidate() -> None:
    text = (
        "# Почему мусор не становится платным\n\n"
        "Если заявка не дошла до платного рубежа, она разбирается как спор по строке финансового реестра."
    )

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert "разбирается как спор" in claims[0].text
    assert "process:разбираться" in claims[0].signals


def test_process_verb_without_domain_context_is_ignored() -> None:
    text = "# Notes\n\nКоманда разбирается в макете и обсуждает настроение страницы."

    assert split_into_claims(text) == []


def test_claim_cap_sets_truncated_flag() -> None:
    text = "# Правила\n\n" + "\n".join(
        f"- Заявка должна содержать поле {idx} для проверки." for idx in range(5)
    )

    result = extract_claims(text, max_claims=2)

    assert len(result.claims) == 2
    assert result.truncated is True


def test_callout_title_and_list_items_are_claims() -> None:
    text = (
        "> [!example] Принять заявку можно только после проверки данных.\n"
        "> - Заявка должна содержать телефон клиента.\n"
        "> - Нельзя списывать деньги до Принять.\n"
        "> - Студия должна подтвердить канал входа.\n"
    )

    claims = split_into_claims(text)
    texts = [claim.text for claim in claims]

    assert len(claims) == 4
    assert all(">" not in t and "[!example]" not in t for t in texts)
    assert any("телефон" in t for t in texts)
    assert any("списывать" in t for t in texts)


def test_callout_inner_prose_splits_into_claims() -> None:
    text = (
        "> [!failure] Почему мусор не платный\n"
        "> Если заявка не дошла до рубежа, она разбирается как спор по строке реестра.\n"
        "> Деньги всегда возвращаются по строке финансового реестра.\n"
    )

    claims = split_into_claims(text)

    assert len(claims) == 2
    assert claims[0].text.startswith("Если заявка")
    assert claims[1].text.startswith("Деньги всегда")
    assert "process:разбираться" in claims[0].signals
    assert all(">" not in claim.text for claim in claims)


def test_plain_blockquote_list_items_are_claims() -> None:
    text = (
        "> - Заявка должна содержать телефон клиента.\n"
        "> - Нельзя списывать деньги до Принять.\n"
    )

    claims = split_into_claims(text)

    assert len(claims) == 2
    assert "телефон" in claims[0].text
    assert ">" not in claims[0].text


def test_callout_marker_only_line_yields_no_claim() -> None:
    assert split_into_claims("> [!note]\n") == []


def test_callout_does_not_merge_with_preceding_paragraph() -> None:
    text = (
        "Нейтральное вступление для контекста страницы.\n"
        "> [!warning] Студия должна нажать Принять только после проверки.\n"
    )

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert "Студия должна" in claims[0].text
    assert "вступление" not in claims[0].text


def test_callout_inner_heading_scopes_list_without_leaking() -> None:
    text = (
        "> [!info] Контроль качества\n"
        "> ## Условия качественной заявки\n"
        "> - закреплена конкретная студия и канал входа;\n"
        "\n"
        "Свободный абзац после callout для контекста.\n"
    )

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert claims[0].text == "закреплена конкретная студия и канал входа;"
    assert "heading:условия" in claims[0].signals


def test_callout_table_rows_are_not_claims() -> None:
    text = (
        "> [!info] Тарифы\n"
        "> | поле | значение |\n"
        "> | Заявка должна содержать телефон | да |\n"
    )

    claims = split_into_claims(text)

    assert all("|" not in claim.text for claim in claims)


def test_callout_multiline_prose_is_one_claim() -> None:
    # A sentence wrapped across several `>` lines must stay ONE claim, not be
    # fragmented per physical line. Regression guard for the callout segmenter.
    text = (
        "> [!note] Контекст\n"
        "> Студия обязана подтвердить канал входа\n"
        "> только после ручной проверки заявки клиента.\n"
    )

    claims = split_into_claims(text)

    assert len(claims) == 1
    assert "подтвердить канал входа" in claims[0].text
    assert "ручной проверки" in claims[0].text


def test_callout_list_continuation_matches_main_loop() -> None:
    # A list item wrapped onto a continuation line fragments identically inside
    # a callout and at the top level — the callout introduces no new gap.
    # Merging list continuations is a separate, segmenter-wide concern.
    main = split_into_claims(
        "# H\n\n- Студия должна нажать Принять и открыть\nполный комплект для печати."
    )
    callout = split_into_claims(
        "> [!x] T\n> - Студия должна нажать Принять и открыть\n>   полный комплект для печати."
    )

    assert [c.text for c in main if "должна" in c.text] == [
        c.text for c in callout if "должна" in c.text
    ]
    assert len(callout) >= 1
