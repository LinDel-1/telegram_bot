import datetime

import psycopg2
import telegram


USER = 'postgres'
PASSWORD = '12345678'
HOST = 'localhost'
PORT = '5432'
DATABASE = 'telegram_bot'
TABLE_NAME = 'user_bot_action'
MV_TABLE_NAME = 'user_last_action'

FIELDS_NAME = [
    'username_id',
    'username',
    'last_name',
    'first_name',
    'message',
    'time_sending',
]

CREATE_TABLE_SQL = f'''
    create table {TABLE_NAME} (
        id serial primary key,
        username_id bigint,
        username character varying(100),
        last_name character varying(100),
        first_name character varying(100),
        message character varying(1000),
        time_sending timestamp
)
'''

CREATE_MV_TABLE_SQL = f'''
drop materialized view if exists {MV_TABLE_NAME};
create materialized view {MV_TABLE_NAME} as (
    with last_action_users as (
        select username_id, max(time_sending) as time_sending
        from user_bot_action
        group by username_id
    )
    
    select common.* 
    from user_bot_action as common
    join last_action_users as last
    on last.username_id = common.username_id and
    last.time_sending = common.time_sending
);
'''


class DataBase:
    def __init__(self) -> None:
        """
        Создаёт инстанс объекта, отвечающего за подключение к БД
        """

        self.connection = psycopg2.connect(user=USER,
                                           password=PASSWORD,
                                           host=HOST,
                                           port=PORT,
                                           database=DATABASE)
        self.cursor = self.connection.cursor()
        print('DataBase connected')

    def create_row(self, telegram_user: telegram.User, message_text: str) -> None:
        """
        Метод, который создаёт строку в инстансе класса, отвечающего за определённую БД.
        """

        # Собираем необходимые поля для записи в единую строку
        fields_string = ', '.join(FIELDS_NAME)
        values_count_string = ', '.join(['%s'] * len(FIELDS_NAME))
        value_tuple = self.get_telegram_user_values(telegram_user, message_text)
        sql_request = f"""
            insert into {TABLE_NAME} ({fields_string})
            values ({values_count_string})
                    """
        self.cursor.execute(sql_request, value_tuple)
        self.connection.commit()

    @classmethod
    def get_telegram_user_values(cls, telegram_user: telegram.User, message_text) -> tuple:
        """
        Вспомогательный метод, формирующий кортеж из данных, которые надо внести в БД
        """

        time_sending = datetime.datetime.now()
        value_tuple = (
            telegram_user.id, telegram_user.username, telegram_user.last_name, telegram_user.first_name,
            message_text, time_sending
        )

        return value_tuple

    def _close(self) -> None:
        if self.connection:
            self.connection.close()

    def __del__(self) -> None:
        """
        При заверешении программы, инстанс класса БД разрушается, закрыв подключение к БД
        """
        self._close()
        print('DataBase closed')
