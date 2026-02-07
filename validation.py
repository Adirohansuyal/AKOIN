def validate_corep(data):

    flags = []

    cet1 = 0
    at1 = 0

    for f in data["fields"]:
        if f["code"] == "010":
            cet1 = f["value"]
        if f["code"] == "020":
            at1 = f["value"]

    if cet1 < 0:
        flags.append("CET1 cannot be negative")

    tier1 = cet1 + at1

    if tier1 == 0:
        flags.append("Tier 1 capital is zero")

    data["validation_flags"] = flags
    return data
