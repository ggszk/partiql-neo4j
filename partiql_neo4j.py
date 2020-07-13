#
# partiql-neo4j
# simple implementation of PartiQL interface for Neo4j
#
# AST spec: https://github.com/partiql/partiql-lang-kotlin/blob/master/docs/dev/README-AST-V0.md
# We partly use this specification.
# Sorry for using deprecated specification for simple implementation (current version is V1)
#
# Many restrictions of PartiQL

import sys
from Neo4j import Neo4j

# Main Class
class PartiqlNeo4j:
    # Metadata for query translation
    metadata = {'relationships' :[]}
    def __init__(self, metadata):
        self.metadata = metadata

    # execute partiql query
    def execute_query(self, uri, user, passwd, query) :
        ast = parse(query)
        cypher_str = to_string_cypher(ast, self.metadata)
        result = execute_neo4j(uri, user, passwd, cypher_str)
        return result

    # parse patriql to AST
    def partiql_parse(self, query) :
        return parse(query)
    
    # AST to PartiQL
    def ast_to_string_sql(self, ast) :
        return to_string_sql(ast)

    # AST to Cypher
    def ast_to_string_cypher(self, ast) :
        return to_string_cypher(ast, self.metadata)

    # execyte Cypher
    def execute_neo4j(self, uri, user, passwd, cypher_str) :
        return execute_neo4j(uri, user, passwd, cypher_str)

# Parse PatriQL to AST
def parse(sql_str) :
    sql_words = sql_str.split()

    # Very very simple syntax check
    # - 1st word must be 'SELECT'
    if sql_words[0].lower() != 'select' :
        print('Syntax error : missing select', file=sys.stderr)
        sys.exit(1)

    # project
    # find from
    from_idx = -1
    i = 0
    for word in sql_words :
        if word.lower() == "from" : 
            from_idx = i
        i = i + 1
    # no from
    if from_idx == -1 :
        print('Syntax error : missing from', file=sys.stderr)
        sys.exit(1)

    project_expr = ['list']
    project_words = ''.join(sql_words[1:from_idx]).split(',')
    for project_word in project_words :
        project_expr.append(['id', project_word])

    # find where
    where_idx = len(sql_words) # if there is no where, where_idx = len(sql_words)
    i = 0
    for word in sql_words :
        if word.lower() == "where" : 
            where_idx = i
        i = i + 1

    # from
    source_words = sql_words[from_idx+1:where_idx]
    source_string = ' '.join(source_words)
    source_table_strings = source_string.split(',')
    source_tables = []
    for source_table_string in source_table_strings :
        source_tables.append(source_table_string.split())
    source_expr = []

    # from: single table
    if len(source_tables) == 1 :
        source_expr = create_single_source_expr(source_tables[0])
    # from : multi table: only inner join of two tables
    elif len(source_tables) == 2 :
        source_expr = ['inner_join', create_single_source_expr(source_tables[0]), create_single_source_expr(source_tables[1])]
    else :
        print('Syntax error : sorry not to support 3 or above joins', file=sys.stderr)
        sys.exit(1)

    # AST without where clause
    ast = ['select', ['project', project_expr], ['from', source_expr]]

    # where
    if where_idx != len(sql_words) : # there is where clause
        cond_words = sql_words[where_idx+1:]
        cond_expr = ' ' .join(cond_words) # ignore where clause parse
        ast.append(['where', cond_expr])

    return ast

# check and normalize table pattern
def create_single_source_expr(source_words) :
    # parse path expression
    path_strings = source_words[0].split('.')
    if len(path_strings) > 1 :
        path_expr = ['path', ['id', path_strings[0]], ['id', path_strings[1]]]
    else :
        path_expr = ['id' , source_words[0]]
    # Normalize: if there is no 'AS' in the from clause, add 'AS'
    if len(source_words) == 1 :
        # last string of path is used for variable
        source_expr = ['as', path_strings[-1], path_expr]
    # there is AS
    elif len(source_words) == 3 :
        source_expr = ['as', source_words[2], path_expr]
    # incompatible from clause
    else :
        print('Syntax error : from clause', file=sys.stderr)
        sys.exit(1)
    
    return source_expr

# serialize to sql
def to_string_sql(ast) : 
    # project
    select_str = "SELECT "
    project_str = ""
    i = 0
    for list_item in ast[1][1] :
        if i != 0 :
            project_str = project_str + list_item[1] + ","
        i = i + 1
    project_str = project_str[:-1]

    # from
    # not join
    if ast[2][1][0] == 'as' :
        from_str = "FROM " + source_expr_to_string(ast[2][1])
    # join
    elif ast[2][1][0] == 'inner_join' :
        from_str = "FROM " + source_expr_to_string(ast[2][1][1]) + ", " + source_expr_to_string(ast[2][1][2])

    sql = select_str + project_str + " " + from_str

    # where
    if len(ast) > 3 :
        where_str = ast[3][1]
        sql = sql + " WHERE " + where_str

    return sql

# source expr to string
def source_expr_to_string(source_expr) :
    source_string = ""
    # not path
    if source_expr[2][0] == 'id' :
        source_string = source_expr[2][1] + " AS " + source_expr[1]
    # path : only 2 depth
    elif source_expr[2][0] == 'path' :
        source_string = source_expr[2][1][1] + "." + source_expr[2][2][1] + " AS " + source_expr[1]
    else :
        print('to_string error : not supported', file=sys.stderr)
        sys.exit(1)
    return source_string

# serialize to cypher
def to_string_cypher(ast, metadata):
    # match
    # not join
    if ast[2][1][0] == 'as' :
        match_str = "MATCH " + source_expr_to_cy_string(ast[2][1])
    # join
    elif ast[2][1][0] == 'inner_join' :
        # analyze relationship
        # source_expr with "path" will be target node
        # the other source_expr will be source node
        if ast[2][1][1][2][0] == 'path' :
            tatget_source_expr = ast[2][1][1]
            source_source_expr = ast[2][1][2]
        elif ast[2][1][2][2][0] == 'path' :
            tatget_source_expr = ast[2][1][2]
            source_source_expr = ast[2][1][1]
        else :
            print("relationship analyze error : not yet support", file=sys.stderr)
            sys.exit(1)
        # check same variable is used for source node
        if tatget_source_expr[2][1][1] != source_source_expr[1] :
            print("relationship analyze error: inconsistent from clauses", file=sys.stderr)
            sys.exit(1)
        # check the existence of relationship between taget and source
        relationhip_type = tatget_source_expr[2][2][1]
        source_node_label = source_source_expr[2][1]
        target_node_label = find_target_node_label(source_node_label, relationhip_type, metadata)
        if target_node_label == "" :
            print('no relationship found ', file=sys.stderr)
            sys.exit(1)
        # simplifed target
        simplified_target_source_expr = ['as', tatget_source_expr[1], ['id', target_node_label]]

        match_str = "MATCH " + source_expr_to_cy_string(source_source_expr) + "-[:" + relationhip_type + "]->" + source_expr_to_cy_string(simplified_target_source_expr)

    cypher = match_str

    # where
    if len(ast) > 3 : # there is where clause
        where_str = ast[3][1]
        cypher = cypher + " WHERE " + where_str

    # return
    return_str = "RETURN "
    i = 0
    for list_item in ast[1][1] :
        if i != 0 :
            # to avoid cypher restriction : Multiple result columns with the same name are not supported 
            return_str = return_str + list_item[1] + " AS column" + str(i) + ","
        i = i + 1
    return_str = return_str[:-1] # cut last ","

    cypher = cypher + " " + return_str #+ ";"

    return cypher

# source expr to cypher string
def source_expr_to_cy_string(source_expr) :
    source_string = "(" + source_expr[1] + ":" + source_expr[2][1] + ")" 

    return source_string

# find relationship from metadata
def find_target_node_label(from_node, relationship_type, metadata) :
    target_node_label = ""
    for relationship in metadata['relationships'] :
        if relationship['from'] == from_node and relationship['type'] == relationship_type :
            target_node_label =   relationship['to']
    return target_node_label # if not found null string will be returned

# Execute Neo4j
def execute_neo4j(uri, user, passwd, cypher):
    neo4j = Neo4j({
            'uri' : uri,
            'user' : user,
            'passwd' : passwd,
    })
    return neo4j.executeQuery(cypher)
