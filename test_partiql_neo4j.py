import pytest

import partiql_neo4j

# test pattern
# samples of Query and AST
# Remark: we don't fully parse for simple translation.
@pytest.mark.parametrize(('query', 'ast', 'cypher', 'result'), [
    (
        "SELECT p FROM Person AS p",
        ['select', ['project', ['list', ['id', 'p']]], ['from', ['as', 'p', ['id', 'Person']]]],
        "MATCH (p:Person) RETURN p AS column1",
        [({'name': 'Jennifer'},), ({'name': 'Michael'},)]
    ),
    (
        "SELECT Person FROM Person",
        ['select', ['project', ['list', ['id', 'Person']]], ['from', ['as', 'Person', ['id', 'Person']]]],
        "MATCH (Person:Person) RETURN Person AS column1",
        [({'name': 'Jennifer'},), ({'name': 'Michael'},)]
    ),
    (
        "SELECT jenn.name, jenn.name FROM Person AS jenn",
        ['select', ['project', ['list', ['path', ['id', 'jenn'], ['id', 'name']], ['path', ['id', 'jenn'], ['id', 'name']]]], ['from', ['as', 'jenn', ['id', 'Person']]]],
        "MATCH (jenn:Person) RETURN jenn.name AS column1, jenn.name AS column2",
        [('Jennifer', 'Jennifer'), ('Michael', 'Michael')]
    ),
    (
        "SELECT jenn FROM Person AS jenn WHERE jenn.name = 'Jennifer'",
        ['select', ['project', ['list', ['id', 'jenn']]], ['from', ['as', 'jenn', ['id', 'Person']]], ['where', ['=', ['path', ['id', 'jenn'], ['id', 'name']], ['lit', "'Jennifer'"]]]],
        "MATCH (jenn:Person) WHERE jenn.name = 'Jennifer' RETURN jenn AS column1",
        [({'name': 'Jennifer'},)]
    ),
    (
        "SELECT company.name FROM Person AS p, p.WORKS_FOR AS company WHERE p.name = 'Jennifer'",
        ['select', 
            ['project', ['list', ['path', ['id', 'company'], ['id', 'name']]]], 
            ['from', 
                ['inner_join', 
                    ['as', 'p', ['id', 'Person']], 
                    ['as', 'company', ['path', ['id', 'p'], ['id', 'WORKS_FOR']]]
                ]
            ],
            ['where', ['=', ['path', ['id', 'p'], ['id', 'name']], ['lit', "'Jennifer'"]]]
        ],
        "MATCH (p:Person)-[:WORKS_FOR]->(company:Company) WHERE p.name = 'Jennifer' RETURN company.name AS column1",
        [('Neo4j',)]
    ),
    (
        "SELECT Person, Person.name FROM Person",
        ['select', ['project', ['list', ['id', 'Person'], ['path', ['id', 'Person'], ['id', 'name']]]], ['from', ['as', 'Person', ['id', 'Person']]]],
        "MATCH (Person:Person) RETURN Person AS column1, Person.name AS column2",
        [({'name': 'Jennifer'}, 'Jennifer'), ({'name': 'Michael'}, 'Michael')]
    ),
    (
        "SELECT from_node.n_id, dijkstra(from_node, to_node, 'CONNECT_TO', 'cost'), to_node.n_id FROM g2 AS from_node, g2 AS to_node WHERE from_node.n_id = 0 AND to_node.n_id = 8",
        ['select', 
            ['project', 
                ['list', 
                    ['path', ['id', 'from_node'], ['id', 'n_id']],
                    ['call', 'dijkstra', ['list', ['id', 'from_node'], ['id', 'to_node'], ['lit', "'CONNECT_TO'"], ['lit', "'cost'"]]],
                    ['path', ['id', 'to_node'], ['id', 'n_id']]
                ]
            ],
            ['from', 
                ['inner_join', 
                    ['as', 'from_node', ['id', 'g2']], 
                    ['as', 'to_node',  ['id', 'g2']]
                ]
            ],
            ['where', 
                ['and', 
                    ['=', ['path', ['id', 'from_node'], ['id', 'n_id']], ['lit', 0]], 
                    ['=', ['path', ['id', 'to_node'], ['id', 'n_id']], ['lit', 8]]
                ]
            ]
        ],
        "MATCH (from_node:g2), (to_node:g2) WHERE from_node.n_id = 0 and to_node.n_id = 8 CALL apoc.algo.dijkstra(from_node, to_node, 'CONNECT_TO', 'cost') YIELD path AS path, weight AS weight RETURN from_node.n_id AS column1, path AS column2, weight AS column3, to_node.n_id AS column4",
        [(0, [0, 1, 3, 5, 8], 12.0, 8)]
    )
])

def test_partiql_neo4j(query, ast, cypher, result) :
    # Metadata of Neo4j graph database
    metadata = {
        'relationships' :[
            {'from' : 'Person', 'to' : 'Company', 'type' : 'WORKS_FOR'},
            {'from' : 'employeesWithTuples', 'to' : 'project', 'type' : 'project'}
        ],
        'functions' : [
            {'name' : 'dijkstra', 'original_name' : 'apoc.algo.dijkstra', 'parameters' : ("path", "weight")}
        ]
    }
    # for Neo4j connection
    uri = "bolt://localhost:7687"
    user= "neo4j"
    passwd = "neo4jneo4j"

    pn = partiql_neo4j.PartiqlNeo4j(metadata)
    assert pn.partiql_parse(query) == ast
    assert pn.ast_to_string_cypher(ast) == cypher
    assert pn.execute_query(uri, user, passwd, query)== result
