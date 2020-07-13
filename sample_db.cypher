# sample graph database for Neo4j
# please execute these in Neo4j Browser
# Remark: you must check 'Enable multi statement query editor' option in Neo4j Browser setting for executing these queries at once

# Sample in Neo4j tutorial
CREATE (p:Person {name:'Jennifer'});
CREATE (p:Person {name:'Michael'});
MATCH (p1:Person {name:'Jennifer'}),(p2:Person {name:'Michael'}) CREATE (p1)-[:IS_FRIENDS_WITH {since:'2018'}]->(p2);
MATCH (p:Person {name:'Jennifer'}) CREATE (p)-[:LIKES]->(t:Technology {type:'Graphs'});
MATCH (p:Person {name:'Jennifer'}) CREATE (p)-[:WORKS_FOR]->(t:Company {name:'Neo4j'});

# Sample in PartiQL tutorial (to be tested...)
CREATE (p:employeesWithTuples {id:3, name:'Bob Smith'});
CREATE (p:employeesWithTuples {id:6, name:'Jane Smith', title: 'Software Eng 2'});
MATCH (p:employeesWithTuples {name:'Bob Smith'}) CREATE (p)-[:project]->(t:project {name:'AWS Redshift Spectrum querying', org: 'AWS'});
MATCH (p:employeesWithTuples {name:'Jane Smith'}) CREATE (p)-[:project]->(t:project {name:'AWS Redshift security', org: 'AWS'});

# Sample for dijkstra
CREATE (n:g2 {n_id:0, interest:0});
CREATE (n:g2 {n_id:1, interest:0});
CREATE (n:g2 {n_id:2, interest:0});
CREATE (n:g2 {n_id:3, interest:1});
CREATE (n:g2 {n_id:4, interest:0});
CREATE (n:g2 {n_id:5, interest:0});
CREATE (n:g2 {n_id:6, interest:0});
CREATE (n:g2 {n_id:7, interest:0});
CREATE (n:g2 {n_id:8, interest:0});
CREATE (n:g2 {n_id:9, interest:1});
MATCH (n1:g2 {n_id:0}),(n2:g2 {n_id:1}) CREATE (n1)-[:CONNECT_TO {cost:3}]->(n2);
MATCH (n1:g2 {n_id:0}),(n2:g2 {n_id:9}) CREATE (n1)-[:CONNECT_TO {cost:6}]->(n2);
MATCH (n1:g2 {n_id:0}),(n2:g2 {n_id:2}) CREATE (n1)-[:CONNECT_TO {cost:4}]->(n2);
MATCH (n1:g2 {n_id:1}),(n2:g2 {n_id:3}) CREATE (n1)-[:CONNECT_TO {cost:5}]->(n2);
MATCH (n1:g2 {n_id:1}),(n2:g2 {n_id:0}) CREATE (n1)-[:CONNECT_TO {cost:3}]->(n2);
MATCH (n1:g2 {n_id:2}),(n2:g2 {n_id:0}) CREATE (n1)-[:CONNECT_TO {cost:4}]->(n2);
MATCH (n1:g2 {n_id:2}),(n2:g2 {n_id:4}) CREATE (n1)-[:CONNECT_TO {cost:6}]->(n2);
MATCH (n1:g2 {n_id:2}),(n2:g2 {n_id:7}) CREATE (n1)-[:CONNECT_TO {cost:3}]->(n2);
MATCH (n1:g2 {n_id:3}),(n2:g2 {n_id:1}) CREATE (n1)-[:CONNECT_TO {cost:5}]->(n2);
MATCH (n1:g2 {n_id:3}),(n2:g2 {n_id:5}) CREATE (n1)-[:CONNECT_TO {cost:2}]->(n2);
MATCH (n1:g2 {n_id:3}),(n2:g2 {n_id:6}) CREATE (n1)-[:CONNECT_TO {cost:1}]->(n2);
MATCH (n1:g2 {n_id:4}),(n2:g2 {n_id:2}) CREATE (n1)-[:CONNECT_TO {cost:6}]->(n2);
MATCH (n1:g2 {n_id:5}),(n2:g2 {n_id:3}) CREATE (n1)-[:CONNECT_TO {cost:2}]->(n2);
MATCH (n1:g2 {n_id:5}),(n2:g2 {n_id:8}) CREATE (n1)-[:CONNECT_TO {cost:2}]->(n2);
MATCH (n1:g2 {n_id:6}),(n2:g2 {n_id:3}) CREATE (n1)-[:CONNECT_TO {cost:1}]->(n2);
MATCH (n1:g2 {n_id:7}),(n2:g2 {n_id:2}) CREATE (n1)-[:CONNECT_TO {cost:3}]->(n2);
MATCH (n1:g2 {n_id:8}),(n2:g2 {n_id:5}) CREATE (n1)-[:CONNECT_TO {cost:2}]->(n2);
MATCH (n1:g2 {n_id:8}),(n2:g2 {n_id:9}) CREATE (n1)-[:CONNECT_TO {cost:7}]->(n2);
MATCH (n1:g2 {n_id:9}),(n2:g2 {n_id:0}) CREATE (n1)-[:CONNECT_TO {cost:6}]->(n2);
MATCH (n1:g2 {n_id:9}),(n2:g2 {n_id:8}) CREATE (n1)-[:CONNECT_TO {cost:7}]->(n2);