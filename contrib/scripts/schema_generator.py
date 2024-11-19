import os

from database.models import Base

from sqlalchemy.schema import CreateTable, SetColumnComment, SetTableComment

models = Base.metadata.sorted_tables
path_to_schema = os.environ.get('SQL_SCHEMA_PATH', default='./schema.sql')


def generate_documentation():
    with open(path_to_schema, 'w') as file:
        for model in models:
            file.write(f'{str(CreateTable(model))[:-2]};\n')  # noqa
            if model.comment:
                file.write(f'{SetTableComment(model)};\n')  # noqa
            for column in model.columns:
                if column.comment:
                    file.write(f'{SetColumnComment(column)};\n')  # noqa


if __name__ == '__main__':
    generate_documentation()
