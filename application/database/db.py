import asyncpg
import asyncio

from cessing.config import BD_SUPERUSER, BD_SUPERPASS, NEW_DB, NEW_PASS, NEW_USER, HOST, PORT

async def create_database():


    conn = await asyncpg.connect(
        database="postgres",
        user=BD_SUPERUSER,
        password=BD_SUPERPASS,
        host=HOST,
        port=PORT
    )

    user_exists = await conn.fetchval(
        "SELECT 1 FROM pg_roles WHERE rolname = $1;", NEW_USER
    )

    if not user_exists:
        await conn.execute(f"""
                CREATE USER "{NEW_USER}" WITH PASSWORD '{NEW_PASS}';
                ALTER USER "{NEW_USER}" CREATEDB;
            """)
        print(f"Пользователь '{NEW_USER}' создан и получил право на создание БД.")
    else:
        print(f"Пользователь '{NEW_USER}' уже существует.")



    exists = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1;", NEW_DB
    )

    if not exists:
        await conn.execute(f"CREATE DATABASE \"{NEW_DB}\" OWNER \"{NEW_USER}\"")
        print(f"База данных '{NEW_DB}' успешно создана и принадлежит {NEW_USER}.")
    else:
        print(f"База данных '{NEW_DB}' уже существует.")

    await conn.close()

async def create_table_users():
    conn = await asyncpg.connect(
        database=NEW_DB,
        user=NEW_USER,
        password=NEW_PASS,
        host=HOST,
        port=PORT
        )
    table_name = "users"
    await conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            telegram_id BIGINT PRIMARY KEY,
            measurements TEXT[],
            username TEXT
            )
        """)
    print(f"Таблица {table_name} создана")
    await conn.close()

async def create_table_series():
    conn = await asyncpg.connect(
        database=NEW_DB,
        user=NEW_USER,
        password=NEW_PASS,
        host=HOST,
        port=PORT
        )
    table_name = "series"
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS series (
            measurement TEXT,
            quantity TEXT,
            nominal_value DOUBLE PRECISION[],
            error DOUBLE PRECISION[],
            access BIGINT
            )
        """)
    print(f"Таблица {table_name} создана")
    await conn.close()

async def create_table_measurements():
    conn = await asyncpg.connect(
        database=NEW_DB,
        user=NEW_USER,
        password=NEW_PASS,
        host=HOST,
        port=PORT
        )
    table_name = "measurements"
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            measurement TEXT,
            quantity TEXT,
            value DOUBLE PRECISION[],
            instrum_err REAL,
            access BIGINT
            )
        """)
    print(f"Таблица {table_name} создана")
    await conn.close()

async def create_table_settings():
    conn = await asyncpg.connect(
        database=NEW_DB,
        user=NEW_USER,
        password=NEW_PASS,
        host=HOST,
        port=PORT
        )
    table_name = "settings"
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            confidence REAL,
            separator TEXT,
            detect_series BOOLEAN DEFAULT TRUE,
            telegram_id BIGINT
            )
        """)
    print(f"Таблица {table_name} создана")
    await conn.close()

# async def create_table_stats():
#     conn = await asyncpg.connect(
#         database=NEW_DB,
#         user=NEW_USER,
#         password=NEW_PASS,
#         host=HOST,
#         port=PORT
#         )
#     table_name = "stats"
#     await conn.execute("""
#         CREATE TABLE IF NOT EXISTS stats (
#             telegram_id BIGINT,
#             username TEXT,
#             last_activity TIMESTAMP,
#             pics INT
#             )
#         """)
#     print(f"Таблица {table_name} создана")
#     await conn.close()

asyncio.run(create_database())
asyncio.run(create_table_users())
asyncio.run(create_table_settings())
asyncio.run(create_table_measurements())
asyncio.run(create_table_series())
# asyncio.run(create_table_stats())