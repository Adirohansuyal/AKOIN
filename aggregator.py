def aggregate_fields(data):
    """
    Aggregates fields with the same code and label.
    """
    if "fields" not in data:
        return data

    aggregated_fields = {}
    for field in data["fields"]:
        key = (field["code"], field["label"])
        if key not in aggregated_fields:
            aggregated_fields[key] = {
                "code": field["code"],
                "label": field["label"],
                "value": 0,
                "source_rule": field["source_rule"]
            }
        aggregated_fields[key]["value"] += field["value"]

    data["fields"] = list(aggregated_fields.values())
    return data