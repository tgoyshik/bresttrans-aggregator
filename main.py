import os
import sys
import tempfile
import shutil
import argparse
from collections import defaultdict

from drive_loader import GoogleDriveBusLoader
from validator import BusDataValidator
from aggregator import BusDataAggregator

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    default_sources = os.path.join(BASE_DIR, 'sources.txt')
    default_output = os.path.join(BASE_DIR, 'merged_data.json')
    default_credentials = os.path.join(BASE_DIR, 'credentials.json')

    parser = argparse.ArgumentParser()
    parser.add_argument('--sources', '-s', default=default_sources)
    args = parser.parse_args()

    sources_path = os.path.abspath(args.sources)
    if not os.path.exists(sources_path):
        try:
            with open(sources_path, 'w', encoding='utf-8') as f:
                f.write("# Вставляйте каждую ссылку с новой строки. Пример: https://drive.google.com/drive/folders/...\n")
            print(f"File created: {args.sources}")
            return 0
        except Exception as e:
            print(f"Error creating file: {e}")
            return 1

    urls = []
    filename_sources = os.path.basename(sources_path)
    
    with open(sources_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, 1):
            clean_line = line.strip()
            if not clean_line or clean_line.startswith('#'):
                continue
            
            if clean_line.count("http") > 1 or " " in clean_line:
                print(f"\nПРЕДУПРЕЖДЕНИЕ: В файле {filename_sources} на строке {idx} несколько ссылок.")
                print("Перенесите каждую ссылку на отдельную строчку.\n")
                continue
                
            urls.append(clean_line)

    print("BRESTTRANS DATA AGGREGATOR (PARSING FILE NAMES)")
    print(f"\nFolders loaded: {len(urls)}")

    temp_dir = tempfile.mkdtemp(prefix='bus_aggregator_')
    loader = GoogleDriveBusLoader(credentials_file=default_credentials)
    validator = BusDataValidator()
    aggregator = BusDataAggregator()

    all_files = []
    report_by_reasons = defaultdict(list)
    
    duplicate_counts = defaultdict(int)
    
    for url in urls:
        try:
            files = loader.download_all_from_folder(url, temp_dir)
            if not files:
                report_by_reasons["Папка пуста (нет JSON файлов)"].append(url)
            else:
                all_files.extend(files)
                
        except ValueError as e:
            report_by_reasons[f"Ошибка: {str(e)}"].append(url)
        except PermissionError as e:
            report_by_reasons[f"Ошибка: {str(e)}"].append(url)
        except Exception as e:
            report_by_reasons[f"Ошибка: {str(e)}"].append(url)

    print(f"Downloaded files: {len(all_files)}\n")

    seen_file_contents = set()
    content_to_file_key = {} 

    for file_path in all_files:
        filename = os.path.basename(file_path)
        
        if "_" in filename:
            name_parts = filename.removesuffix('.json').split('_')
            if len(name_parts) >= 3:
                student_name = f"{name_parts[0]} {name_parts[1]} {name_parts[2]}"
            elif len(name_parts) == 2:
                student_name = f"{name_parts[0]} {name_parts[1]}"
            else:
                student_name = name_parts[0]
        else:
            student_name = "Unknown_Student"

        file_key = f"Файл: {filename} ({student_name})"

        is_duplicate_file = False
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_text = f.read()
                if file_text in seen_file_contents:
                    is_duplicate_file = True
                else:
                    seen_file_contents.add(file_text)
                    content_to_file_key[file_text] = file_key
        except Exception:
            pass

        if is_duplicate_file:
            original_file_key = content_to_file_key[file_text]
            duplicate_counts[original_file_key] += 1
            continue 

        is_valid, records, errors = validator.validate_file(file_path)
        
        if is_valid:
            ordered_records = []
            for record in records:
                record.pop('student', None) 
                full_time_str = record.pop('time', '')
                
                if " " in full_time_str:
                    date_part, time_part = full_time_str.split(" ", 1)
                else:
                    date_part = full_time_str
                    time_part = ""

                new_record = {
                    'student': student_name,   
                    'date': date_part,         
                    'time': time_part          
                }
                
                new_record.update(record)      
                ordered_records.append(new_record)
                
            aggregator.add_records(ordered_records)
            print(f"File {filename} ({student_name}): added {len(ordered_records)} records")
        else:
            error_str = "".join(errors)
            if "[JSON_SYNTAX_ERROR]" in error_str or "Expecting" in error_str or "JSON decode" in error_str or "unmatched" in error_str:
                reason_headline = "Файл поврежден (нарушен синтаксис JSON)"
            else:
                reason_headline = "Файл не прошел валидацию (сбиты форматы полей или пропущены данные)"
                
            report_by_reasons[reason_headline].append(f"Файл: {filename} ({student_name})")

    aggregator.save_results(default_output)
    
    total_duplicate_files = sum(duplicate_counts.values())
    print(f"Total unique records: {len(aggregator.all_records)}")
    print(f"Total duplicate files removed: {total_duplicate_files}")

    if duplicate_counts:
        print("\nОТЧЕТ О ДУБЛИКАТАХ:\n")
        for file_info, count in duplicate_counts.items():
            print(f"{file_info} количество {count}")

    if report_by_reasons:
        print("\nОТЧЕТ О СБОЯХ ПРИ ОБРАБОТКЕ ДАННЫХ:")
        for reason, items_list in report_by_reasons.items():
            print(f"\nПричина: {reason}")
            for item in items_list:
                prefix = "Ссылка:" if item.startswith("http") else ""
                clean_item = item.replace("Файл: ", "") if item.startswith("Файл:") else item
                if prefix:
                    print(f"{prefix} {clean_item}")
                else:
                    print(f"Файл: {clean_item}")
            
    print()
    shutil.rmtree(temp_dir)
    return 0

if __name__ == "__main__":
    sys.exit(main())
