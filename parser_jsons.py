import json
import logging
import os
from pathlib import Path
from typing import Generator, Dict, Any, List

from app.crud_2 import save_certificate_to_db
# from app.crud_2 import create_certificate  # Не используется напрямую
# RecordContext нужен только для контекста логирования, если требуется — перенести в utils
try:
    from app.certificate.schemas import CertificateCreate
except ImportError:
    from app.certificate.schemas import CertificateCreate  # fallback для совместимости
# TODO: RecordContext перенести в отдельный модуль utils, если нужен
from app.models_for_new_db_certs import RecordContext


def iter_json_files(root: str) -> Generator[Path, None, None]:
    root_path = Path(root)

    for path in root_path.rglob("*.json"):
        if path.is_file():
            yield path
            

def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_certificate(raw_data: Dict[str, Any], file_path: Path) -> CertificateCreate:
    try:
        return CertificateCreate(**raw_data)
    except Exception as e:
        logging.exception(f"Ошибка валидации файла {file_path}: {e}")
        raise

    
def process_single_certificate(path: Path) -> bool:
    """
    Обработка одного сертификата: загрузка -> валидация -> сохранение в БД
    
    Returns:
        True если успешно, False если ошибка
    """
    try:
        # 1. Загружаем JSON
        js = load_json(path)
        
        if not isinstance(js, dict):
            logging.error(f"Ожидался JSON-объект, а не массив. Файл: {path}")
            return False
        
        # Получаем данные для контекста ДО валидации
        cert_id = js.get('idCertificate', 'N/A')
        cert_number = js.get('number', 'N/A')
        
        # 2. Устанавливаем контекст и выполняем всё внутри него
        with RecordContext(
            record_type="Certificate",
            record_id=cert_id,
            extra_info=f"Номер: {cert_number}, Файл: {path.name}"
        ):
            # 3. Валидируем
            cert_obj = validate_certificate(js, path)
            
            # 4. Сохраняем в БД (контекст активен здесь!)
            save_certificate_to_db(cert_obj)
        
        logging.info(f"Сертификат сохранен: {cert_number} ({path})")
        return True
        
    except Exception as e:
        logging.error(f"Ошибка обработки {path}: {e}")
        return False


def process(root: str) -> Dict[str, int]:
    """
    Обработка всех JSON файлов из директории
    
    Returns:
        Словарь со статистикой: {"success": N, "failed": M, "total": K}
    """
    success_count = 0
    failed_count = 0
    
    for path in iter_json_files(root):
        if process_single_certificate(path):
            success_count += 1
        else:
            failed_count += 1
    
    total = success_count + failed_count
    
    logging.info(f"\nГотово! Успешно: {success_count}, Ошибок: {failed_count}, Всего: {total}")
    
    return {
        "success": success_count,
        "failed": failed_count,
        "total": total
    }


def iter_root_folders_from_12(root: str, start: int = 25):
    # берём только директории, имя которых число >= start
    items = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        try:
            num = int(name)
        except ValueError:
            continue
        if num >= start:
            items.append((num, path))
    # сортировка по номеру (12, 13, ...)
    items.sort(key=lambda x: x[0])
    return [p for _, p in items]

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    root = r"Z:\\"
    folders = iter_root_folders_from_12(root, start=25)

    total_stats = []
    for folder in folders:
        logging.info("Processing folder: %s", folder)
        stats = process(folder)   # <-- твоя функция
        total_stats.append((folder, stats))

    print("Готово. Папок обработано:", len(total_stats))
    # если надо — вывести итог
    for folder, stats in total_stats:
        print(folder, "->", stats)