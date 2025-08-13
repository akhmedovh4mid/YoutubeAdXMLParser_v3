import logging
import argparse
import subprocess

from pathlib import Path
from datetime import datetime
from argparse import Namespace
from uiautomator2 import Device
from typing import List, Optional
from dataclasses import dataclass
from multiprocessing import Process

from src.youtube.youtube_parser import YoutubeParser


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    serial: str
    status: str
    model: str


def parse_args() -> Namespace:
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description="Парсер рекламы YouTube")
    parser.add_argument(
        "-s", "--serials",
        nargs="+",
        help="Список серийных номеров устройств",
        required=True
    )
    return parser.parse_args()


def get_adb_devices() -> List[Optional[DeviceInfo]]:
    """Получает список подключенных ADB устройств."""
    try:
        result = subprocess.run(
            ["adb", "devices", "-l"],
            text=True,
            encoding="utf-8",
            capture_output=True,
        )
        
        devices = []
        for line in result.stdout.splitlines():
            if not line or line == "List of devices attached":
                continue

            parts = line.split()
            if len(parts) >= 4:
                devices.append(
                    DeviceInfo(
                        serial=parts[0],
                        status=parts[1],
                        model=parts[3].split(":")[1] if ":" in parts[3] else "unknown"
                    )
                )
            else:
                logger.warning(f"Не удалось распарсить строку устройства: {line}")

        return devices
    except FileNotFoundError:
        logger.error("ADB не найден! Убедитесь, что он установлен и добавлен в PATH.")
        return []
    except Exception as e:
        logger.error(f"Ошибка при получении устройств: {str(e)}", exc_info=True)
        return []
    

def worker(serial: str, links: List[str]) -> None:
    """Рабочая функция для каждого процесса."""
    logger.info(f"[{serial}] Запуск worker процесса")
    start_time = datetime.now()
    
    try:
        device = Device(serial=serial)
        parser = YoutubeParser(device=device)
        parser.run(links=links)
    except Exception as e:
        logger.error(f"[{serial}] Ошибка в worker процессе: {str(e)}", exc_info=True)
    finally:
        duration = datetime.now() - start_time
        logger.info(f"[{serial}] Worker процесс завершен. Время работы: {duration}")


def main():
    """Основная функция приложения."""
    args = parse_args()
    links_file = Path("links.txt")
    
    logger.info("Запуск приложения YouTube Parser")
    
    links_file = Path("links.txt")
    if not links_file.is_file():
        logger.error("Файл links.txt не найден в рабочей директории")
        exit(1)
        
    logger.info("Получение списка подключенных устройств...")
    connected_devices = get_adb_devices()
    
    valid_serials = []
    for serial in args.serials:
        if serial not in [d.serial for d in connected_devices]:
            logger.error(f"Устройство {serial} не подключено или не найдено!")
        else:
            valid_serials.append(serial)
    
    if not valid_serials:
        logger.error("Нет доступных устройств для работы. Выход.")
        exit(1)

    logger.info(f"Устройства для обработки: {valid_serials}")

    try:
        with open(links_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]
            logger.info(f"Загружено {len(links)} ссылок из файла")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла links.txt: {str(e)}")
        exit(1)

    if not links:
        logger.error("Файл links.txt пуст")
        exit(1)

    processes = []
    start_time = datetime.now()

    try:
        logger.info("Запуск процессов для устройств...")
        for serial in valid_serials:
            logger.info(f"Создание процесса для устройства {serial}")
            process = Process(
                name=f"Device-{serial}",
                target=worker,
                args=(serial, links),
                daemon=True
            )
            processes.append(process)
            process.start()
            logger.debug(f"Процесс для устройства {serial} запущен")

        logger.info("Ожидание завершения процессов...")
        for process in processes:
            process.join()
            logger.debug(f"Процесс {process.name} завершил работу")

    except KeyboardInterrupt:
        logger.warning("Получен сигнал прерывания. Завершение процессов...")
        for process in processes:
            process.terminate()
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}", exc_info=True)
    finally:
        duration = datetime.now() - start_time
        logger.info(f"Все процессы завершены. Общее время работы: {duration}")


if __name__ == "__main__":
    main()
