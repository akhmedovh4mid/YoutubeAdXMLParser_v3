import time

from PIL.Image import Image
from typing import List, Optional
from uiautomator2 import Device, UiObject

from src.core.nodes import Nodes
from src.core.models import NodeCoords
from src.core.parser_config import ParserConfig


class ContentHandler:
    def __init__(self, device: Device) -> None:
        self.device = device
        self.nodes = Nodes(device=self.device)

    def get_content_block_coords(self) -> NodeCoords:
        watch_list_node_coords = NodeCoords.from_node(node=self.nodes.content_nodes.watch_list_node)
        if self.nodes.content_nodes.relative_container_node.exists:
            relative_container_node_coords = NodeCoords.from_node(node=self.nodes.content_nodes.relative_container_node)
            return NodeCoords(
                bounds=(
                    relative_container_node_coords.bounds[0], relative_container_node_coords.bounds[3],
                    watch_list_node_coords.bounds[2], watch_list_node_coords.bounds[3]
                ),
                center=(
                    relative_container_node_coords.center[0],
                    (watch_list_node_coords.center[1] + relative_container_node_coords.center[1]) // 2
                )
            )
        return watch_list_node_coords

    def swipe_to_next_content(self) -> None:
        coords = self.get_content_block_coords()
        self.device.swipe_points(
            points=[
                (coords.center[0], coords.bounds[3] - ParserConfig.offset),
                (coords.center[0], coords.bounds[1] + ParserConfig.offset)
            ],
            duration=ParserConfig.next_content_swipe_duration
        )
        
    def swipe_half_content(self) -> None:
        coords = self.get_content_block_coords()
        distance = (coords.bounds[3] - coords.bounds[1]) // 2
        self.device.swipe_points(
            points=[
                (coords.center[0], coords.bounds[3] - ParserConfig.offset),
                (coords.center[0], coords.bounds[3] - ParserConfig.offset - distance)
            ],
            duration=ParserConfig.half_content_swipe_duration
        )
        
    def reposition_content(self, first_point: int, second_point: int) -> None:
        coords = self.get_content_block_coords()
        self.device.swipe_points(
            points=[
                (coords.center[0], first_point),
                (coords.center[0], second_point)
            ],
            duration=ParserConfig.reposition_content_swipe_duration
        )
        
    def get_children_nodes(self, node: UiObject) -> List[Optional[UiObject]]:
        childrens = []

        for child_index in range(node.info["childCount"]):
            childrens.append(node.child(index=child_index)[0])
            
        return childrens

    def get_children_nodes_with_class(self, node: UiObject, class_name: str) -> List[Optional[UiObject]]:
        childrens = []

        for child_index in range(node.info["childCount"]):
            child = node.child(index=child_index)[0]
            if child.info.get("className") == class_name:
                childrens.append(child)

        return childrens

    def get_node_screenshot(self, left: int, top: int, right: int, bottom: int) -> Image:
        coords = self.get_content_block_coords()
        if coords.bounds[1] >= top:
            return self.device.screenshot().crop(
                box=(left, coords.bounds[1], right, bottom)
            )
        return self.device.screenshot().crop(
            box=(left, top, right, bottom)
        )

    def back_to_watch_list(self, max_attempts: int = 5) -> None:
        for _ in range(max_attempts):
            if self.nodes.content_nodes.watch_list_node.exists:
                break
            self.device.press("back")
            time.sleep(ParserConfig.video_load_timeout)
