from neo4j import GraphDatabase
import random
import json


'''
relation types:
- ACTED_IN (aktor grał w danym filmie)
- BELONGS_TO (film należy do danego gatunku)
- HAS_DIRECTED (osoba wyreżyserowała dany film)
- HAS_PRODUCED (firma wyprodukowała dany film)
'''


class GraphManager:
    def __init__(self):
        self.movie_nodes = []
        self.person_nodes = []
        self.company_nodes = []
        self.genre_nodes = []
        self.relationships = {
            'ACTED_IN': [],
            'BELONGS_TO': [],
            'HAS_DIRECTED': [],
            'HAS_PRODUCED': []
        }

    def add_movie_node(self, node):
        if node not in self.movie_nodes:
            self.movie_nodes.append(node)

    def add_person_node(self, node):
        if node not in self.person_nodes:
            self.person_nodes.append(node)

    def add_company_node(self, node):
        if node not in self.company_nodes:
            self.company_nodes.append(node)

    def add_genre_node(self, node):
        if node not in self.genre_nodes:
            self.genre_nodes.append(node)

    def delete_temps(self):
        del self.movie_nodes
        del self.person_nodes
        del self.company_nodes
        del self.genre_nodes

    def get_number_of_all_nodes(self):
        return len(self.movie_nodes) + len(self.person_nodes) + len(self.company_nodes) + len(self.genre_nodes)

    def get_number_of_all_relationships(self):
        return sum(len(x) for x in self.relationships.values())


class MovieNode:
    label = 'Movie'

    def __init__(self, movie):
        self.original_title = movie['original title']
        self.runtime = movie['runtimes']
        self.rating = movie['rating']
        self.title = movie['title']
        self.year = movie['year']
        self.genres = movie['genres']
        self.cast = movie['cast']
        self.directors = movie['director']
        self.companies = movie['production companies']

    def delete_temps(self):
        del self.genres
        del self.cast
        del self.directors
        del self.companies

    def __eq__(self, other):
        return self.title == other.title


class PersonNode:
    label = 'Person'

    def __init__(self, person, p_type):
        self.name = person['name']
        self.type = p_type

    def __eq__(self, other):
        return self.name == other.name


class CompanyNode:
    label = 'Company'

    def __init__(self, company):
        self.name = company['name']

    def __eq__(self, other):
        return self.name == other.name


class GenreNode:
    label = 'Genre'

    def __init__(self, genre):
        self.name = genre

    def __eq__(self, other):
        return self.name == other.name


def build_graph_manager():
    with open('movie_data.json', 'r') as f:
        full_data = json.load(f)
    
    # working in a loop to ensure that total number of nodes
    # does not exceed 1000 and total number of relationships
    # does not exceed 10000 (graphenedb free plan limit)
    while True:

        # selecting random 120 items from full movie data
        keys = random.sample(list(full_data.keys()), k=120)
        data = {key: full_data[key] for key in keys}

        gm = GraphManager()

        # filling GraphManager with nodes
        for movie_id, movie_info in data.items():
            gm.add_movie_node(MovieNode(movie_info))
            
            for genre in movie_info['genres']:
                gm.add_genre_node(GenreNode(genre))

            for person in movie_info['cast']:
                gm.add_person_node(PersonNode(person, 'actor'))

            for director in movie_info['director']:
                gm.add_person_node(PersonNode(director, 'director'))

            for company in movie_info['production companies']:
                gm.add_company_node(CompanyNode(company))
    
        if gm.get_number_of_all_nodes() > 1000:
            continue

        # building relationships if the number of nodes <= 1000
        for person in gm.person_nodes:
            for movie in gm.movie_nodes:
                if person.type == 'actor':
                    if any(person.name == p['name'] for p in movie.cast):
                        gm.relationships['ACTED_IN'].append((movie, person))
                if person.type == 'director':
                    if any(person.name == p['name'] for p in movie.directors):
                        gm.relationships['HAS_DIRECTED'].append((movie, person))

        for genre in gm.genre_nodes:
            for movie in gm.movie_nodes:
                if genre.name in movie.genres:
                    gm.relationships['BELONGS_TO'].append((movie, genre))

        for company in gm.company_nodes:
            for movie in gm.movie_nodes:
                if any(company.name == c['name'] for c in movie.companies):
                    gm.relationships['HAS_PRODUCED'].append((movie, company))

        if gm.get_number_of_all_relationships() <= 10000:
            break

    # deleting obsolete data, which makes the gm object
    # about 40-50% smaller in size (for example, 713 kB -> 388 kB)
    gm.delete_temps()

    # omitting isinstance check because node_1 is always of MovieNode type
    for relation in gm.relationships.values():
        for node_1, node_2 in relation:
            if hasattr(node_1, 'genres'):
                node_1.delete_temps()

    # returning final object with information about nodes
    # and relationships between them                
    return gm