from unittest.mock import patch

from core.smart.smart_reader import get_physical_drive_number, normalize_drive_letter


def test_normalize_drive_letter_accepts_windows_drive_forms():
    assert normalize_drive_letter("c:") == "C:"
    assert normalize_drive_letter(" D:\\ ") == "D:"


def test_normalize_drive_letter_rejects_command_text():
    assert normalize_drive_letter("C:; whoami") is None
    assert normalize_drive_letter("") is None


@patch("core.smart.smart_reader.subprocess.run")
def test_drive_lookup_uses_argument_list_without_shell(mock_run):
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "7\r\n"

    assert get_physical_drive_number("e:\\") == 7

    command = mock_run.call_args.args[0]
    assert command[0] == "powershell.exe"
    assert command[-1] == "E"
    assert mock_run.call_args.kwargs["shell"] is False
