import io
import pandas as pd
from resources.utils.use_cases_execeptions import ParseFileException


def get_csv_from_file(file: bytes) -> pd.DataFrame:
    try:
        buffer = io.BytesIO(file)
        df = pd.read_csv(buffer, header=None, dtype={i: object for i in range(0, 6)})
    except Exception:
        raise ParseFileException(format_expected="csv")
    return df


def check_regex(column: pd.Series, regex: str) -> dict:
    match_regex = column.str.contains(regex)
    errors = column[~match_regex].to_dict()
    return errors
