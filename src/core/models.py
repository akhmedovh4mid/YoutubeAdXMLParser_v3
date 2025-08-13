from typing import Tuple
from datetime import time
from PIL.Image import Image
from uiautomator2 import UiObject
from dataclasses import dataclass


@dataclass
class AdParseResult:
    url: str
    text: str
    image: Image

    
@dataclass
class ScheduleItem:
    region_name: str
    start_time: time
    end_time: time

    
@dataclass
class NodeCoords:
    bounds: Tuple[int, int, int, int]
    center: Tuple[float, float]

    @staticmethod
    def from_node(node: UiObject) -> 'NodeCoords':
        return NodeCoords(bounds=node.bounds(), center=node.center())
