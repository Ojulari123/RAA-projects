import typer
import os
from io import BytesIO
import requests
import asyncio
import httpx
from datetime import datetime 
from config import API_URL, IMAGE_DIR
from PIL import Image
from helper import url_query_params, get_image,save_image

app = typer.Typer()

# @app.command()
# def hello(name: str):
#     typer.echo(f"Hello {name}")

# setting the default format
default_format = typer.Argument(
    datetime.now().strftime('%Y-%m-%d'),
    formats=['%Y-%m-%d']
)

# @app.command()
# # passing the default format as parameter, which will essentially print what the current day of the week is
# def day_of_week(date: datetime = default_format):
#     typer.echo(date.strftime('%A'))

# function to get images from url asynchronously
async def get_images(urls):
    async with httpx.AsyncClient() as client:
        #make a new list and append the the images in the url using a HTTP client
        tasks = []
        for url in urls:
            tasks.append(
                asyncio.create_task(get_image(client, url)) #an async task is to be created and is scheduling when to call the function
            )
        images = await asyncio.gather(*tasks)
        return images
    
@app.command()
def fetch_image(
    date: datetime = default_format, 
    save: bool = False,
    start: datetime =typer.Option(None),
    end: datetime = typer.Option(None),
):
    print("Sending API requests")
    query_params = url_query_params(date, start, end)

    #Adding 'date' to the API call 
    response = requests.get(API_URL,params=query_params)

    response.raise_for_status() #if response isnt 200 raise exception

    # turn the date from the parameter into a string
    # datetime = str(date.date())
    # url_for_date = f"{API_URL}&date={datetime}"
    # response = requests.get(url_for_date)

    data = response.json()
    
    if isinstance(data, dict):
        data = [data]

    urls = [d['url'] for d in data] #get the values in url dictionary and store them in a new list
    titles = [d['title'] for d in data]
    images = asyncio.run(get_images(urls)) #to asynchronously run the get_image function and assign it to images

    #loop thru images with the index i and then show the images
    for i, image in enumerate(images):
        image.show()

        # once the save flag is set to true, and if  the image directory doesnt exist make one 
        if save:
            save_image(image, titles[i])
        image.close()

if __name__ == '__main__':
    app()