# https://www.postgresql.org/docs/9.2/runtime-config-query.html#RUNTIME-CONFIG-QUERY-CONSTANTS
import psycopg2
import queue
from decouple import config
#check
import time


#

def execute_query(cursor, query):
    # Executing an MYSQL function using the execute() method
    cursor.execute("EXPLAIN (ANALYSE,FORMAT JSON) " + query)
    # Fetch a single row using fetchone() method.
    result = cursor.fetchall()
    print("Results: ", result)
    return result


# Iterate and compare plans
def compare_plans(original_plan, alternate_plan):
    original_plan = original_plan[0][0][0]["Plan"]
    alternate_plan = alternate_plan[0][0][0]["Plan"]
    q1 = queue.Queue()
    q2 = queue.Queue()
    q1.put(original_plan)
    q2.put(alternate_plan)

    while not q1.empty():
        current_plan = q1.get()
        alt_plan = q2.get()
        node_type1 = current_plan["Node Type"]
        node_type2 = alt_plan["Node Type"]
        if (node_type1 == node_type2):
            if "Plans" in current_plan and "Plans" in alt_plan:
                for element in current_plan["Plans"]:
                    # print(element["Node Type"])
                    q1.put(element)
                for element in alt_plan["Plans"]:
                    # print(element["Node Type"])
                    q2.put(element)
            # q1.put(current_plan["Plans"][0])
            # q2.put(alt_plan["Plans"][0])
        else:
            return False
    return True


def generate_aqp(result, cursor, query):
    aqp_list = []
    # method_configuration_list = ["enable_async_append","enable_bitmapscan","enable_hashagg",
    #                              "enable_gathermerge", "enable_hashjoin", "enable_incremental_sort",
    #                              "enable_indexscan", "enable_indexonlyscan", "enable_material",
    #                              "enable_memoize", "enable_mergejoin", "enable_nestloop",
    #                              "enable_parallel_append", "enable_parallel_hash", "enable_partition_pruning",
    #                              "enable_partitionwise_join", "enable_partitionwise_aggregate", "enable_seqscan",
    #                              "enable_sort", "enable_tidscan"
    #                              ]
    method_configuration_list = ["enable_bitmapscan", "enable_hashagg", "enable_hashjoin",
                                 "enable_seqscan", "enable_indexonlyscan",
                                 "enable_nestloop ", "enable_sort", "enable_tidscan",
                                 "enable_indexscan", "enable_mergejoin"
                                 ]
    # method_configuration_list = ["ENABLE_SORT","ENABLE_BITMAPSCAN", "ENABLE_HASHAGG", "ENABLE_HASHJOIN",
    #                              "ENABLE_INDEXSCAN", "ENABLE_INDEXONLYSCAN",
    #                              "ENABLE_MERGEJOIN", "ENABLE_NESTLOOP", "ENABLE_SEQSCAN",
    #                              "ENABLE_TIDSCAN"
    #                             ]
    original_plan = result
    aqp_list.append(original_plan)
    for element in method_configuration_list:
        a = method_configuration_list.index(element)
        if a == 0:
            pass
        else:
            previous_enable = method_configuration_list[a - 1]
            cursor.execute("SET " + previous_enable + " = on")
            #check
            # print("SET " + previous_enable + " = on")

        #check
        start_time = time.time()
        #
        # cursor.execute("SET " + element + " TO OFF; EXPLAIN (ANALYSE,FORMAT JSON) " + query)
        cursor.execute("SET " + element + " = off; EXPLAIN (ANALYSE,FORMAT JSON) " + query)
        alternate_plan = cursor.fetchall()
        print("SET " + element + " = off; EXPLAIN (ANALYSE,FORMAT JSON) " + query)
        #check
        execution_time = time.time() - start_time
        #to check query plans are different
        #print(alternate_plan)
        #check
        print("%s seconds" % (execution_time))
        #
        if not compare_plans(original_plan, alternate_plan):
            aqp_list.append(alternate_plan)
    return aqp_list


if __name__ == "__main__":
    # Need .env file info
    try:
        conn = psycopg2.connect(
             database=config('DATABASE'), user=config('USER'), password=config('PASSWORD'), host=config('HOST'),
             port=config('PORT')
        )
        print("Connected!")
        # Creating a cursor object using the cursor() method
        cursor = conn.cursor()
        # query = " select c_custkey, count(o_orderkey) from customer left outer join orders on c_custkey = o_custkey and
        # o_comment not like '%pending%packages%' group by c_custkey;"
        query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from " \
                "customer, orders, lineitem where c_mktsegment = 'HOUSEHOLD' and c_custkey = o_custkey and l_orderkey = " \
                "o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, " \
                "o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10; "
        result = execute_query(cursor, query)
        aqp_list = generate_aqp(result, cursor, query)
        # print(len(aqp_list))
        conn.close()
    except:
        print("Failed to connect to DB!")

    # Closing the connection
