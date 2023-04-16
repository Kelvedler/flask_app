def label_columns(table):
    return [column.label(f'{column.table.description}__{column.description}') for column in table.columns]
