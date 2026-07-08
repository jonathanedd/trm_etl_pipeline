import pandas as pd
from sodapy import Socrata
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os


load_dotenv()

#DATA EXTRACTION FROM SOCIETY API 
def data_extract_trm():
   domain = os.getenv("API_DOMAIN")
   dataset_id = os.getenv("API_DATASET_ID")

   token = os.getenv("API_TOKEN")
   if token == "":
       token = None

   limit_rows = int(os.getenv("LIMIT", 30000000))

   if not domain or not dataset_id:
        raise ValueError("¡Error! No 'API_DOMAIN' or 'API_DATASET_ID' found in .env")

   client = Socrata(domain, token)
   results = client.get(dataset_id, limit=limit_rows)
   results_df = pd.DataFrame.from_records(results)

   return results_df

#DATA TRANSFORMATION FOR COLUMNS VALOR AND VIGENCIADESDE
def data_transf_trm(trm):
    trm['valor'] = trm['valor'].astype(float)
    trm['vigenciadesde'] = pd.to_datetime(trm['vigenciadesde'])

    return trm

# LOAD DATA TO POSTGRESQL NEON
def data_load_trm(clean_data, table_name, pg_motor):

    with pg_motor.begin() as conn:
        # TRUNCATE vacía la tabla al instante, pero deja la estructura intacta para que la vista no se rompa
        conn.execute(text(f"TRUNCATE TABLE {table_name};"))

    clean_data.to_sql(table_name, pg_motor, if_exists='append', index=False)
    
    print(f"Cargando datos a PostgreSQL...{table_name}")


"""ETL PROCESS ASSEMBLY LINE"""


# DATABASE GETTING
str_conn = os.getenv("DATABASE_NEON")

if str_conn is None:
    raise ValueError("¡Database not found, check your .env ")

pg_motor = create_engine(str_conn)


#ASSEMBLY LINE OF THE ETL PROCESS
raw_data = data_extract_trm()
clean_data = data_transf_trm(raw_data)
load_data = data_load_trm(clean_data, "trm_diaria", pg_motor)



# 08/jul/2026:6:14 PM - Verifying the TRM code flows with no issue, Script run manually. 




