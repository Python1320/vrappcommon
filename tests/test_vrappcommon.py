import sys
from unittest.mock import MagicMock, call, patch

import pytest

from vrappcommon import jankyguihelpers, utils


def test_oscfloat_int():
    assert utils.oscfloat([42]) == 42.0
    assert utils.oscfloat([0]) == 0.0
    assert utils.oscfloat([-1]) == -1.0


def test_oscfloat_float():
    assert utils.oscfloat([3.14]) == 3.14
    assert utils.oscfloat([0.0]) == 0.0


def test_oscfloat_bool():
    assert utils.oscfloat([True]) == 1.0
    assert utils.oscfloat([False]) == 0.0


def test_oscfloat_nested_list():
    assert utils.oscfloat([[42]]) == 42.0
    assert utils.oscfloat([(3.14,)]) == 3.14


def test_oscfloat_str():
    assert utils.oscfloat(["42.5"]) == 42.5


def test_oscfloat_str_fail():
    with pytest.raises(ValueError, match="cannot convert string 'abc' to a float"):
        utils.oscfloat(["abc"])


def test_oscfloat_invalid_type():
    with pytest.raises(ValueError):
        utils.oscfloat([None])


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific ctypes call")
@patch("ctypes.windll.kernel32.SetConsoleTitleW", autospec=True)
def test_set_console_title_windows(mock_set_title):
    with patch("vrappcommon.jankyguihelpers.PROGRAMNAME", "TestApp"):
        jankyguihelpers.set_console_title("My Title")
        mock_set_title.assert_called_once_with("My Title")


@pytest.mark.skipif(sys.platform == "win32", reason="ANSI escape on non-Windows")
@patch("builtins.print")
def test_set_console_title_unix(mock_print):
    jankyguihelpers.set_console_title("My Title")
    mock_print.assert_called_once_with("\x1b]0;My Title\x07", end="", flush=True)


@pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific")
@patch("ctypes.windll.kernel32.SetConsoleTitleW", autospec=True)
def test_set_console_title_fallsback_to_programname(mock_set_title):
    with patch("vrappcommon.jankyguihelpers.PROGRAMNAME", "FallbackApp"):
        jankyguihelpers.set_console_title("")
        mock_set_title.assert_called_once_with("FallbackApp")


@patch("vrappcommon.jankyguihelpers.os._exit")
@patch("vrappcommon.jankyguihelpers.TopErrorWindow")
@patch("vrappcommon.jankyguihelpers.logging")
def test_fatal_calls_exit(mock_logging, mock_window, mock_exit):
    jankyguihelpers.fatal("test error", detail="some detail")
    mock_exit.assert_called_once_with(1)


@patch("vrappcommon.jankyguihelpers.os._exit")
@patch("vrappcommon.jankyguihelpers.TopErrorWindow")
@patch("vrappcommon.jankyguihelpers.logging")
def test_fatal_creates_error_window(mock_logging, mock_window, mock_exit):
    jankyguihelpers.fatal("boom", detail="stacktrace here")
    mock_window.assert_called_once()
    args, _ = mock_window.call_args
    assert "An error has occured" in args[1]
    assert "boom" in args[1]


@patch("vrappcommon.jankyguihelpers.os._exit")
@patch("vrappcommon.jankyguihelpers.TopErrorWindow")
@patch("vrappcommon.jankyguihelpers.logging")
def test_fatal_nodecor(mock_logging, mock_window, mock_exit):
    jankyguihelpers.fatal("raw message", nodecor=True)
    mock_window.assert_called_once()
    args, _ = mock_window.call_args
    assert args[1] == "raw message"


@patch("vrappcommon.jankyguihelpers.os._exit")
@patch("vrappcommon.jankyguihelpers.TopErrorWindow")
@patch("vrappcommon.jankyguihelpers.logging")
def test_fatal_re_raises_in_debugpy(mock_logging, mock_window, mock_exit):
    with patch.dict("sys.modules", {"debugpy": MagicMock()}):
        with pytest.raises(Exception):
            jankyguihelpers.fatal("should raise")


@patch("psutil.process_iter")
def test_is_vrchat_running_found(mock_process_iter):
    p1 = MagicMock()
    p1.name.return_value = "VRChat.exe"
    p2 = MagicMock()
    p2.name.return_value = "notepad.exe"
    mock_process_iter.return_value = [p1, p2]

    from vrappcommon.vrutils import is_vrchat_running

    assert is_vrchat_running() is True


@patch("vrappcommon.vrutils.os.name", "nt")
@patch("psutil.process_iter")
def test_is_vrchat_running_not_found(mock_process_iter):
    p1 = MagicMock()
    p1.name.return_value = "explorer.exe"
    mock_process_iter.return_value = [p1]

    from vrappcommon.vrutils import is_vrchat_running

    assert is_vrchat_running() is False


@patch("vrappcommon.vrutils.os.name", "posix")
@patch("psutil.process_iter")
def test_is_vrchat_running_unix(mock_process_iter):
    p1 = MagicMock()
    p1.name.return_value = "VRChat"
    mock_process_iter.return_value = [p1]

    from vrappcommon.vrutils import is_vrchat_running

    assert is_vrchat_running() is True
