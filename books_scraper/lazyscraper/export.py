import json
import duckdb


def export_json(data: list[dict], file_name: str) -> None:
    try:
        with open(file_name, "r") as f:
            old_data = json.load(f)
    except Exception as e:
        old_data = []
    old_data.extend(data)
    with open(file_name, "w") as f:
        json.dump(old_data, f, indent=4)    
    print("finished loading data")
    print("\n"*2)
            

def type_to_duckdb_type(value):
    if isinstance(value, int):
        return 'INTEGER'
    elif isinstance(value, float):
        return 'DOUBLE'
    else:
        return 'VARCHAR'

def export_duckdb(data: list[dict], file_name: str, table_name: str) -> None:
    try:
        with duckdb.connect(file_name) as db:
            columns= ",".join(f"{key} {type_to_duckdb_type(value)}" for key, value in data[0].items())
            db.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} ({columns})
                      """)

            placeholder= ",".join(["?" for _ in data[0].keys()])
            values= [tuple(value.values()) for value in data]
            db.executemany(f"""
                INSERT INTO {table_name}
                VALUES ({placeholder})
                       """, values)
            print(f"finished loading data")
    except Exception as e:
        raise Exception(f"Error:\n{e}")
        
