import partiql_neo4j

# for Neo4j connection
uri = "bolt://localhost:7687"
user= "neo4j"
passwd = "neo4jneo4j"

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
#sql_str = "SELECT p FROM Person AS p"
#sql_str = "SELECT Person FROM Person"
#sql_str = "SELECT jenn.name, jenn.name FROM Person AS jenn"
#sql_str = "SELECT jenn FROM Person AS jenn WHERE jenn.name = 'Jennifer'"
#sql_str = "SELECT company.name FROM Person AS p, p.WORKS_FOR AS company WHERE p.name = 'Jennifer'"
#sql_str = "SELECT Person, Person.name FROM Person"
#sql_str = "SELECT e.name AS employeeName, e.project.name AS projectName FROM employeesWithTuples e WHERE e.project.org = 'AWS'" # to be implemented...
sql_str = "SELECT from_node.n_id, dijkstra(from_node, to_node, 'CONNECT_TO', 'cost'), to_node.n_id FROM g2 AS from_node, g2 AS to_node WHERE from_node.n_id = 0 and to_node.n_id = 8"

# Query execution sample
pn = partiql_neo4j.PartiqlNeo4j(metadata)
#result = pn.execute_query(uri, user, passwd, sql_str)
#print(result)

# Parse and translation example
ast = pn.partiql_parse(sql_str)
print(ast)
ast_answer = [
    'select', 
        ['project', 
            ['list', 
                ['id', 'from_node.n_id'],
                ['call', 'dijkstra', ['list', ['id', 'from_node'], ['id', 'to_node'], ['lit', "'CONNECT_TO'"], ['lit', "'cost'"]]],
                ['id', 'to_node.n_id']
            ]
        ],
        ['from', 
            ['inner_join', 
                ['as', 'from_node', ['id', 'g2']], 
                ['as', 'to_node',  ['id', 'g2']]
            ]
        ],
        ['where', "from_node.n_id = 0 and to_node.n_id = 8"]
]
cypher_answer = "MATCH (from_node:g2), (to_node:g2) WHERE from_node.n_id = 0 and to_node.n_id = 8 CALL apoc.algo.dijkstra(from_node, to_node, 'CONNECT_TO', 'cost') yield path as path, weight as weight RETURN path, weight"

query = pn.ast_to_string_sql(ast)
print(query) # sql translation don't pass function pattern
cypher_str = pn.ast_to_string_cypher(ast)
##cypher_str = "match (n)-[:LIKES]->(m) where id(n) = 0 return id(m)" # for test
print(cypher_str)

# cypher execute example
result_neo4j = pn.execute_neo4j(uri, user, passwd, cypher_str)
print(result_neo4j)
