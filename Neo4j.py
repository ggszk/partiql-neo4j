from neo4j import GraphDatabase
from neo4j import Path

# Storage engine for Neo4j
class Neo4j :
    # initialize
    def __init__(self, param):
        self.driver = GraphDatabase.driver(param['uri'], auth=(param['user'], param['passwd']))

    # Execute cypher query
    def executeQuery(self, cypher):
        session = self.driver.session()
        neo_result = session.run(cypher)

        # result for return: list of dict
        result = []

        for neo_record in neo_result:
            # neo_record is an instance of Node or Relationship class
            record = []
            for key in neo_record.keys(): # key means almost column index
                # not object case: string or integer or float
                if type(neo_record[key]) == str or type(neo_record[key]) == int  or type(neo_record[key]) == float :
                    record.append(neo_record[key])
                # Path case
                elif type(neo_record[key]) == Path :
                    node_id_list = []
                    for node in neo_record[key].nodes :
                        # Remark: 'n_id' attribute must be on all nodes which is user defined node id (for ease debug...)
                        node_id_list.append(node.get('n_id'))
                    record.append(node_id_list)                   
                # Node or Relationship case
                else :
                    columns_obj = {}
                    # Python Driver returns a pair of an attribute and a values as 'tuple'!! (as not dict) (items() returns tuples)
                    for item in neo_record[key].items():
                        columns_obj[item[0]] = item[1]
                    record.append(columns_obj)
            result.append(tuple(record))
        session.close()
        return result

