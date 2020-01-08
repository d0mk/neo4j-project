from neo4j import GraphDatabase
import json
from build_neo4j_db import (
    build_graph_manager,
    MovieNode,
    GenreNode,
    CompanyNode,
    PersonNode
)

def load_connection_data():
    with open('connection_data.json', 'r') as f:
        data = json.load(f)
    return data['uri'], data['user'], data['password']


def empty_and_fill_database():

    def get_attributes(node):
        if node.label == MovieNode.label:
            attr_string = '''
                original_title: $org_title,
                runtime: $runtime,
                rating: $rating,
                title: $title,
                year: $year'''
            attributes = {
                'org_title': node.original_title,
                'runtime': node.runtime,
                'rating': node.rating,
                'title': node.title,
                'year': node.year
            }

        elif node.label == GenreNode.label:
            attr_string = 'name: $name'
            attributes = {'name': node.name}

        elif node.label == CompanyNode.label:
            attr_string = 'name: $name'
            attributes = {'name': node.name}

        elif node.label == PersonNode.label:
            attr_string = 'name: $name, type: $type'
            attributes = {'name': node.name, 'type': node.type}

        return attr_string, attributes


    uri, user, password = load_connection_data()
    driver = GraphDatabase.driver(uri, auth=(user, password))
    gm = build_graph_manager()

    with driver.session() as session:
        session.run('MATCH (n) DETACH DELETE n')

        for rel_type in gm.relationships:
            for node_1, node_2 in gm.relationships[rel_type]:
                n_1 = get_attributes(node_1)
                n_2 = get_attributes(node_2)

                session.run(f'MERGE (n:{node_1.label} {{{n_1[0]}}}) '
                            f'MERGE (m:{node_2.label} {{{n_2[0]}}}) '
                            f'MERGE (n)<-[:{rel_type}]-(m)', {**n_1[1], **n_2[1]})

    driver.close()


if __name__ == '__main__':
    empty_and_fill_database()