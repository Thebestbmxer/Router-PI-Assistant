from router_controller.firmware_status_providers.openwrt.parsers import (
    parse_storage,
)

def test_parse_storage():
    output = """
Filesystem 1024-blocks Used Available Mounted on
/dev/root 15360 9000 6360 /
"""

    result = parse_storage(output)

    assert result["total"] == 15360 * 1024
    assert result["used"] == 9000 * 1024
    assert result["available"] == 6360 * 1024
