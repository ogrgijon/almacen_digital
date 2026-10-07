import i18n


def test_legal_notice_is_translated():
    i18n.set_language("es")
    notice = i18n.translate("AVISOLEGAL_TEXT")

    assert "AVISO LEGAL" in notice
    assert notice != "AVISOLEGAL_TEXT"
