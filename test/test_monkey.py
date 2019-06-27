from kw.platform import monkey


def test_patch(mocker):
    m_patch = mocker.Mock()
    m_module = mocker.Mock(patch=m_patch)

    mocker.patch("kw.platform.monkey._import_module", return_value=m_module)

    assert "requests" not in monkey._PATCHED_MODULES

    monkey.patch(requests=True)

    assert "requests" in monkey._PATCHED_MODULES
    m_patch.assert_called_once_with()
