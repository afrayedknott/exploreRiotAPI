from typing import final
import json
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import psycopg2
import uuid
import os

class SqlHandler:
    # Create a global psql connection object
    def __init__(self, json_fp):
        
        # refactor to be able to swap between instantiating off json file or a set of user, pw, db, host, port parameters
        # look into dynamic class instantiating or class factories
        with open(json_fp, mode="r") as json_file:
            # Store credentials to the global namespace
            global credentials
            credentials = json.load(json_file)
            self.user = credentials["user"]
            self.password = credentials["password"]
            self.database = credentials["database"]
            self.host = credentials["host"]
            self.port = credentials["port"]
            self.engine = None

    def establish_connection(self):
        try:
            self.engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}'
                                    .format(credentials["user"],
                                            credentials["password"],
                                            credentials["host"],
                                            credentials["port"],
                                            credentials["database"]
                                            )
                                    )
            print('Engine created')

        except Exception as ex:
                print('Exception:')
                print(ex)

        print("User {0} connected to {1}.".format(self.user, self.database))
        
    def upsert_df(self, df, table_name):
        """Implements the equivalent of pd.DataFrame.to_sql(..., if_exists='update')
        (which does not exist). Creates or updates the db records based on the
        dataframe records.
        Conflicts to determine update are based on the dataframes index.
        This will set unique keys constraint on the table equal to the index names
        1. Create a temp table from the dataframe
        2. Insert/update from temp table into table_name
        Returns: True if successful
        """

        # If the table does not exist, we should just use to_sql to create it
        with self.engine.connect() as connection:
            
            sql_t = text(f"""SELECT FROM information_schema.tables 
                    WHERE  table_schema = 'public';""")

            table_schema = connection.execute(sql_t)
            print(table_schema.all())

            if not connection.execute(
                f"""SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE  table_schema = 'public'
                    AND    table_name   = '{table_name}');
                    """
            ).first()[0]:
                df.to_sql(table_name, connection)
                return True

        # If it already exists...
        with self.engine.connect() as connection:
            temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
            df.to_sql(temp_table_name, connection, index=True)

            index = list(df.index.names)
            print(*index)
            index_sql_txt = ", ".join([f'"{i}"' for i in index])
            print(index_sql_txt)
            columns = list(df.columns)
            print(columns)
            headers = index + columns
            print(headers)
            headers_sql_txt = ", ".join(
                [f'"{i}"' for i in headers]
            )  # index1, index2, ..., column 1, col2, ...
            print(headers_sql_txt)

            # col1 = exluded.col1, col2=excluded.col2
            update_column_stmt = ", ".join([f'"{col}" = EXCLUDED."{col}"' for col in columns])
            print(update_column_stmt)

            # For the ON CONFLICT clause, postgres requires that the columns have unique constraint
            query_pk = f"""
            ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert;
            ALTER TABLE "{table_name}" ADD CONSTRAINT unique_constraint_for_upsert UNIQUE ({index_sql_txt});
            """
            connection.execute(query_pk)

            # Compose and execute upsert query
            query_upsert = f"""
            INSERT INTO "{table_name}" ({headers_sql_txt}) 
            SELECT {headers_sql_txt} FROM "{temp_table_name}"
            ON CONFLICT ({index_sql_txt}) DO UPDATE 
            SET {update_column_stmt};
            """
            connection.execute(query_upsert)
            connection.execute(f"DROP TABLE {temp_table_name}")

            return True

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


