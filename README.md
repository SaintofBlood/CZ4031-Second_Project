# CZ4031-PostgreSqlQuery-Natural Language Annotater

## About

The PostgresqlQuery Natural Language Annotater is a desktop application built using python with tkinter library. This project aims to provide an algorithm to describe the Query Eexecution Plan (QEP) generated for each query, draw the QEP as a tree structure, describe the difference in QEPs of similar queries and generate the reason of the changing of the QEP.

This project's purpose is to enhance the beginner's learning expereience of realtional database management systems. Through the visualizing the QEP by both text format and tree structure formate, the learner will be albe to get the idea of QEP easier. By providing the difference of the QEP for 2 similari queries and providing the reason of the changes, the learner will be able to have a good understanding of how a optimized QEP is generated.


## Usage

To use this application, you need to run the app/app.py in this project.

Before running this application, you need to satisfy the following dependencies


### Dependencies

This application was built with Python v3.8.5 and uses the dependencies specified in `requirements.txt`. Use the command `pip install -r requirements.txt` to install the latest version of the listed packages.

**Note: We use PyQT5 module to build the GUI and this module should be a built in library. Therefore, no need to install it manually**

### User Maunal

The application (or system) accept two inputs, namely, two SQL queries.

1. Paste the query of `<query>` to the first text field. By running the input, the Postgresql can generate the QEP abd 2 AQPs of the first query.

After inserting the required input, click **"Execute SQL Query"** to see the result

The output of this system contains 4 parts:
1. The natural language description of the QEPs

2. The tree structure of the QEPs

3. The difference between the two QEP, if these two queries's execution plans are comparable

4. The reason of the differerence, if any

### Sample Queries

There are 6 set of sample test queries available in this project.

To use the sample queries, for example, query_1, simply go to the dropdown and exxecute the desired sample query. 
### Example

#### Input
1. First Query

```sql
SELECT *
FROM 
     orders,
     customer
WHERE
     c_custkey = o_custkey
AND
     c_name = 'Name'
ORDER BY
      c_phone  
```

#### Output(Result)

1. Natural Language Description

Description of Query A
```
The query is executed as follow.
Step 1, perform sequential scan on table orders.
Step 2, perform sequential scan on table customer and filtering on (c_name) text = 'Name' text to get intermediate table T1.
Step 3, hash table T1 and perform hash join on table orders and table T1 under condition orders.o_custkey = customer.c_custkey to get intermediate table T2.
Step 4, perform sort on table T2 with attribute customer.c_phone to get intermediate table T3.
Step 5, perform gather merge on table T3 to get the final result.
```

Description of Query B
```
The query is executed as follow.
Step 1, perform sequential scan on table orders.
Step 2, perform index scan on table customer with index customer_pkey and filtering on (c_name) text = 'Name' text to get intermediate table T1.
Step 3, hash table T1 and perform hash join on table orders and table T1 under condition orders.o_custkey = customer.c_custkey to get intermediate table T2.
Step 4, perform sort on table T2 with attribute customer.c_phone to get intermediate table T3.
Step 5, perform gather merge on table T3 to get the final result.
```

2. Tree Structure Description

Tree Structure of QEP and AQP of Query A
- Displayed using the blockdialog library

3. Description of the Difference

```
Difference 1 : hash table T1 and hash join on table orders and table T1 under condition orders.o_custkey = customer.c_custkey to get intermediate table T2 has been changed to nested loop on table orders, and table T1 to get intermediate table T2

Difference 2 : sequential scan on table customer and filtering on (c_name) text = 'Name' text to get intermediate table T1 has been changed to bitmap heap scan on table customer with index condition c_custkey = orders.o_custkey and filtering on (c_name) text = 'Name' text to get intermediate table T1
```

4. Explanation

```
Reason for Difference 1: Hash Join in P1 on has now evolved to Nested Loop in P2 on relation . This is because Hash joins generally have a higher cost to retrieve the first row than nested-loop joins do as Postgres must build the hash table before it retrieves any rows. 

Reason for Difference 2: Sequential Scan in P1 on relation customer has now evolved to Bitmap Heap Scan in P2 on relation customer. This is because Bitmap heap scan means that PostgreSQL has found a small subset of rows to fetch (e.g., from an index), and is going to fetch only those rows. This will of course have a lot more seeking, so is faster only when it needs a small subset of the rows compared to Sequential Scan when majority of rows are used. 
```

The output actually is the combination of the difference and its explanation
```
Difference 1 : hash table T1 and hash join on table orders and table T1 under condition orders.o_custkey = customer.c_custkey to get intermediate table T2 has been changed to nested loop on table orders, and table T1 to get intermediate table T2

Reason for Difference 1: Hash Join in P1 on has now evolved to Nested Loop in P2 on relation . This is because Hash joins generally have a higher cost to retrieve the first row than nested-loop joins do as Postgres must build the hash table before it retrieves any rows. 

Difference 2 : sequential scan on table customer and filtering on (c_name) text = 'Name' text to get intermediate table T1 has been changed to bitmap heap scan on table customer with index condition c_custkey = orders.o_custkey and filtering on (c_name) text = 'Name' text to get intermediate table T1

Reason for Difference 2: Sequential Scan in P1 on relation customer has now evolved to Bitmap Heap Scan in P2 on relation customer. This is because Bitmap heap scan means that PostgreSQL has found a small subset of rows to fetch (e.g., from an index), and is going to fetch only those rows. This will of course have a lot more seeking, so is faster only when it needs a small subset of the rows compared to Sequential Scan when majority of rows are used. 
```

## Report
