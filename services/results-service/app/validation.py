def check_ranges(values: dict, fields: list[dict]) -> list[dict]:
    """Return one problem per value that is outside its allowed range."""
    problems = []
    for field in fields:
        name = field["name"]
        if name in values:
            value = values[name]
            if not isinstance(value, (int, float)):
                problems.append({"field": name, "issue": "must be a number"})
            elif not (field["min"] <= value <= field["max"]):
                problems.append(
                    {
                        "field": name,
                        "issue": f"must be between {field['min']} and {field['max']}",
                    }
                )
    return problems
