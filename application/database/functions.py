import asyncpg
import asyncio

from cessing.config import DB_CONFIG

async def write_new_user(telegram_id):
    conn = await asyncpg.connect(**DB_CONFIG)
    measurements = []
    rows = await conn.fetch("""
        SELECT telegram_id FROM users
    """)
    ids = [row["telegram_id"] for row in rows]
    if telegram_id not in ids:
        await conn.execute("""
        INSERT INTO users (telegram_id, measurements)
        VALUES ($1, $2)
        """, telegram_id, measurements)
    await conn.close()

async def write_measurement(measurement: str, quantity: str, value: list, instrum_err: float, access: int):
    conn = await asyncpg.connect(**DB_CONFIG)

    await conn.execute("""
        INSERT INTO measurements (measurement, quantity, value, instrum_err, access)
        VALUES ($1, $2, $3, $4, $5)
    """, measurement, quantity, value, instrum_err, access)

    measurements_list = await get_measurements(access)

    if measurement not in measurements_list:
        measurements_list.append(measurement)
        await conn.execute("""
            UPDATE users SET measurements = $2 WHERE telegram_id = $1
        """, access, measurements_list)

    await conn.close()

async def delete_measurement(access, measurement, quantity):
    conn = await asyncpg.connect(**DB_CONFIG)

    await conn.execute("""
        DELETE FROM measurements WHERE access = $1 AND measurement = $2 AND quantity = $3
    """, access, measurement, quantity)
    await conn.close()

async def get_from_measurement(user_id, measurement, quantity):
    conn = await asyncpg.connect(**DB_CONFIG)

    row = await conn.fetchrow("""
        SELECT value, instrum_err FROM measurements WHERE access = $1 AND measurement = $2 AND quantity = $3
    """, user_id, measurement, quantity)
    values = row["value"]
    instrum_err = row["instrum_err"]

    await conn.close()
    return values, instrum_err


async def get_measurements(access: int):
    conn = await asyncpg.connect(**DB_CONFIG)
    rows = await conn.fetch("""
        SELECT measurements FROM users WHERE telegram_id = $1
        """, access)
    await conn.close()
    return rows[0]["measurements"] if rows else []

async def get_quantities(user_id, measurement):
    conn = await asyncpg.connect(**DB_CONFIG)

    rows = await conn.fetch("""
        SELECT quantity FROM measurements WHERE access = $1 AND measurement = $2
    """, user_id, measurement)

    await conn.close()
    return [row["quantity"] for row in rows]




async def write_series(measurement: str, quantity: str, nominal_value: list, error: list, access: int):
    conn = await asyncpg.connect(**DB_CONFIG)
    if type(nominal_value) != list:
        nominal_value = [nominal_value]
    if type(error) != list:
        error = [error]

    await conn.execute("""
        INSERT INTO series (measurement, quantity, nominal_value, error, access)
        VALUES ($1, $2, $3, $4, $5)
    """, measurement, quantity, nominal_value, error, access)

    await conn.close()

async def delete_series(measurement, quantity, access):
    conn = await asyncpg.connect(**DB_CONFIG)
    await conn.execute("""
    DELETE FROM series WHERE measurement = $1 AND quantity = $2 AND access = $3
    """, measurement, quantity, access)

async def update_series(access, measurement, quantity, nominal_value, error):
    conn = await asyncpg.connect(**DB_CONFIG)
    row = await conn.fetchrow("""
        SELECT nominal_value, error FROM series WHERE access = $1 AND measurement = $2 AND quantity = $3
    """, access, measurement, quantity)
    nominal_value_list = row["nominal_value"]
    error_list = row["error"]
    nominal_value_list.append(nominal_value)
    error_list.append(error)

    await conn.execute("""
        UPDATE series SET nominal_value = $1, error = $2 WHERE access = $3 AND measurement = $4 AND quantity = $5
    """, nominal_value_list, error_list, access, measurement, quantity)

    await conn.close()

async def get_series_list(user_id, measurement):
    conn = await asyncpg.connect(**DB_CONFIG)

    rows = await conn.fetch("""
        SELECT quantity FROM series WHERE access = $1 AND measurement = $2
    """, user_id, measurement)
    await conn.close()
    return [row["quantity"] for row in rows]

async def get_series(access, measurement, quantity):
    conn = await asyncpg.connect(**DB_CONFIG)

    row = await conn.fetchrow("""
        SELECT nominal_value, error FROM series WHERE access = $1 AND measurement = $2 AND quantity = $3
    """, access, measurement, quantity)
    nominals, errors = row["nominal_value"], row["error"]
    await conn.close()
    return nominals, errors

async def write_settings(confidence, separator, telegram_id):
    conn = await asyncpg.connect(**DB_CONFIG)

    rows = await conn.fetch("""
        SELECT telegram_id FROM settings
    """)
    ids = [row["telegram_id"] for row in rows]

    if telegram_id not in ids:
        await conn.execute("""
            INSERT INTO settings (confidence, separator, telegram_id)
            VALUES ($1, $2, $3)
        """, confidence, separator, telegram_id)
    await conn.close()

async def get_settings(telegram_id):
    conn = await asyncpg.connect(**DB_CONFIG)

    row = await conn.fetchrow("""
        SELECT * FROM settings WHERE telegram_id = $1
    """, telegram_id)
    await conn.close()
    return row

async def update_settings(telegram_id, new_param, param):
    conn = await asyncpg.connect(**DB_CONFIG)

    await conn.execute(f"""
    UPDATE settings SET {param} = $2 WHERE telegram_id = $1""",
                       telegram_id, new_param)

async def delete_exp(measurement: str, access):
    conn = await asyncpg.connect(**DB_CONFIG)

    await conn.execute("""
    DELETE FROM series WHERE measurement = $1 AND access = $2
    """, measurement, access)

    await conn.execute("""
        DELETE FROM measurements WHERE measurement = $1 AND access = $2
        """, measurement, access)

    measurements = (await conn.fetchrow("""SELECT * FROM users WHERE telegram_id = $1""",
                                        access))["measurements"]
    measurements.remove(f"{measurement}")

    await conn.execute("""UPDATE users SET measurements = $1 WHERE telegram_id = $2""", measurements, access)





