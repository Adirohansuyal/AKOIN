import pandas as pd

def map_to_template(data):

    rows = []

    for f in data["fields"]:
        rows.append({
            "Field Code": f["code"],
            "Description": f["label"],
            "Value": f["value"],
            "Rule Source": f["source_rule"]
        })

    df = pd.DataFrame(rows)
    return df
