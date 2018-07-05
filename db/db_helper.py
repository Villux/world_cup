import numpy as np

insert_query = 'insert into {table_name} ({columns}) values ({placeholders})'

def guarantee_python_types(obj):
    if isinstance(obj, np.generic):
        return np.asscalar(obj)
    return obj

def get_value_tuple(row):
    values = [guarantee_python_types(value) for value in row.values()]
    return tuple(values)

def build_insert_query(data, table_name):
    columns = data.keys()
    placeholders = ["?"] * len(columns)
    query = insert_query.format(table_name=table_name, columns=','.join(columns),placeholders=','.join(placeholders))
    return query
