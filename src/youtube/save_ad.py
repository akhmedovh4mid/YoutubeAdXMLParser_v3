import json
import time
import datetime

from pathlib import Path
from typing import Dict, Optional, List

from src.core.models import ScheduleItem, AdParseResult


class SaveAdManager:
    def __init__(self, serial: str, save_path: str = "results", config_path: str = "configs.json") -> None:
        self.serial = serial
        
        self.config_path = Path(config_path)
        self.save_path = Path(save_path).joinpath(self.serial)

        self.schedule = self.load_config()

    @staticmethod
    def str2time(time_str: str) -> datetime.time:
        hours, minutes = map(int, time_str.split(":"))
        return datetime.time(hour=hours, minute=minutes)

    def load_config(self) -> List[Optional[ScheduleItem]]:
        if not self.config_path.exists():
            return []

        with self.config_path.open("r", encoding="utf-8") as f:
            config: Dict[str, Dict[str, Dict[str, str]]] = json.load(f)
        
        items_list: List[ScheduleItem] = []
        schedule_config = config.get(self.serial)
        if schedule_config:
            for region, time in schedule_config.items():
                items_list.append(
                    ScheduleItem(
                        region_name=region.lower(), 
                        start_time=self.str2time(time["start_time"]), 
                        end_time=self.str2time(time["end_time"])
                    )
                )
        return items_list
    
    def get_current_interval(self) -> Optional[str]:
        now = datetime.datetime.now().time()

        for item in self.schedule:
            if item.start_time <= item.end_time:
                if item.start_time <= now <= item.end_time:
                    return item.region_name

            else:
                if now >= item.start_time or now <= item.end_time:
                    return item.region_name

        return None

    def save_ad_info(self, ad_info: AdParseResult) -> None:
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        if not self.schedule:
            temp_save_path = self.save_path.joinpath("all")
        else:
            region_name = self.get_current_interval()
            temp_save_path = self.save_path.joinpath(region_name if region_name else "all")
                
        temp_save_path.mkdir(parents=True, exist_ok=True)
        
        unique_name = str(int(time.time()))
        ad_save_folder = temp_save_path.joinpath(unique_name)
        ad_save_folder.mkdir(parents=True, exist_ok=True)

        with ad_save_folder.joinpath("info.txt").open("w", encoding="utf-8") as file:
            file.write(f"Text: {ad_info.text}\n")
            file.write(f"URL: {ad_info.url}\n")

        ad_info.image.save(ad_save_folder.joinpath("image.png"))
