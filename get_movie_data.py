import imdb
import json
import re
import os


# value used for limiting the number of elements in movie's list attributes,
# for example storing info only about top N cast members or directors
N = 5


def get_top250_movies_data():
    ia = imdb.IMDb()

    movies_ids = (movie.getID() for movie in ia.get_top250_movies())
    top250_movies = (ia.get_movie(movie_id) for movie_id in movies_ids)

    selected_keys = (
        'original title',
        'title',
        'cast',
        'genres',
        'runtimes',
        'rating',
        'year',
        'director',
        'production companies'
    )

    movie_data = {}
    
    for movie in top250_movies:
        movie_data[movie.movieID] = {key : extract_info(value) for key, value in movie.data.items() if key in selected_keys}

        # printing progress
        print(f'\r{(len(movie_data) / 250) * 100:.2f}%', end='')

    for movie_id in movie_data:
        movie_data[movie_id]['runtimes'] = int(movie_data[movie_id]['runtimes'][0])
        movie_data[movie_id]['original title'] = strip_year_from_title(movie_data[movie_id]['original title'])

    return movie_data


def extract_info(value):
    if isinstance(value, list):
        value = value[:N]
        if isinstance(value[0], (imdb.Person.Person, imdb.Company.Company)):
            return [v.data for v in value]
        else:
            return [v for v in value]
    else:
        return value


def strip_year_from_title(title):
    return re.sub(r' \(\d+\)', '', title)


def save_data_to_json(data):
    with open('movie_data.json', 'w') as f:
        json.dump(data, f)


def get_data_and_save_to_json_file():
    '''Function used for retrieving information about 250 movies
       from imdb ranking. This process can take about 10 minutes,
       the original movie_data.json file is overwrited.
    '''

    if os.path.isfile('./movie_data.json'):
        print('The movie_data.json file already exists, generating it may take about 10 minutes.')
        if input('Continue? (y/n): ').lower() == 'y':
            save_data_to_json(get_top250_movies_data())
        else:
            print('\nOperation canceled.')
    else:
        save_data_to_json(get_top250_movies_data())


if __name__ == '__main__':
    get_data_and_save_to_json_file()