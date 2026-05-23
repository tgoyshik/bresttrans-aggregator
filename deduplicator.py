import hashlib
from typing import List, Dict, Tuple, Any

class BusDeduplicator:
    def __init__(self):
        self.seen_hashes = set()
        self.duplicate_count = 0
    
    def _create_record_hash(self, record: Dict[str, Any]) -> str:
        time = record.get('time', '')
        stop = record.get('currentStop', '')
        entered = record.get('entered', '')
        hash_string = f"{time}|{stop}|{entered}"
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    def deduplicate(self, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
        unique_records = []
        duplicates_in_batch = 0
        for record in records:
            r_hash = self._create_record_hash(record)
            if r_hash not in self.seen_hashes:
                self.seen_hashes.add(r_hash)
                unique_records.append(record)
            else:
                duplicates_in_batch += 1
                self.duplicate_count += 1
        return unique_records, duplicates_in_batch
