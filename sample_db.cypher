# sample graph database for Neo4j
# please execute these in Neo4j Browser
# Remark: you must check 'Enable multi statement query editor' option in Neo4j Browser setting for executing these queries at once

CREATE (p:Person {name:'Jennifer'});
CREATE (p:Person {name:'Michael'});
MATCH (p1:Person {name:'Jennifer'}),(p2:Person {name:'Michael'}) CREATE (p1)-[:IS_FRIENDS_WITH {since:'2018'}]->(p2);
MATCH (p:Person {name:'Jennifer'}) CREATE (p)-[:LIKES]->(t:Technology {type:'Graphs'});
MATCH (p:Person {name:'Jennifer'}) CREATE (p)-[:WORKS_FOR]->(t:Company {name:'Neo4j'});