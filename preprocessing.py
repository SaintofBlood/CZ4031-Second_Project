# https://www.postgresql.org/docs/9.2/runtime-config-query.html#RUNTIME-CONFIG-QUERY-CONSTANTS
import psycopg2
import queue
from decouple import config

def execute_originalquery(cursor,query):
   #Executing an MYSQL function using the execute() method
   cursor.execute("EXPLAIN (ANALYSE,FORMAT JSON) " + query)
   # Fetch a single row using fetchone() method.
   result = cursor.fetchall()
   # print("Results: ", result)
   return result

# Iterate and compare plans, return True if same , false if different
def compare_plans(original_plan, alternate_plan):
   original_plan = original_plan[0][0][0]["Plan"]
   alternate_plan = alternate_plan[0][0][0]["Plan"]
   # if same cost just abort, dont need to check, confirm same plan 
   if (original_plan["Total Cost"] == alternate_plan["Total Cost"]): 
      return True
   # if not
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
      else: return False
   return True

def check_for_join(original_plan):
   original_plan = original_plan[0][0][0]["Plan"]
   q1 = queue.Queue()
   q1.put(original_plan)
   while not q1.empty():
      current_plan = q1.get()
      if "Join" in current_plan["Node Type"]:
         return True
      else:
         for element in current_plan["Plans"]:
                  q1.put(element)
   
   return False

def iterating_alternate_config_list(plans_list,original_plan,cursor,query,conn,off_config,on_config, have_join):
   #Alternate plans (Max: 10)
   #Checking for AEP for Joins
   if have_join:
      #Full Merge Join
      plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Nested Loop", "Hash Join"])
      if(plan != "error" and not compare_plans(original_plan,plan)):
         print("plan added")
         plans_list.append(plan)
         
      #Full hash join
      plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ['Nested Loop', "Merge Join"])
      if(plan != "error" and not compare_plans(original_plan,plan)):
         print("plan added")
         plans_list.append(plan)

      #Full nested loop join
      plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ['Merge Join', "Hash Join"])
      if(plan != "error" and not compare_plans(original_plan,plan)):
         print("plan added")
         plans_list.append(plan)

   #Checking for AEP for Scans
   #Seq scan 
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Index Scan", "Bitmap Scan", "Index Only Scan", "Tid Scan"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)

   # Index Scan
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Seq Scan", "Bitmap Scan", "Index Only Scan", "Tid Scan"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)
   # Bitmap Scan
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Seq Scan", "Index Scan", "Index Only Scan", "Tid Scan"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)
   
   # Index Only Scan
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Seq Scan", "Index Scan", "Bitmap Scan", "Tid Scan"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)

   # Tid Only Scan
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Seq Scan", "Index Scan", "Bitmap Scan", "Index Only Scan"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)

   # Checking for AEP for Sort
   # Sort
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Sort"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)

   # Checking for AEP for Others
   # No Hash Agg
   plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Hash Agg"])
   if(plan != "error" and not compare_plans(original_plan,plan)):
      print("plan added")
      plans_list.append(plan)

   # # No Material
   # plan = execute_alternatequery(conn,cursor,query,off_config, on_config, ["Material"])
   # if(plan != "error" and not compare_plans(original_plan,plan)):
   #       plans_list.append(plan)
   return plans_list

def execute_alternatequery(conn,cursor,query,off_config, on_config,off=[]):
   try:  
      # 5s timeout   
      cursor.execute("set statement_timeout = 5000")
      #Setting off for alternate query plans
      for condition in off:
         cursor.execute(off_config[condition])
   
      cursor.execute(query)
      alternate_plan = cursor.fetchall()

      # Setting config back on to set up for next alternate query plan
      for condition in off:
            cursor.execute(on_config[condition])
      return alternate_plan
            
   except(Exception, psycopg2.DatabaseError) as error:
      # Check error
      print("Your error: ", error)
      conn.rollback()
      return "error"


def generate_aqp(original_plan,cursor,query,conn,have_join):
   plans_list = []

   # if have join use full config list
   if have_join: 
      off_config = {
        # Joins
        "Hash Join" : "set enable_hashjoin=off",
        "Merge Join" : "set enable_mergejoin=off",
        "Nested Loop" : "set enable_nestloop=off",
        # Scans
        "Seq Scan" : "set enable_seqscan=off",
        "Index Scan" : "set enable_indexscan=off",
        "Bitmap Scan": "set enable_bitmapscan=off",
        "Index Only Scan": "set enable_indexonlyscan=off",
        "Tid Scan": "set enable_tidscan=off",
        # Sort
        "Sort" : "set enable_sort=off",
        #Others
        "Hash Agg": "set enable_hashagg=off",
      }
      on_config = {
         # Joins
         "Hash Join" : "set enable_hashjoin=on",
         "Merge Join" : "set enable_mergejoin=on",
         "Nested Loop" : "set enable_nestloop=on",
         # Scans
         "Seq Scan" : "set enable_seqscan=on",
         "Index Scan" : "set enable_indexscan=on",
         "Bitmap Scan": "set enable_bitmapscan=on",
         "Index Only Scan": "set enable_indexonlyscan=on",
         "Tid Scan": "set enable_tidscan=on",
         # Sort
         "Sort" : "set enable_sort=on",
         #Others
         "Hash Agg": "set enable_hashagg=on",
      }

   # Else shrink list
   else:
      off_config = {
         # Scans
        "Seq Scan" : "set enable_seqscan=off",
        "Index Scan" : "set enable_indexscan=off",
        "Bitmap Scan": "set enable_bitmapscan=off",
        "Index Only Scan": "set enable_indexonlyscan=off",
        "Tid Scan": "set enable_tidscan=off",
        # Sort
        "Sort" : "set enable_sort=off",
        #Others
        "Hash Agg": "set enable_hashagg=off",
      }
      on_config = {
         # Scans
         "Seq Scan" : "set enable_seqscan=on",
         "Index Scan" : "set enable_indexscan=on",
         "Bitmap Scan": "set enable_bitmapscan=on",
         "Index Only Scan": "set enable_indexonlyscan=on",
         "Tid Scan": "set enable_tidscan=on",
         # Sort
         "Sort" : "set enable_sort=on",
         #Others
         "Hash Agg": "set enable_hashagg=on",
      }

   # add original plan to list
   plans_list.append(original_plan)
   # print(plans_list)
   query = "EXPLAIN (FORMAT JSON) " + query
   # Iterate to off configs
   plans_list = iterating_alternate_config_list(plans_list,original_plan,cursor,query,conn,off_config,on_config, have_join)
   return plans_list

def repackage_output(plans_list):
   new_plan_list=[]
   for element in plans_list:
      new_plan_list.append(element[0][0][0])
   return new_plan_list


if __name__ == "__main__":
   # Need .env file info / take input from interface.py
   # Need to take in query from interface.py
   try:
      conn = psycopg2.connect(
         database=config('DATABASE'), user=config('USER'), password=config('PASSWORD'), host=config('HOST'), port= config('PORT')
      )
      print("Connected!")
   except:
      print("Failed to connect to DB!")
   #Creating a cursor object using the cursor() method
   cursor = conn.cursor()
   # query = " select c_custkey, count(o_orderkey) from customer left outer join orders on c_custkey = o_custkey and o_comment not like '%pending%packages%' group by c_custkey;"
   query = "select l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority from customer, orders, lineitem where c_mktsegment = 'HOUSEHOLD' and c_custkey = o_custkey and l_orderkey = o_orderkey and o_orderdate < date '1995-03-21' and l_shipdate > date '1995-03-21' group by l_orderkey, o_orderdate, o_shippriority order by revenue desc, o_orderdate limit 10; "
   result = execute_originalquery(cursor,query)
   # if no join in QEP, shrink off and on config list
   if check_for_join(result): 
      plans_list = generate_aqp(result,cursor,query,conn,True)
   else: plans_list = generate_aqp(result,cursor,query,conn,False)
   # For checking
   # for element in plans_list:
   #    print(element)
   #    print("-----------------------------------")
   plans_list = repackage_output(plans_list)
   # For checking
   for element in plans_list:
      print(element)
      print("-----------------------------------")
   #Closing the connection
   conn.close()
