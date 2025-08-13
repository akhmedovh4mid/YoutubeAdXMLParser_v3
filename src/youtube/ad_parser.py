import time

from typing import Optional
from PIL.Image import Image
from uiautomator2 import Device

from src.core.nodes import Nodes
from src.utils.ocr import Tesseract
from src.core.models import NodeCoords
from src.core.models import AdParseResult
from src.utils.image_utils import ImageUtils
from src.core.node_selectors import Selectors
from src.core.parser_config import ParserConfig
from src.youtube.content_handler import ContentHandler


class AdParser:
    def __init__(self, device: Device, lang: str = "eng") -> None:
        self.lang = lang
        self.device = device
        self.nodes = Nodes(device=self.device)
        self.content_handler = ContentHandler(device=self.device)

    def get_ad_url(self, node_coords: NodeCoords) -> Optional[str]:
        self.device.click(*node_coords.center)
        
        try:
            self.nodes.chrome_nodes.action_button.click(timeout=ParserConfig.node_spawn_timeout)
        except:
            return None

        self.nodes.chrome_nodes.content_preview_text.wait(timeout=ParserConfig.node_spawn_timeout)
        
        url = self.nodes.chrome_nodes.content_preview_text.get_text()

        self.device.press("back")
        time.sleep(ParserConfig.action_timeout)
        self.device.press("back")
        time.sleep(ParserConfig.action_timeout)

        return url
        
    def get_ad_text(self, image: Image) -> str:
        image_crop = image.crop(box=(int(image.width * 0.13), 0, int(image.width * 0.87), image.height))
        image_data = Tesseract.get_screen_data(image=image_crop, lang=self.lang)
        text = " ".join(word for line in image_data.text for word in line.split())
        return text

    def parse_ad(self) -> Optional[AdParseResult]:
        view_count = self.nodes.content_nodes.ad_block_node.child(**Selectors.Class.view_group).count
        image_count = self.nodes.content_nodes.ad_block_node.child(**Selectors.Class.image_view).count
        
        match (view_count, image_count):
            case (8, 4) | (7, 4) | (8, 3) | (7, 3) | (18, 8) | (18, 7) | (18, 9) | (17, 8):
                ...
            case (v, i) if (v <= 2 and i <= 3): 
                return None
            case (8, 5):
                return None
            case _:
                # Отправка в тг
                return None

        ad_block_node_children = self.content_handler.get_children_nodes(node=self.nodes.content_nodes.ad_block_node)
        watch_list_coords = NodeCoords.from_node(node=self.nodes.content_nodes.watch_list_node)
        ad_block_coords = NodeCoords.from_node(node=self.nodes.content_nodes.ad_block_node)
        image_node_coords = NodeCoords.from_node(node=ad_block_node_children[0])
        
        ad_text_block = self.content_handler.get_node_screenshot(
            ad_block_coords.bounds[0], image_node_coords.bounds[3],
            ad_block_coords.bounds[2], ad_block_coords.bounds[3]
        )
        
        sponsored_text = Tesseract.find_matches_by_word(lang=self.lang, image=ad_text_block, target_word="Sponsored", scale=2)
        ad_text_block = ad_text_block.crop(box=(0, 0, ad_text_block.width, sponsored_text.top + sponsored_text.height))

        content_block_coords = self.content_handler.get_content_block_coords()
        if image_node_coords.bounds[1] <= content_block_coords.bounds[1]:
            self.content_handler.reposition_content(
                first_point=image_node_coords.bounds[3],
                second_point=watch_list_coords.bounds[3]
            )
            time.sleep(ParserConfig.action_timeout)

            ad_block_node_children = self.content_handler.get_children_nodes(node=self.nodes.content_nodes.ad_block_node)
            image_node_coords = NodeCoords.from_node(node=ad_block_node_children[0])
        
        ad_image_block = self.content_handler.get_node_screenshot(*image_node_coords.bounds)

        text = self.get_ad_text(image=ad_text_block)
        url = self.get_ad_url(node_coords=image_node_coords)
        if url is None:
            return None
        
        image = ImageUtils.combine_images_vertically(top_img=ad_image_block, bottom_img=ad_text_block)

        return AdParseResult(url=url, text=text, image=image)
