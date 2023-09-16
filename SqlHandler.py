from typing import final
import json
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import psycopg2
import uuid

class SqlHandler:
    # Create a global psql connection object
    def __init__(self, json_fp):
        
        # refactor to be able to swap between instantiating from
        # json file or a set of user, pw, db, host, port parameters
        # look into dynamic class instantiating or class factories
        with open(json_fp, mode="r") as json_file:
            # Store credentials to the global namespace
            self.credentials = json.load(json_file)
            self.user = self.credentials["user"]
            self.password = self.credentials["password"]
            self.database = self.credentials["database"]
            self.host = self.credentials["host"]
            self.port = self.credentials["port"]
        self.engine = None
        self.establish_connection()

    def establish_connection(self):
        try:
            self.engine = \
                create_engine('postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'
                              .format(self.credentials["user"],
                                      self.credentials["password"],
                                      self.credentials["host"],
                                      self.credentials["port"],
                                      self.credentials["database"]
                                      )
                              )
            print('Engine created')

        except Exception as ex:
                print('Exception:')
                print(ex)

        print("User {0} connected to {1}.".\
              format(self.user, self.database))

    def get_dbs(self):
        with self.engine.connect() as connection:   
           sql_text = """
           SELECT datname FROM pg_database 
           WHERE datistemplate = false;
           """.format("")
           result = connection.execute(sql_text)
           dbnames  = [row[0] for row in result]
           print(dbnames)
       
    def get_tbls(self, db):
        with self.engine.connect() as connection:   
           sql_text = """
           SELECT table_name FROM information_schema.tables 
           WHERE table_schema='public' AND table_type='BASE TABLE';
           """.format("")
           result = connection.execute(sql_text)
           tblnames  = [row[0] for row in result]
           print(tblnames)
    
    def get_cols(self, db):
        with self.engine.connect() as connection:   
           sql_text = """
           SELECT table_name FROM information_schema.tables 
           WHERE table_schema='public' AND table_type='BASE TABLE';
           """.format("")
           result = connection.execute(sql_text)
           tblnames  = [row[0] for row in result]
           print(tblnames)
    # def upload_data(self, data, schema, tbl_name, unique_col, drop_cols):
    #     pd.to_sql(data, schema=schema, name=tbl_name, index=False, if_exists='append')
    #     #sql_str = f"""CREATE TABLE {schema}.{tbl_name};"""
    #     #with self.engine.connect() as connection:
    #     #    connection.execute(sql_str)
        
    # def create_new_temp_table(self, schema, tbl_name, unique_col, drop_cols):
    #     sql_str = f"""CREATE TEMP TABLE {schema}.{tbl_name};"""
    #     with self.engine.connect() as connection:
    #         connection.execute(sql_str)

    # def delete_table(self, schema, tbl_name):
    #     sql_str = text(f"""DROP TABLE {schema}.{tbl_name};""")
    #     with self.engine.connect() as connection:
    #         connection.execute(sql_str)

    # def upsert_df(self, df, schema, tbl_name, primary_col=None, drop_cols=None, index_fl=False):
    #     """Implements the equivalent of pd.DataFrame.to_sql(..., if_exists='update')
    #     (which does not exist). Creates or updates the db records based on the
    #     dataframe records.
    #     Conflicts to determine update are based on the dataframes index.
    #     This will set unique keys constraint on the table equal to the index names
    #     1. Create a temp table from the dataframe
    #     2. Insert/update from temp table into table_name
    #     Returns: True if successful
    #     """

    #     #drop designated cols from the dataframe
    #     for drop_col in drop_cols:
    #         if drop_col in list(df):
    #             df = df.drop(drop_col, axis=1)
    #             print("Dropped:"+ drop_col)
    #         else:
    #             print(drop_col + "does not exist to drop.")

    #     if not sa.inspect(self.engine).dialect.has_table(self.engine.connect(), tbl_name): #check if table exists
    #         #create new table
    #         if index_fl:
    #             df.to_sql(con=self.engine, schema=schema, name=tbl_name, index=index_fl, index_label='index')
    #         else:
    #             df.to_sql(con=self.engine, schema=schema, name=tbl_name, index=index_fl)
    #         #set primary
    #         if primary_col is not None:
    #             set_primary_sql_str = f"""
    #                 ALTER TABLE {schema}.{tbl_name} ADD CONSTRAINT primaryKey PRIMARY KEY ({primary_col});
    #                 """
    #             with self.engine.connect() as connection:
    #                     connection.execute(set_primary_sql_str)
    #         else: pass
    #     else:
    #         # create temp table with data
    #         # use temp table to append
    #         # use temp table to update
    #         # remove temp table
    #         with self.engine.connect() as connection:
    #             temp_table_name = tbl_name + "_tmp"
    #             if index_fl:
    #                 df.to_sql(con=self.engine, schema=schema, name=temp_table_name, index=index_fl, index_label='index')
    #             else:
    #                 df.to_sql(con=self.engine, schema=schema, name=temp_table_name, index=index_fl)

    #             index = list(df.index.names)
    #             index_sql_txt = ", ".join([f'"{i}"' for i in index])
    #             columns = list(df.columns)
    #             headers = index + columns
    #             headers_sql_txt = ", ".join(
    #                 [f'"{i}"' for i in headers]
    #             )  # index1, index2, ..., column 1, col2, ...
    #             print(headers_sql_txt)

    #             # col1 = exluded.col1, col2=excluded.col2
    #             update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
    #             print(update_column_stmt)

    #             # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
    #             query_pk = f"""
    #             ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert;
    #             ALTER TABLE "{table_name}" ADD CONSTRAINT unique_constraint_for_upsert UNIQUE ({index_sql_txt});
    #             """
    #             connection.execute(query_pk)

    #             # Compose and execute upsert query
    #             query_upsert = f"""
    #             INSERT INTO "{table_name}" ({headers_sql_txt}) 
    #             SELECT {headers_sql_txt} FROM "{temp_table_name}"
    #             ON CONFLICT ({index_sql_txt}) DO UPDATE 
    #             SET {update_column_stmt};
    #             """
    #             connection.execute(query_upsert)
    #             connection.execute(f"DROP TABLE {temp_table_name}")

    #             return True

#class Load:
#    @classmethod
#    # One-step create table from pandas df
#    def create_and_load(cls, data, tablename): 
#        try:
#            # Create sqlalchemy engine for pandas df.to_sql function
#            engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}/{3}'
#                                    .format(credentials["user"],
#                                            credentials["password"],
#                                            credentials["host"],
#                                            credentials["database"]
#                                            )
#                                  )
#        except Exception as ex:
#            print('Exception:')
#            print(ex)
#        try:
#            # Read csv and do not include index column
#            df = pd.read_csv(data,index_col=False)
#            # Do not store into postgres with an index column
#            df.to_sql("{0}".format(tablename), con=engine, index=False)
#            print("Created table: {0}".format(tablename))
#        except Exception as ex:
#            print('Exception:')
#            print(ex)
#        connection.commit()
#    @classmethod
#    # One-step drop table
#    def drop(cls, table):
#        cursor = connection.cursor()
#        cursor.execute("""
#        DROP TABLE IF EXISTS {0}  
#        """.format(table)
#        )
#        connection.commit()
#        cursor.close()
#        print("Dropped table: {0}".format(table))
#class Query:
#    @classmethod
#    # Retrieve column names in given table
#    def get_columns(cls, table):
#        cursor = connection.cursor()
#        cursor.execute("""
#        SELECT * FROM {0} LIMIT 0    
#        """.format(table)
#        )
#        colnames = [desc[0] for desc in cursor.description]
#        cursor.close()
#        return(colnames)
#    @classmethod
#    # Return subset of table
#    def get_sample(cls, table, num_records):
#        cursor = connection.cursor()
#        cursor.execute("""
#        SELECT * FROM {0} LIMIT {1}    
#        """.format(table, num_records)
#        )
#        result = cursor.fetchall()
#        cursor.close()
#        columns = Query.get_columns(table)
#        df = pd.DataFrame(result, columns=columns)
#        return(df)
#    @classmethod
#    # Get all records
#    def fetchall(cls, table):
#        cursor = connection.cursor()
#        cursor.execute("""
#        SELECT * FROM {0}
#        """.format(table))     
#        result = cursor.fetchall()
#        colnames = [desc[0] for desc in cursor.description]
#        cursor.close()
#        df = pd.DataFrame(result, columns=colnames)
#        return(df)
#    @classmethod
#    # Basic query
#    def query(cls, query):
#        cursor = connection.cursor()
#        cursor.execute("""
#        {0}
#        """.format(query))     
#        result = cursor.fetchall()
#        colnames = [desc[0] for desc in cursor.description]
#        cursor.close()
#        df = pd.DataFrame(result, columns=colnames)
#        return(df)
#class Meta:
#    @classmethod
#    # See all tables in DB instance
#    def get_tables(cls):
#        cursor = connection.cursor()
#        cursor.execute("""
#        SELECT table_name FROM information_schema.tables
#        WHERE table_schema = 'public'
#        """)
#        result = cursor.fetchall()
#        cursor.close()
#        if len(result) < 1:
#            result = "There are no tables in this database"
#        return(result)


