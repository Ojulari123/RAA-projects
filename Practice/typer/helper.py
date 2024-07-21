from typing import Dict
from PIL import Image
import requests
from io import BytesIO
from config import IMAGE_DIR
import os

def url_query_params(datetime,start,end) -> Dict:
    """Generates correct URL query parameters based on CLI arguments"""
    if start:
        params = {'start_date' : str(start.date())}
        if end:
            params['end_date'] = str(end.date())
        return params
    else:
        return {'date': str(datetime.date())}
    
async def get_image(client, url: str) ->Image:
     """Makes APi request to Image endpoint, and converts Pillow Image"""
     image_response = await client.get(url)
     image = Image.open(BytesIO(image_response.content)) #turn a byte to an image / open an image froma byte stream
     return image

def save_image(image: Image, title: str):
        if not IMAGE_DIR.exists():
            os.mkdir(IMAGE_DIR)
        image_name = f"{title}.{image.format}"
        image.save(IMAGE_DIR /image_name, image.format)