#
# partiql-neo4j
# simple implementation of PartiQL interface for Neo4j
#
# AST spec: https://github.com/partiql/partiql-lang-kotlin/blob/master/docs/dev/README-AST-V0.md
# We partly use this specification.
# Sorry for using deprecated specification for simple implementation (current version is V1)
#
# Many restrictions of PartiQL

from lark import Lark
from partiql_lang import Build_AST
import sys
from Neo4j import Neo4j

ops = ['=', '!=', '>', '>=', '<', '<=']
cons = ['and', 'or']

# Main Class
class PartiqlNeo4j:
    # Metadata for query translation
    metadata = {'relationships' :[]}
    def __init__(self, metadata):
        self.metadata = metadata

    # execute partiql query
    def execute_query(self, uri, user, passwd, query) :
        ast = self.partiql_parse(query)
        cypher_str = self.ast_to_string_cypher(ast)
        result = self.execute_neo4j(uri, user, passwd, cypher_str)
        return result

    # parse patriql to AST
    def partiql_parse(self, query) :
        rule = open('partiql_grammer.lark').read()
        parser = Lark(rule, start="select", parser='lalr')
        tree = parser.parse(query)
        b = Build_AST()
        ast = b.visit(tree)
        return ast
    
    # AST to PartiQL
    def ast_to_string_sql(self, ast) :
        return ast_to_sql(ast)

    # AST to Cypher
    def ast_to_string_cypher(self, ast) :
        return ast_to_cypher(ast, self.metadata)

    # execyte Cypher
    def execute_neo4j(self, uri, user, passwd, cypher_str) :
        neo4j = Neo4j({
                'uri' : uri,
                'user' : user,
                'passwd' : passwd,
        })
        return neo4j.executeQuery(cypher_str)

# construct SQL
def ast_to_sql(ast) :
    ret_str = ""
    if ast[0] == "select" :
        ret_str = "select " + ast_to_sql(ast[1]) + ast_to_sql(ast[2]) 
        # where clause
        if len(ast) > 3 :
            ret_str = ret_str + ast_to_sql(ast[3]) 
    elif ast[0] == 'project' :
        ret_str = ast_to_sql(ast[1])
    elif ast[0] == 'list' :
        i = 0
        for c in ast :
            if i > 0 :
                ret_str = ret_str + ast_to_sql(c) + ", "
            i = i + 1
        ret_str = ret_str[:-2]
    elif ast[0] == 'call' :
        ret_str = ast[1] + "(" + ast_to_sql(ast[2]) + ")"
    elif ast[0] == 'from' :
        ret_str = " from " + ast_to_sql(ast[1])
    elif ast[0] == 'as' :
        ret_str = ast_to_sql(ast[2]) + " as " + ast[1]
    elif ast[0] == 'inner_join' :
        ret_str = ast_to_sql(ast[1]) + ", " + ast_to_sql(ast[2])    
    elif ast[0] == 'where' :
        ret_str = " where " + ast_to_sql(ast[1])
    elif ast[0] in ops or ast[0] in cons:
        ret_str = ast_to_sql(ast[1]) + " " + ast[0] + " " + ast_to_sql(ast[2])
    elif ast[0] == 'path' :
        ret_str = ast_to_sql(ast[1]) + "." + ast_to_sql(ast[2])
    elif ast[0] == 'lit' :
        if type(ast[1]) == int :
            ret_str = str(ast[1])
        else :
            ret_str = "'" + ast[1] + "'"
    elif ast[0] == 'id' :
        ret_str = ast[1]
    return ret_str

# construct Cypher
def ast_to_cypher(ast, metadata) :
    ret_str = ""
    if ast[0] == "select" :
        ret_str = "MATCH " + ast_to_cypher(ast[2], metadata)
        # where clause
        if len(ast) > 3 :
            ret_str = ret_str + ast_to_cypher(ast[3], metadata) 
        # return clause : list
        i = 0
        col_str = " RETURN "
        column_id = 1 # No of columns
        for c in ast[1][1] :
            # to avoid cypher restriction : Multiple result columns with the same name are not supported
            if c[0] == 'call' :
                call_str = " CALL " + ast_to_cypher(c, metadata)[0]
                yield_str = " YIELD "
                for p in ast_to_cypher(c, metadata)[1] :
                    yield_str = yield_str + p + " AS " + p + ", "
                col_str = call_str + yield_str[:-2] + col_str
                for p in ast_to_cypher(c, metadata)[1] :
                    col_str = col_str + p + " AS column" + str(column_id) + ", "
                    column_id = column_id + 1
            elif i != 0 :
                col_str = col_str + ast_to_cypher(c, metadata) + " AS column" + str(column_id) + ", "
                column_id = column_id + 1
            # function call
            i = i + 1
        ret_str = ret_str + col_str[:-2]
    elif ast[0] == 'project' :
        ret_str = ast_to_cypher(ast[1], metadata)
    elif ast[0] == 'list' :
        i = 0
        for c in ast :
            if i > 0 :
                ret_str = ret_str + ast_to_cypher(c, metadata) + ", "
            i = i + 1
        ret_str = ret_str[:-2]
    elif ast[0] == 'call' :
        # find function from metadata
        for func in metadata['functions'] :
            if func['name'] == ast[1] :
                # get function information from metadata
                func_name = func['original_name']
                func_result_params = func['parameters']
        if func_name == "" :
            print("no such function in metadata", file=sys.stderr)
            sys.exit(1)
        # return tuple not string
        ret_str = (func_name + "(" + ast_to_cypher(ast[2], metadata) + ")", func_result_params)
    elif ast[0] == 'from' :
        ret_str = ast_to_cypher(ast[1], metadata)
    elif ast[0] == 'as' :
        ret_str = "(" + ast[1] + ":" + ast_to_cypher(ast[2], metadata) + ")"
    elif ast[0] == 'inner_join' :
        # analyze relationship
        # no relationship. cartesian product case
        if ast[1][2][0] != 'path' and ast[2][2][0] != 'path' :
            ret_str = ast_to_cypher(ast[1], metadata) + ", " + ast_to_cypher(ast[2], metadata)
        # source_expr with "path" will be target node
        # the other source_expr will be source node
        else :
            if ast[1][2][0] == 'path' :
                tatget_source_expr = ast[1]
                source_source_expr = ast[2]
            elif ast[2][2][0] == 'path' :
                tatget_source_expr = ast[2]
                source_source_expr = ast[1]
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
            ret_str = source_expr_to_cy_string(source_source_expr) + "-[:" + relationhip_type + "]->" + source_expr_to_cy_string(simplified_target_source_expr)
    elif ast[0] == 'where' :
        ret_str = " WHERE " + ast_to_cypher(ast[1], metadata)
    elif ast[0] in ops or ast[0] in cons:
        ret_str = ast_to_cypher(ast[1], metadata) + " " + ast[0] + " " + ast_to_cypher(ast[2], metadata)
    elif ast[0] == 'path' :
        ret_str = ast_to_cypher(ast[1], metadata) + "." + ast_to_cypher(ast[2], metadata)
    elif ast[0] == 'lit' :
        if type(ast[1]) == int :
            ret_str = str(ast[1])
        else :
            ret_str = "'" + ast[1] + "'"
    elif ast[0] == 'id' :
        ret_str = ast[1]
    return ret_str

# find relationship from metadata
def find_target_node_label(from_node, relationship_type, metadata) :
    target_node_label = ""
    for relationship in metadata['relationships'] :
        if relationship['from'] == from_node and relationship['type'] == relationship_type :
            target_node_label =   relationship['to']
    return target_node_label # if not found null string will be returned

# source expr to cypher string
def source_expr_to_cy_string(source_expr) :
    source_string = "(" + source_expr[1] + ":" + source_expr[2][1] + ")" 
    return source_string


