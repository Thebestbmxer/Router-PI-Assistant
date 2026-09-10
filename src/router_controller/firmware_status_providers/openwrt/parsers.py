def parse_release(output: str) -> dict[str, str]:
    result = {}

    for line in output.splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        result[key.strip()] = (
            value.strip()
            .strip("'")
        )

    return result


def parse_load_average(
    output: str,
) -> tuple[float, float, float] | None:

    parts = output.split()

    if len(parts) < 3:
        return None

    try:
        return (
            float(parts[0]),
            float(parts[1]),
            float(parts[2]),
        )

    except ValueError:
        return None


def parse_meminfo(
    output: str,
) -> dict[str, int]:

    result = {}

    for line in output.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        value = value.strip()

        if value.endswith("kB"):
            value = value[:-2]

        try:
            result[key.strip()] = int(value) * 1024

        except ValueError:
            continue

    return result
