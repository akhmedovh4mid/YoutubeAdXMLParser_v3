from uiautomator2 import Device

from src.core.node_selectors import Selectors


class BaseNode:
    def __init__(self, device: Device) -> None:
        self.device = device
        self._init_nodes()
        
    def _init_nodes(self) -> None:
        raise NotImplementedError


class MainNodes(BaseNode):
    def _init_nodes(self) -> None:
        self.main_node = self.device(**Selectors.Main.main_node)
        self.time_bar_node = self.main_node.child(**Selectors.Main.time_bar_node)
        self.video_player_node = self.main_node.child(**Selectors.Main.video_player_node)
        self.video_metadata_node = self.main_node.child(**Selectors.Main.video_metadata_node)
        self.engagement_panel_node = self.main_node.child(**Selectors.Main.engagement_panel_node)


class PlayerNodes(MainNodes):
    def _init_nodes(self) -> None:
        super()._init_nodes()
        self.progress_bar = self.video_player_node.child(**Selectors.Player.progress_bar)
        self.control_button = self.video_player_node.child(**Selectors.Player.control_button)

class ContentNodes(MainNodes):
    def _init_nodes(self) -> None:
        super()._init_nodes()
        self.ad_block_node = self.video_metadata_node.child(**Selectors.Content.ad_block_node)
        self.watch_list_node = self.video_metadata_node.child(**Selectors.Content.watch_list_node)
        self.relative_container_node = self.video_metadata_node.child(**Selectors.Content.relative_container_node)


class AdNodes(MainNodes):
    def _init_nodes(self) -> None:
        super()._init_nodes()
        self.close_button = self.engagement_panel_node.child(**Selectors.Ad.close_ad_button)
        self.header_panel_node = self.engagement_panel_node.child(**Selectors.Ad.header_panel_node)
        self.drag_handle_button = self.engagement_panel_node.child(**Selectors.Ad.drag_handle_button)


class ClassNodes(MainNodes):
    def _init_nodes(self) -> None:
        super()._init_nodes()
        self.relative_layouts = self.video_metadata_node.child(**Selectors.Class.relative_layout)
        
        
class ChromeNodes(BaseNode):
    def _init_nodes(self) -> None:
        self.toolbar_node = self.device(**Selectors.Chrome.toolbar_node)
        self.action_button = self.toolbar_node.child(**Selectors.Chrome.action_button)
        self.content_preview_text = self.device(**Selectors.Chrome.content_preview_text)


class Nodes:
    _instance = None

    def __new__(cls, device: Device):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, device: Device) -> None:
        if self._initialized:
            return
        self.device = device
        self._init_nodes()
        self._initialized = True

    def _init_nodes(self) -> None:
        self.ad_nodes = AdNodes(self.device)
        self.main_nodes = MainNodes(self.device)
        self.class_nodes = ClassNodes(self.device)
        self.chrome_nodes = ChromeNodes(self.device)
        self.player_nodes = PlayerNodes(self.device)
        self.content_nodes = ContentNodes(self.device)

