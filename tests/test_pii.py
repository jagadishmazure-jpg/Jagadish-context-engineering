import logging

import pytest

from ctxeng.offload import Scratch
from ctxeng.pii import get_logger, luhn_ok, mask


@pytest.mark.parametrize(
    "raw,token",
    [
        ("pay with 4111 1111 1111 1111 now", "[CARD]"),
        ("card 5500-0000-0000-0004", "[CARD]"),
        ("mail ops.lead@example.test today", "[EMAIL]"),
        ("call (555) 010-2233", "[PHONE]"),
        ("call +1 555.010.2233", "[PHONE]"),
        ("ssn 123-45-6789", "[SSN]"),
    ],
)
def test_masks(raw, token):
    assert token in mask(raw)


def test_non_luhn_number_not_masked_as_card():
    assert "[CARD]" not in mask("order 1234567890123")


def test_invalid_ssn_area_not_masked():
    assert mask("code 000-12-3456") == "code 000-12-3456"


def test_luhn():
    assert luhn_ok("4111111111111111") and not luhn_ok("4111111111111112")


def test_logger_masks_args_and_exceptions(caplog):
    log = get_logger("ctxeng.test")
    with caplog.at_level(logging.INFO, logger="ctxeng.test"):
        log.info("user %s card %s", "a.b@example.test", "4111111111111111")
        try:
            raise ValueError("bad ssn 123-45-6789")
        except ValueError:
            log.exception("failed")
    text = caplog.text + " ".join(r.getMessage() for r in caplog.records)
    assert "a.b@example.test" not in text and "4111111111111111" not in text
    assert "123-45-6789" not in "".join(r.exc_text or "" for r in caplog.records)


def test_logger_filter_added_once():
    a = get_logger("ctxeng.once")
    get_logger("ctxeng.once")
    assert len(a.filters) == 1


def test_scratch_error_does_not_echo_input(tmp_path):
    with pytest.raises(ValueError) as e:
        Scratch(tmp_path).put("a.b@example.test", "x")
    assert "example.test" not in str(e.value)
