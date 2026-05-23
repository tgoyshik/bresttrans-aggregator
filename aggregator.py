import json
from typing import List, Dict, Any

class BusDataAggregator:
    def __init__(self):
        self.all_records = []
        
    def add_records(self, records: List[Dict[str, Any]]):
        self.all_records.extend(records)
        
    def save_results(self, output_json: str):
        if not self.all_records:
            print("No data to save")
            return
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(self.all_records, f, indent=2, ensure_ascii=False)
        print(f"Saved to JSON: {output_json}")
