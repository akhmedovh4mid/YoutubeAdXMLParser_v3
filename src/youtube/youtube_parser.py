import sys
import time
import signal
import logging

from typing import List
from uiautomator2 import Device

from src.core.nodes import Nodes
from src.core.models import NodeCoords
from src.youtube.ad_parser import AdParser
from src.utils.image_utils import ImageUtils
from src.youtube.save_ad import SaveAdManager
from src.youtube.youtube_app import YoutubeApp
from src.core.parser_config import ParserConfig
from src.youtube.video_handler import VideoHandler
from src.core.mobile_settings import MobileSettings
from src.youtube.content_handler import ContentHandler


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class ContentEndError(Exception):
    pass

class YoutubeParser:
    def __init__(self, device: Device, lang: str = "eng") -> None:
        """Инициализация парсера YouTube."""
        self.lang = lang
        self.device = device
        self._running = False
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._initialize_components()
        self._configure_device()
        logger.info(f"[{self.device.serial}] - YouTube парсер успешно инициализирован")
        
    def _signal_handler(self, signum, frame) -> None:
        """Обработчик сигналов завершения программы."""
        logger.info(f"[{self.device.serial}] - Получен сигнал {signum}, завершение работы...")
        self._running = False
        self._cleanup()
        sys.exit(0)
        
    def _initialize_components(self) -> None:
        """Инициализирует все необходимые компоненты."""
        self.nodes = Nodes(device=self.device)
        self.app = YoutubeApp(device=self.device)
        self.mobile = MobileSettings(device=self.device)
        
        self.ad_parser = AdParser(device=self.device)
        self.video_handler = VideoHandler(device=self.device)
        self.content_handler = ContentHandler(device=self.device)
        self.save_manager = SaveAdManager(serial=self.device.serial)
        
    def _configure_device(self) -> None:
        """Выполняет базовую настройку устройства."""
        try:
            self.mobile.change_rotation()
            self.mobile.notification_disable()
            logger.info(f"[{self.device.serial}] - Устройство успешно настроено")
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Ошибка при настройке устройства: {str(e)}")
            raise 
        
    def _cleanup(self) -> None:
        """Выполняет очистку ресурсов при завершении работы."""
        try:
            logger.info(f"[{self.device.serial}] - Завершение работы, закрытие YouTube...")
            self.app.close()
            logger.info(f"[{self.device.serial}] - YouTube успешно закрыт")
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Ошибка при закрытии YouTube: {str(e)}")

    def run(self, links: List[str]) -> None:
        """Основной метод для запуска парсера."""
        if not links:
            logger.warning(f"[{self.device.serial}] - Список ссылок пуст")
            return

        self._running = True
        
        try:
            self._start_youtube_app()
            
            for link in links:
                if not self._running:
                    break
                self._process_link(link)
                
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Критическая ошибка: {str(e)}", exc_info=True)
            raise
        finally:
            self._cleanup()

    def _start_youtube_app(self) -> None:
        """Запускает приложение YouTube."""
        try:
            self.app.start()
            logger.info(f"[{self.device.serial}] - Приложение YouTube успешно запущено")
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Ошибка при запуске YouTube: {str(e)}")
            raise
        
    def _process_link(self, link: str) -> None:
        """Обрабатывает одну ссылку."""
        cleaned_link = link.strip()
        logger.info(f"[{self.device.serial}] - Начало обработки ссылки: {cleaned_link}")
        
        try:
            self.app.open_link(link=cleaned_link)
            if not self._prepare_video():
                logger.warning(f"[{self.device.serial}] - Пропускаем ссылку из-за ошибки подготовки видео")
                return
            self._process_content()
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Ошибка при обработке ссылки {cleaned_link}: {str(e)}")
            # Продолжаем работу со следующей ссылкой
        finally:
            # Закрываем текущее видео перед переходом к следующему
            ...
    
    def _prepare_video(self) -> bool:
        """Подготавливает видео к просмотру."""
        try:
            result = self.video_handler.preparing_video()
            if not result:
                logger.error(f"[{self.device.serial}] - Не удалось подготовить видео")
                return False
        
            logger.info(f"[{self.device.serial}] - Подготовка видео: {result}")
            return True
        
        except Exception as e:
            logger.error(f"[{self.device.serial}] - Ошибка при подготовке видео: {str(e)}")
            return False

    def _process_content(self) -> None:
        """Обрабатывает контент на странице."""
        swipe_count = 0
        while self._running and swipe_count < ParserConfig.max_swipe_count:
            try:
                if self._process_ad_block():
                    swipe_count = 3
                else:
                    swipe_count += 1
                    self._swipe_to_next_content()
            except ContentEndError:
                logger.info(f"[{self.device.serial}] - Достигнут конец ленты")
                break
            except (Exception) as e:
                logger.error(f"[{self.device.serial}] - Ошибка при обработке контента: {str(e)}")
                break
                
    def _process_ad_block(self) -> bool:
        if not self.nodes.content_nodes.ad_block_node.exists:
            return False

        ad_block_coords = NodeCoords.from_node(self.nodes.content_nodes.ad_block_node)
        watch_block_coords = NodeCoords.from_node(self.nodes.content_nodes.watch_list_node)

        if ad_block_coords.bounds[3] == watch_block_coords.bounds[3]:
            self.content_handler.swipe_half_content()
            return True

        self._handle_ad_block(ad_block_coords, watch_block_coords)
        return True
    
    def _handle_ad_block(self, ad_coords: NodeCoords, watch_coords: NodeCoords) -> None:
        self.content_handler.reposition_content(
            first_point=ad_coords.bounds[3],
            second_point=watch_coords.bounds[3]
        )
        time.sleep(ParserConfig.action_timeout)
        
        self._parse_and_save_ad()
        
        self._swipe_to_next_content(swipes=3)
        
    def _parse_and_save_ad(self) -> None:
        result = self.ad_parser.parse_ad()
        if result:
            self.save_manager.save_ad_info(result)
            logger.info(f"[{self.device.serial}] - Найдена реклама: {result.text:.50}...")
        
        else:
            self.content_handler.back_to_watch_list()

    def _swipe_to_next_content(self, swipes: int = 1) -> None:
        for _ in range(swipes):
            before_swipe = self.device.screenshot()
            self.content_handler.swipe_to_next_content()
            time.sleep(ParserConfig.action_timeout)

            after_swipe = self.device.screenshot()
            if self._is_same_content(before_swipe, after_swipe):
                raise ContentEndError("Контент не изменился после свайпа")

    def _is_same_content(self, img1, img2) -> bool:
        match = ImageUtils.compare_images(img1, img2)
        logger.info(f"[{self.device.serial}] - Схожесть скриншотов: {match}%")
        return match >= ParserConfig.screenshot_similarity_threshold


# class YoutubeParser:
#     def __init__(self, device: Device, lang: str = "eng") -> None:
#         self.lang = lang
#         self.device = device

#         self.nodes = Nodes(device=self.device)
#         self.app = YoutubeApp(device=self.device)
#         self.mobile = MobileSettings(device=self.device)
        
#         self.ad_parser = AdParser(device=self.device)
#         self.video_handler = VideoHandler(device=self.device)
#         self.content_handler = ContentHandler(device=self.device)
#         self.save_manager = SaveAdManager(serial=self.device.serial)

#         self.mobile.change_rotation()
#         self.mobile.notification_disable()

#     def run(self, links: List[str]) -> None:
#         self.app.start()
#         print("[INFO] Открытие Youtube")
        
#         for link in links:
#             self.app.open_link(link=link)
#             print(f"[INFO] Открытие {link.replace('\n', '')}")
            
#             print(self.video_handler.preparing_video())

#             swipe_count = 0
#             while swipe_count < ParserConfig.max_swipe_count:
#                 first_screenshot = self.device.screenshot()
                
#                 if self.nodes.content_nodes.ad_block_node.exists:
#                     swipe_count = 0
                    
#                     ad_block_coords = NodeCoords.from_node(self.nodes.content_nodes.ad_block_node)
#                     watch_block_coords = NodeCoords.from_node(self.nodes.content_nodes.watch_list_node)
                    
#                     if ad_block_coords.bounds[3] == watch_block_coords.bounds[3]:
#                         self.content_handler.swipe_half_content()
#                         continue
                    
#                     else:
#                         self.content_handler.reposition_content(
#                             first_point=ad_block_coords.bounds[3],
#                             second_point=watch_block_coords.bounds[3]
#                         )
#                         time.sleep(ParserConfig.action_timeout)
                        
#                         result = self.ad_parser.parse_ad()
#                         if result:
#                             self.save_manager.save_ad_info(result)
#                             print(result)
#                         time.sleep(ParserConfig.action_timeout)
                        
#                         self.content_handler.swipe_to_next_content()
#                         time.sleep(ParserConfig.action_timeout)
#                         self.content_handler.swipe_to_next_content()
#                         time.sleep(ParserConfig.action_timeout)
                        
#                         second_screenshot = self.device.screenshot()
#                         match_percentages = ImageUtils.compare_images(first_screenshot, second_screenshot)
#                         print(match_percentages)
#                         if match_percentages >= 70:
#                             break
                        
#                         swipe_count += 2
#                         continue
                    
#                 self.content_handler.swipe_to_next_content()
#                 time.sleep(ParserConfig.action_timeout)
#                 second_screenshot = self.device.screenshot()
#                 match_percentages = ImageUtils.compare_images(first_screenshot, second_screenshot)
#                 print(match_percentages)
#                 if match_percentages >= 70:
#                     break
                
#                 swipe_count += 1
