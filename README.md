# PartiQL-Neo4j

## Overview

* Simple implementation for accessing Neo4j using PartiQL
* Parse PartiQL -> AST -> translate to Cypher -> execute Cypher in Neo4j
* AST spec: https://github.com/partiql/partiql-lang-kotlin/blob/master/docs/dev/README-AST-V0.md
* We partly use this specification.
* Sorry for using deprecated specification for simple implementation (current version is V1)

## Environments

* Neo4j 3.5.18
* Neo4j Bolt Driver 1.7.1 for Python
* neobolt 1.7.17

## Restriction of PartiQL

* many!

## Usage

* Please check example.py
* Passed samples of PartiQL, AST, and Cypher are in test_pariql_neo4j.py
* Neo4j database for above examples can be created by executing cypher queries in sample_db.cypher.
