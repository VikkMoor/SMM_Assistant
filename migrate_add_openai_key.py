
from main import app
from app import db
from app.models import User
from sqlalchemy import inspect, text


with app.app_context():
    table_name = User.__tablename__

    columns = [
        column["name"]
        for column in inspect(db.engine).get_columns(table_name)
    ]

    if "openai_api_key" not in columns:
        with db.engine.begin() as connection:
            connection.execute(
                text(
                    f'ALTER TABLE "{table_name}" '
                    'ADD COLUMN openai_api_key VARCHAR(500)'
                )
            )

        print("Столбец openai_api_key успешно добавлен.")
    else:
        print("Столбец openai_api_key уже существует.")
