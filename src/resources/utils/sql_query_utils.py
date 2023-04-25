def get_sql_in_params(name: str, params: list[str]) -> (str, dict):
    in_placeholders = [f":{name}{i}" for i in range(len(params))]
    in_placeholders = f"({', '.join(in_placeholders)})"
    in_params = {f"{name}{i}": params[i] for i in range(len(params))}
    return in_params, in_placeholders
