## list the packages
import json 
import psycopg2 as pg
from zipfile import ZipFile
import pandas as pd
from sqlalchemy import create_engine


## define important variables
schema_json = '/home/agnes/Documents/digital_skola/Project/project_3_de/sql/schemas/user_address.json'
create_schema_sql = """create table user_address_2018_snapshots {};"""
database='shipping_orders'
user='postgres'
password='1234'
host='localhost'
port='5432'
zip_small_file = '/home/agnes/Documents/digital_skola/Project/project_3_de/temp/dataset-small.zip'
small_file_name = 'dataset-small.csv'
table_name = 'user_address_2018_snapshots'
result_ingestion_check_sql = '/home/agnes/Documents/digital_skola/Project/project_3_de/sql/queries/result_ingestion_user_address.sql'


## open table from json
with open(schema_json, 'r') as schema:
    content = json.loads(schema.read())


## create tuples that will create the sql query to create the table
list_schema = []
for c in content:
     col_name = c['column_name']
     col_type = c['column_type']
     constraint = c['is_null_able']
     ddl_list = [col_name, col_type, constraint]
     list_schema.append(ddl_list)

list_schema_2 = []
for l in list_schema:
     s = ' '.join(l)
     list_schema_2.append(s)

create_schema_sql_final = create_schema_sql.format(tuple(list_schema_2)).replace("'", "")


## init to Postgres
conn = pg.connect(database=database,
                  user=user,
                  password=password,
                  host=host,
                  port=port)

conn.autocommit=True
cursor=conn.cursor()

try:
    cursor.execute(create_schema_sql_final)
    print("DDL schema created succesfully...")
except pg.errors.DuplicateTable:
    print("table already created...")


## Load zipped file to dataframe
zf = ZipFile(zip_small_file)
df = pd.read_csv(zf.open(small_file_name), header=None)


## add column name as table header
col_name_df = [c['column_name'] for c in content]
df.columns = col_name_df


## filter necessary data
df_filtered = df[(df['created_at'] >= '2018-02-01') & (df['created_at'] < '2018-12-31')]


## create engine to upload multiple values to table in postgres
engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')


## insert new data to postgres
df_filtered.to_sql(table_name, engine, if_exists='append', index=False) 


## print the result
print(f'Total inserted rows: {len(df_filtered)}')
print(f'Inital created_at: {df_filtered.created_at.min()}')
print(f'Last created_at: {df_filtered.created_at.max()}')


## execute given query 
cursor.execute(open(result_ingestion_check_sql, 'r').read())
result = cursor.fetchall()
print(result)