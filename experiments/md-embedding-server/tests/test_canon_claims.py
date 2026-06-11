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
