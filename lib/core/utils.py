import math
import numpy as np

from datetime import timezone
from ruamel.yaml import YAML

def load_yaml(path):
    yaml = YAML()
    with open(path, encoding="utf-8") as f:
        return yaml.load(f)

def ensure_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    return obj


def safe_float(value):
    if value is None:
        return 0.0
    if isinstance(value, (float, np.floating)) and math.isnan(value):
        return 0.0
    return float(value)