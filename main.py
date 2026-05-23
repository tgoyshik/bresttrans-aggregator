import os
import sys
import tempfile
import shutil
import argparse

from drive_loader import GoogleDriveBusLoader
from validator import BusDataValidator
from deduplicator import BusDeduplicator
from aggregator import BusDataAggregator
import config

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    default_sources = os.path.join(BASE_DIR, 'sources.txt')
    default_output = os.path.join(BASE_DIR, 'merged_data.json')
    default_credentials = os.path.join(BASE_DIR, 'credentials.json')

    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', '-s', default=default_sources)
    args = parser.parse_args()

    if not os.path.exists(args.sources):
        print(f"File not found: {args.sources}")
        return 1

    with open(args.sources, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    print("BRESTTRANS DATA AGGREGATOR (PARSING FILE NAMES)")
    print(f"Folders loaded: {len(urls)}")

    temp_dir = tempfile.mkdtemp(prefix='bus_aggregator_')
    loader = GoogleDriveBusLoader(credentials_file=default_credentials)
    validator = BusDataValidator()
    deduplicator = BusDeduplicator()
    aggregator = BusDataAggregator()

    all_files = []
    for url in urls:
        files = loader.download_all_from_folder(url, temp_dir)
        all_files.extend(files)

    print(f"Downloaded files: {len(all_files)}")

    for file_path in all_files:
        filename = os.path.basename(file_path)
        
        if "_" in filename:
            parts = filename.split('_')
            if len(parts) >= 2:
                student_name = f"{parts[0]} {parts[1]}"
            else:
                student_name = parts[0]
        else:
            student_name = "Unknown_Student"

        is_valid, records, errors = validator.validate_file(file_path)
        if is_valid:
            unique_records, dups = deduplicator.deduplicate(records)
            
            for record in unique_records:
                record['student'] = student_name
                
            aggregator.add_records(unique_records)
            print(f"File {filename} ({student_name}): added {len(unique_records)} records, duplicates: {dups}")
        else:
            print(f"Validation error in {filename}: {errors}")

    aggregator.save_results(default_output)
    
    print(f"Total unique records: {len(aggregator.all_records)}")
    print(f"Total duplicates removed: {deduplicator.duplicate_count}")

    shutil.rmtree(temp_dir)
    return 0

if __name__ == "__main__":
    sys.exit(main())
