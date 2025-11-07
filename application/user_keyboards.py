from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardButton, InlineKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить", callback_data="cd_instruction_1")]
])

"""INSTRUCTION"""
instruction_slide_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="cd_main_menu")],
    [InlineKeyboardButton(text="1/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="☞", callback_data="cd_instruction_2")]
])
instruction_slide_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="cd_main_menu")],
    [InlineKeyboardButton(text="☜", callback_data="cd_instruction_1"),
     InlineKeyboardButton(text="2/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="☞", callback_data="cd_instruction_3")]
])
instruction_slide_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="cd_main_menu")],
    [InlineKeyboardButton(text="☜", callback_data="cd_instruction_2"),
     InlineKeyboardButton(text="3/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="☞", callback_data="cd_instruction_4")]
])
instruction_slide_4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="cd_main_menu")],
    [InlineKeyboardButton(text="☜", callback_data="cd_instruction_3"),
     InlineKeyboardButton(text="4/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="☞", callback_data="cd_instruction_5")]
])
instruction_slide_5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Пропустить", callback_data="cd_main_menu")],
    [InlineKeyboardButton(text="☜", callback_data="cd_instruction_4"),
     InlineKeyboardButton(text="5/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="☞", callback_data="cd_instruction_6")]
])
instruction_slide_6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☜", callback_data="cd_instruction_5"),
     InlineKeyboardButton(text="6/6", callback_data="cd_empty"),
     InlineKeyboardButton(text="-> Cessing!", callback_data="cd_main_menu")]
])

"""INSTRUCTION END"""


back_to_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="cd_main_menu")]
])


main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Мои записи 💾", callback_data="cd_my_meas"),
     InlineKeyboardButton(text="Записать ✏️", callback_data="cd_new_meas")],
    [InlineKeyboardButton(text="Настройки ⚙️", callback_data="cd_settings"),
     InlineKeyboardButton(text="Отзыв 📝", callback_data="cd_feedback")]
])

"""NEW MEASUREMENT"""
new_measurement_done = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Готово", callback_data="cd_new_meas_done")]
])
async def new_measurement_witch_folder(measurements):
    bilder = InlineKeyboardBuilder()

    for measurement in measurements:
        measurement_space_rep = measurement.replace(" ", "¤")
        bilder.button(text=f"{measurement}", callback_data=f"cd_new_meas_w_in_dir:{measurement_space_rep}")
    bilder.adjust(1)
    bilder.row(InlineKeyboardButton(text="Новая папка", callback_data="cd_new_meas_new_folder"))
    return bilder.as_markup()


new_measurement_back_from_folder_name = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="cd_new_meas_back_to_select_folder")]
])

just_added_new_measurement_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Записать в серию", callback_data="cd_new_meas_add_to_ser")],
    [InlineKeyboardButton(text="Записать ещё ✏️", callback_data="cd_new_meas"),
     InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
])

async def new_measurement_witch_series(series_list):
    bilder = InlineKeyboardBuilder()

    for series in series_list:
        series = series.replace(" ", "_")
        bilder.button(text=f"{series}", callback_data=f"cd_new_meas_add_to_ser:{series}")
    bilder.adjust(2)
    bilder.row(InlineKeyboardButton(text="Новая серия", callback_data="cd_new_meas_new_series"))
    return bilder.as_markup()

"""NEW MEASUREMENT END"""


"""MY MEASUREMENT"""

async def my_meas_witch_meas(measurements):
    bilder = InlineKeyboardBuilder()
    if len(measurements) > 0:
        for measurement in measurements:
            measurement_space_rep = measurement.replace(" ", "¤")
            bilder.button(text=f"{measurement}", callback_data=f"cd_my_meas_witch_meas:{measurement_space_rep}")
        bilder.adjust(1)
    else:
        bilder.button(text="Записей нет", callback_data="cd_my_meas_no_meas")
    bilder.row(InlineKeyboardButton(text="Меню", callback_data="cd_main_menu"))
    return bilder.as_markup()

async def my_meas_witch_quantity(quantities):
    bilder = InlineKeyboardBuilder()
    for quantity in quantities:
        quantity_name = quantity.split(":")[0].replace(" ", "_")
        postfix = quantity.split(":")[1]
        bilder.button(text=f"{quantity_name}", callback_data=f"cd_my_meas_quantity:{quantity}:{postfix}")
    bilder.adjust(2)
    bilder.row(InlineKeyboardButton(text="Назад", callback_data="cd_my_meas"),
               InlineKeyboardButton(text="Меню", callback_data="cd_main_menu"))
    return bilder.as_markup()

async def my_meas_in_measurement(measurement):
    measurement = measurement.replace(" ", "¤")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записать в серию", callback_data="cd_my_meas_add_to_series")],
        [InlineKeyboardButton(text="Зависимая величина 🔎", callback_data="cd_my_meas_select_y")],
        [InlineKeyboardButton(text="Назад", callback_data=f"cd_my_meas_witch_meas:{measurement}"),
         InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
    ])
    return kb

my_meas_back_from_new_ser = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="cd_my_meas_add_to_series"),
     InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
])

async def my_meas_in_series(measurement):
    measurement = measurement.replace(" ", "¤")
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Зависимая величина 🔎", callback_data="cd_my_meas_select_y")],
        [InlineKeyboardButton(text="Назад", callback_data=f"cd_my_meas_witch_meas:{measurement}"),
         InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
    ])
    return kb

async def my_meas_witch_series(series_list):
    bilder = InlineKeyboardBuilder()

    for series in series_list:
        series = series.replace(" ", "_")
        bilder.button(text=f"{series}", callback_data=f"cd_my_meas_add_to_ser:{series}")
    bilder.adjust(2)
    bilder.row(InlineKeyboardButton(text="Новая серия", callback_data="cd_my_meas_new_series"))
    return bilder.as_markup()

async def my_meas_witch_y(quantities, quantity):
    bilder = InlineKeyboardBuilder()
    for quantity in quantities:
        quantity_name = quantity.split(":")[0].replace(" ", "_")
        postfix = quantity.split(":")[1]
        bilder.button(text=f"{quantity_name}", callback_data=f"cd_my_meas_y:{quantity}:{postfix}")
    bilder.adjust(2)
    bilder.row(InlineKeyboardButton(text="Назад", callback_data=f"cd_my_meas_quantity:{quantity}:{postfix}"),
               InlineKeyboardButton(text="Меню", callback_data="cd_main_menu"))
    return bilder.as_markup()

async def my_meas_select_func_for_approx(x, y):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{y} = k * {x} + b", callback_data="my_meas_approx:linear")],
        [InlineKeyboardButton(text=f"{y} = a * ({x} ** 2) + b * {x} + c", callback_data="my_meas_approx:quadratic")]
    ])
    return kb
async def new_meas_approx_done(measurement):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data=f"cd_my_meas_witch_meas:{measurement}"),
         InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
    ])
    return kb

"""MY MEASUREMENT END"""

async def get_file_witch_folder(folders):
    bilder = InlineKeyboardBuilder()
    for folder in folders:
        folder_cd = folder.replace(" ", "¤")
        bilder.button(text=f"{folder}", callback_data=f"cd_get_file_folder:{folder_cd}")
    bilder.adjust(1)
    bilder.row(InlineKeyboardButton(text="Новая папка", callback_data="cd_get_file_new_folder"))

    return bilder.as_markup()


"""SETTINGS"""
settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Доверительная вероятность", callback_data="cd_settings_confidence")],
    [InlineKeyboardButton(text="Разделитель .csv", callback_data="cd_settings_separator")],
    [InlineKeyboardButton(text="Авто определение серии", callback_data="cd_settings_auto_ser")],
    [InlineKeyboardButton(text="Назад", callback_data="cd_main_menu")]
])

settings_param = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="cd_settings"),
     InlineKeyboardButton(text="Меню", callback_data="cd_main_menu")]
])


"""SETTINGS END"""