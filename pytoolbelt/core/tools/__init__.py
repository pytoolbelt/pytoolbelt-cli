import hashlib
import json
from pydantic import BaseModel


def hash_config(model: BaseModel) -> str:
    model_json = json.dumps(model.to_dict())
    model_bytes = model_json.encode('utf-8')
    hash_object = hashlib.sha256()
    hash_object.update(model_bytes)
    return hash_object.hexdigest()
