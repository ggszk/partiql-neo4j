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
        ['select', ['project', ['list', ['id', 'jenn.name'], ['id', 'jenn.name']]], ['from', ['as', 'jenn', ['id', 'Person']]]],
        "MATCH (jenn:Person) RETURN jenn.name AS column1,jenn.name AS column2",
        [('Jennifer', 'Jennifer'), ('Michael', 'Michael')]
    ),
    (
        "SELECT jenn FROM Person AS jenn WHERE jenn.name = 'Jennifer'",
        ['select', ['project', ['list', ['id', 'jenn']]], ['from', ['as', 'jenn', ['id', 'Person']]], ['where', "jenn.name = 'Jennifer'"]],
        "MATCH (jenn:Person) WHERE jenn.name = 'Jennifer' RETURN jenn AS column1",
        [({'name': 'Jennifer'},)]
    ),
    (
        "SELECT company.name FROM Person AS p, p.WORKS_FOR AS company WHERE p.name = 'Jennifer'",
        ['select', 
            ['project', ['list', ['id', 'company.name']]], 
            ['from', 
                ['inner_join', 
                    ['as', 'p', ['id', 'Person']], 
                    ['as', 'company', ['path', ['id', 'p'], ['id', 'WORKS_FOR']]]
                ]
            ],
            ['where', "p.name = 'Jennifer'"]
        ],
        "MATCH (p:Person)-[:WORKS_FOR]->(company:Company) WHERE p.name = 'Jennifer' RETURN company.name AS column1",
        [('Neo4j',)]
    ),
    (
        "SELECT Person, Person.name FROM Person",
        ['select', ['project', ['list', ['id', 'Person'], ['id', 'Person.name']]], ['from', ['as', 'Person', ['id', 'Person']]]],
        "MATCH (Person:Person) RETURN Person AS column1,Person.name AS column2",
        [({'name': 'Jennifer'}, 'Jennifer'), ({'name': 'Michael'}, 'Michael')]
    )
])

def test_partiql_neo4j(query, ast, cypher, result) :
    # Metadata of Neo4j graph database
    metadata = {
        'relationships': [
            {'from': 'Person', 'to': 'Company', 'type': 'WORKS_FOR'}
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
