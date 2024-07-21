from fastapi import FastAPI,HTTPException
from schemas import GenreChoices,BandBase,BandCreate,BandwithID

app = FastAPI()

BANDS = [
    {"id" : 1, "name" : "The Kinks","genre" : "Rock"},
    {"id" : 2, "name" : "Aphex Twin","genre" : "Electronic"},
    {"id" : 3, "name" : "Black Sabbath","genre" : "Metal","albums": [
        {"title": "Master Of Reality","release_date": "1971-07-21"}
    ]},
    {"id" : 4, "name" : "Wu-Tang Clan","genre" : "Hip-Hop"},
]

@app.get('/bands')
#function returns a list of Band
async def bands(genre: GenreChoices | None = None, has_albums: bool = False) -> list[BandBase]: #"GenreChoices | None" means genre can be of type GenreChoices or None. Defaults is None if nothing is provided,if not a query parameter MUST be provided
    band_list = [BandwithID(**b) for b in BANDS]

    if genre:
        band_list = [
            b for b in band_list if b.genre.lower() == genre.value #to get the value of an enum and then creates a list of Band objects by unpacking each filtered dictionary into the Band model
        ]
    
    if has_albums:
        band_list = [
            b for b in band_list if len(b.albums) > 0
        ]
    return band_list

@app.get('/bands/{band_id}')
async def band(band_id:int) -> BandwithID:
    #next() is a built-in function that retrieves the next item, and in this case if the next item is None throw a 404 error
    band = next((BandwithID(**b) for b in BANDS if b["id"] == band_id), None) #iterating over BANDS with id to see if it matches band_id
    if band is None:
        raise HTTPException(status_code=404,detail="Band not found")
    return band

@app.get('/bands/genre/{genre}')
async def bands_for_genre(genre: GenreChoices) -> list[dict]:
    return[
        b for b in BANDS if b["genre"].lower() == genre.value 
    ]

@app.put('/bands')
async def create_band(band_data: BandCreate) ->BandwithID:
    id = BANDS[-1]['id'] + 1 #gets the last id and increments it
    band = BandwithID(id=id, **band_data.model_dump()).model_dump()#creates a new instance and of BandWithID with the id and the unpacked data from band_data(its really bandCreate tho) and then the second "model_dump() is to convert it to a dictionary"
    BANDS.append(band)
    return band