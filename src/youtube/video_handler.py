import time

from uiautomator2 import Device, UiObjectNotFoundError

from src.core.nodes import Nodes
from src.core.models import NodeCoords
from src.core.node_selectors import Selectors
from src.core.parser_config import ParserConfig


class VideoHandler:
    def __init__(self, device: Device) -> None:
        self.device = device
        self.nodes = Nodes(device=self.device)
    
    def wait_load_video(self, max_attempts: int = 15) -> bool:
        for _ in range(max_attempts):
            if (self.nodes.class_nodes.relative_layouts.count == 0) and (not self.nodes.player_nodes.progress_bar.exists):
                return True
            time.sleep(ParserConfig.video_load_timeout)
        return False
    
    def stop_video(self) -> bool:
        try:
            control_btn = self.nodes.player_nodes.control_button
            if not control_btn.exists:
                self.nodes.main_nodes.video_player_node.click()
                control_btn.wait(timeout=ParserConfig.action_timeout)

            if control_btn.exists:
                if control_btn.info.get("contentDescription") != "Play video":
                    control_btn.click()
                    control_btn.wait(timeout=ParserConfig.action_timeout)
                return control_btn.info.get("contentDescription") == "Play video"
            return False
        except UiObjectNotFoundError:
            return False
        
    def ensure_video_stopped(self, max_attempts: int = 3) -> bool:
        for _ in range(max_attempts):
            if self.stop_video():
                return True
            time.sleep(ParserConfig.action_timeout)
        return False
        
    def _handle_drag_handle_case(self) -> bool:
        drag_button_coords = NodeCoords.from_node(node=self.nodes.ad_nodes.drag_handle_button)
        main_node_coords = NodeCoords.from_node(node=self.nodes.main_nodes.main_node)
        
        start_point = (drag_button_coords.center[0], drag_button_coords.bounds[3] + ParserConfig.offset)
        end_point = (drag_button_coords.center[0], main_node_coords.bounds[3] - ParserConfig.offset)
        
        self.device.swipe_points(points=[start_point, end_point], duration=ParserConfig.hidden_ad_duration)
        time.sleep(ParserConfig.action_timeout)

        return not self.nodes.ad_nodes.drag_handle_button.exists
    
    def _handle_close_button_case(self) -> bool:
        try:
            button = self.nodes.ad_nodes.header_panel_node.child(**Selectors.Ad.close_ad_button)
            if button.exists and button.click_exists(timeout=1):
                time.sleep(ParserConfig.action_timeout)
                return not button.exists

            buttons = self.nodes.ad_nodes.header_panel_node.child(**Selectors.Class.image_view)
            if buttons.count > 0 and buttons[-1].click_exists(timeout=1):
                time.sleep(ParserConfig.action_timeout)
                try:
                    return not buttons[-1].exists
                except AssertionError:
                    return True
        except UiObjectNotFoundError:
            return False
        
        return False
    
    def _handle_close_ad(self) -> bool:
        if not self.nodes.ad_nodes.header_panel_node.exists:
            return False

        if self.nodes.ad_nodes.drag_handle_button.exists:
            return self._handle_drag_handle_case()
        
        return self._handle_close_button_case()
    
    def hide_ads(self) -> bool:
        success = self._handle_close_ad()
        if not success:
            time.sleep(ParserConfig.ad_wait_timeout)
            success = self._handle_close_ad()

        if not success and self.nodes.ad_nodes.header_panel_node.exists:
            return False
        return True

    def preparing_video(self) -> bool:
        if not self.wait_load_video():
            return False
        time.sleep(ParserConfig.action_timeout)
        
        watch_list_node = self.nodes.content_nodes.watch_list_node
        if watch_list_node.exists and watch_list_node.child().count == 0:
            return False

        if not self.ensure_video_stopped():
            return False
        time.sleep(ParserConfig.action_timeout)
        
        if not self.hide_ads():
            return False
        time.sleep(ParserConfig.action_timeout)
        
        return True
