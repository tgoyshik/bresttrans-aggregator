import json
from typing import List, Dict, Any, Tuple
from models import BusRecordModel
from pydantic import ValidationError

class BusDataValidator:
    def validate_file(self, file_path: str) -> Tuple[bool, List[Dict[str, Any]], List[str]]:
        errors = []
        valid_records = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if not isinstance(data, list):
                return False, [], ["Root element must be a list"]
            for idx, item in enumerate(data):
                try:
                    validated_item = BusRecordModel(**item)
                    valid_records.append(validated_item.dict())
                except ValidationError as e:
                    for error in e.errors():
                        errors.append(f"Index {idx} -> {'.'.join(map(str, error['loc']))}: {error['msg']}")
            
            if valid_records:
                return True, valid_records, errors
            else:
                return False, [], errors if errors else ["File is empty"]
                
        except json.JSONDecodeError as e:
            return False, [], [f"[JSON_SYNTAX_ERROR] {str(e)}"]
        except Exception as e:
            return False, [], [str(e)]