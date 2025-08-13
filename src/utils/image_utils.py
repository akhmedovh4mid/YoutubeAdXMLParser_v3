import numpy as np

from typing import Optional
from PIL import Image, ImageChops
from PIL.Image import Image as PILImage


class ImageUtils:
    @staticmethod
    def combine_images_vertically(
        top_img: PILImage, 
        bottom_img: PILImage,
        output_path: str = None,
        background_color: tuple = (255, 255, 255)
    ) -> Optional[PILImage]:
        width = max(top_img.width, bottom_img.width)
        height = top_img.height + bottom_img.height
        
        combined = Image.new("RGB", (width, height), background_color)
        
        x_offset = (width - top_img.width) // 2
        combined.paste(top_img, (x_offset, 0))
        
        x_offset = (width - bottom_img.width) // 2
        combined.paste(bottom_img, (x_offset, top_img.height))
        
        if output_path:
            combined.save(output_path)
            return None
        return combined
    
    @staticmethod
    def compare_images(image1: PILImage, image2: PILImage, tolerance: int = 5) -> float:
        if image1.size != image2.size or image1.mode != image2.mode:
            width = min(image1.width, image2.width)
            height = min(image1.height, image2.height)
            image1 = image1.resize((width, height))
            image2 = image2.resize((width, height))
            
        if image1.mode != 'RGB':
            image1 = image1.convert('RGB')
        if image2.mode != 'RGB':
            image2 = image2.convert('RGB')
        
        diff = ImageChops.difference(image1, image2)
        
        diff_array = np.array(diff)
        
        similar_pixels = np.sum(np.all(diff_array <= tolerance, axis=2))
        total_pixels = diff_array.shape[0] * diff_array.shape[1]
        
        similarity_percent = (similar_pixels / total_pixels) * 100
        
        return round(similarity_percent, 2)
