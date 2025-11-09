from operator import setitem

from aiofiles.os import access
from aiogram import F, Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto, BufferedInputFile
from aiogram.fsm.context import FSMContext
from numpy import array
from uncertainties import ufloat
from io import BytesIO

from application import user_keyboards as ukb
from application import states as st
from application.database import functions as dtf
from application.measurementClasses import MeasurementLoader, MeasurementProcess

router = Router()

"""INSTRUCTION"""
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    if "msg_id" in data:
        msg = data["msg_id"]
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    photo = FSInputFile("application/assets/welcome pic/autumn.png")
    await message.answer_photo(photo=photo,
                               disable_notification=True)
    await message.delete()
    id = message.from_user.id
    msg = await message.answer(text=f"<code>Добро пожаловать в Cessing!</code>\n\n"
                                    f"Чтобы удобно и быстро работать с ботом, посмотрите короткую инструкцию.",
                               reply_markup=ukb.start,
                               parse_mode="HTML",
                               disable_notification=True)
    await state.update_data(msg_id=msg)
    await dtf.write_new_user(id)
    await dtf.write_settings(0.950, ",", id)

@router.callback_query(F.data == "cd_empty")
async def func_empty_data(callback: CallbackQuery):
    await callback.answer(text="🤓")

@router.callback_query(F.data == "cd_instruction_1")
async def func_instruction_1(callback: CallbackQuery, state: FSMContext):
    picture_slide_1 = FSInputFile(path="application/assets/Instruction/page1.png")
    msg_id = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id.message_id)
    msg = await callback.message.answer_photo(photo=picture_slide_1,
                                              caption="В <code><i>Cessing</i></code> есть свои настройки. "
                                                      "В них собраны некоторые параметры, "
                                                      "которые не нужно часто менять.\n"
                                                      "Используйте /settings чтоб перейти в меню настроек. "
                                                      "На картинке пример того, как может быть настроен Cessing",
                                              reply_markup=ukb.instruction_slide_1,
                                              parse_mode="HTML",
                                              disable_notification=True)
    await state.update_data(msg_id=msg)
@router.callback_query(F.data == "cd_instruction_2")
async def func_instruction_2(callback: CallbackQuery, state: FSMContext):
    picture_slide_2 = FSInputFile(path="application/assets/Instruction/page2.png")
    msg = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer_photo(photo=picture_slide_2,
                                              caption="<code>Cessing</code> принимает несколько типов файлов.\nВы можете "
                                                      "отправить файл с расширением <code>.xlsx</code> (дефолтное расширение "
                                                      "для экспорта из <b>Excel</b>) или <code>.csv</code> (в <b>Excel</b> "
                                                      "можно выбрать при экспорте). Обязательно запоминайте, какой "
                                                      "разделитель в вашем <code>.csv</code> файле и "
                                                      "меняйте это значение в настройках",
                                              reply_markup=ukb.instruction_slide_2,
                                              parse_mode="HTML",
                                              disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_instruction_3")
async def func_instruction_3(callback: CallbackQuery, state: FSMContext):
    picture_slide_3 = FSInputFile("application/assets/Instruction/page3.png")
    data = await state.get_data()
    msg = data["msg_id"]
    if "msg_media" in data.keys():
        msg_media = data["msg_media"]
        for id in msg_media:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer_photo(photo=picture_slide_3,
                                              caption="Если вы загружаете данные файлом, то обязательно обратите внимание, "
                                                      "как правильно записывать эксперименты для <code>Cessing</code>\n"
                                                      "Когда вы провели опыт, вы должны заполнить один столбец его "
                                                      "результатами. В первую ячейку придумайте и запишите имя вашего "
                                                      "измерения.\n"
                                                      "Например, вы измерили время падения объекта с определённой высоты "
                                                      "пять раз. Саму высоту вы тоже измерили 5 раз - на картинке показано, "
                                                      "как правильно внести данные в таблицу\n\n"
                                                      "<i>Столбик \"С\" заполнен для наглядности, вносить его в "
                                                      "свою таблицу не следует!</i>",
                                              reply_markup=ukb.instruction_slide_3,
                                              parse_mode="HTML",
                                              disable_notification=True)
    await state.update_data(msg_id=msg)
@router.callback_query(F.data == "cd_instruction_4")
async def func_instruction_4(callback: CallbackQuery, state: FSMContext):
    picture_slide_4 = FSInputFile("application/assets/Instruction/page4.png")
    picture_slide_4_2 = FSInputFile("application/assets/Instruction/page4_2.png")
    media = [
        InputMediaPhoto(media=picture_slide_4),
        InputMediaPhoto(media=picture_slide_4_2)
    ]
    msg = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg_media = await callback.message.answer_media_group(media=media,
                                                          disable_notification=True)
    msg = await callback.message.answer(text="Бывают эксперименты, в которых нужно измерять что-то несколько раз и "
                                             "в зависимости от меняющихся параметров.\nНапример, вы измерили "
                                             "падение объекта с определённой высоты несколько раз, поменяли высоту "
                                             "и ещё раз измерили несколько раз. В <code>Cessing</code> есть функция записи "
                                             "измерения в серию - она будет доступна в меню после загрузки файла. "
                                             "Если записать название опыта так, как показано на первой картинке, то "
                                             "бот сам распознает серию и предложит объединить измерения с "
                                             "одинаковым названием. Если согласиться, то далее ваши данные будут "
                                             "храниться в боте одним столбиком, как на второй картинке\n\n"
                                             "Кстати, именно на второй картинке пример, как правильно хранить данные для "
                                             "будущей аппроксимации. После первой строки, ячейки заполняйте как бы "
                                             "координатой. При чём не обязательно с погрешностью - она только лишь "
                                             "добавляет <i>error bar</i> на график.",
                                        reply_markup=ukb.instruction_slide_4,
                                        parse_mode="HTML",
                                        disable_notification=True)

    await state.update_data(msg_media=msg_media)
    await state.update_data(msg_id=msg)



@router.callback_query(F.data == "cd_instruction_5")
async def func_instruction_5(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]
    if "msg_media" in data.keys():
        msg_media = data["msg_media"]
        for id in msg_media:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)

    msg = await callback.message.answer(text="Ещё несколько советов по сохранению данных.\n"
                                             "Вы можете сами записать данные в серию, либо так\n"
                                             "<code>(Записать ✏️ -> (запишите эксперимент) -> Готово -> Записать в серию)"
                                             "</code>\nлибо так\n<code>(Мои записи -> выберите запись -> выберите название "
                                             "столбика(измерения) -> добавить в серию -> выберите серию)</code>\n\n",
                                        reply_markup=ukb.instruction_slide_5,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_instruction_6")
async def func_instruction_6(callback: CallbackQuery, state: FSMContext):
    picture_slide_6 = FSInputFile("application/assets/Instruction/page6.png")
    msg = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer_photo(photo=picture_slide_6,
                                              caption="В <code>Cessing</code> можно работать не только с линейными "
                                                      "зависимостями, но следует уметь зависимости правильно оформлять. "
                                                      "На картинке правильные и неправильные варианты написания "
                                                      "функции зависимости",
                                              reply_markup=ukb.instruction_slide_6,
                                              parse_mode="HTML",
                                              disable_notification=True)
    await state.update_data(msg_id=msg)

"""INSTRUCTION END"""

@router.callback_query(F.data == "cd_main_menu")
async def func_main_menu(callback: CallbackQuery, state: FSMContext):
    msg = (await state.get_data())["msg_id"]
    if msg != "don't delete":
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Отправьте файл или воспользуйтесь кнопками.",
                                        reply_markup=ukb.main_menu,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)
    await state.set_state(st.MainMenu.waiting_for_file)

"""NEW MEASUREMENT"""

@router.callback_query(F.data == "cd_new_meas")
async def func_new_msrm(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text(text="Вводите значения поочереди. По завершении нажмите кнопку"
                                                " \"<b>Готово</b>\"",
                                           reply_markup=ukb.back_to_main_menu,
                                           parse_mode="HTML",
                                           disable_notification=True)
    await state.set_state(st.NewMeasurement.waiting_for_num)
    await state.update_data(nums=[])
    await state.update_data(sequence_num=0)
    await state.update_data(msg_id=msg)


@router.message(st.NewMeasurement.waiting_for_num)
async def func_take_measurement(message: Message, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    nums = data.get("nums", [])
    seq_num = data["sequence_num"]
    id = data["msg_id"]
    await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
    await message.delete()
    kb = None if seq_num < 2 else ukb.new_measurement_done

    try:
        seq_num += 1
        num = float(text)
        nums.append(num)
        await state.update_data(nums=nums)
        await state.update_data(sequence_num=seq_num)
        msg = await message.answer(text=f"Номер {seq_num}\nЧисло <b>{num}</b> добавлено! Введите следующее число.",
                                   reply_markup=kb,
                                   parse_mode="HTML",
                                   disable_notification=True)
    except ValueError:
        msg = await message.answer(text="⚠️Ошибка: Вы ввели неправильный тип данных.\n"
                                        "Вводите десятичную дробь <b>с точкой, а не с запятой</b>")
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_new_meas_done")
async def func_name_for_new_measurement(callback: CallbackQuery, state: FSMContext):
    if StateFilter(st.NewMeasurement.waiting_for_num):
        data = await state.get_data()
        id = data["msg_id"]
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
        await state.set_state(st.NewMeasurement.waiting_for_instrum_err)
        msg = await callback.message.answer(text="Введите приборную погрешность для измерений"
                                                 " (<b>в тех же единицах</b>)",
                                            parse_mode="HTML",
                                            disable_notification=True)
        await state.update_data(msg_id=msg)

@router.message(st.NewMeasurement.waiting_for_instrum_err)
async def func_name_for_new_measurement(message: Message, state: FSMContext):
    if StateFilter(st.NewMeasurement.waiting_for_num):
        try:
            await state.update_data(instrument_error=float(message.text))
            data = await state.get_data()
            id = data["msg_id"]
            await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
            await message.delete()
            await state.set_state(st.NewMeasurement.waiting_for_name)
            msg = await message.answer(text="Введите название для введённых значений, например, Time, Length, ...",
                                       disable_notification=True)
        except ValueError:
            id = (await state.get_data())["msg_id"]
            await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
            msg = await message.answer(text="⚠️Ошибка: Вы ввели неправильный тип данных.\n"
                                            "Вводите десятичную дробь <b>с точкой, а не с запятой</b>\n\nВведите ещё "
                                            "раз приборную погрешность.")
            await message.delete()
        await state.update_data(msg_id=msg)


@router.message(st.NewMeasurement.waiting_for_name)
async def func_new_measurement_done(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    nums = data.get("nums", [])
    nums_string = "\n".join([str(x) for x in nums])
    name = data["name"]
    id = data["msg_id"]

    if (len(name) > 20) or (" " in name):
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        msg = await message.answer(text="⚠️Пожалуйста, ограничьтесь 20 символами (не больше) ⚠️(пробел нельзя)\n\n"
                                        "Запишите снова")
        await state.update_data(msg_id=msg)
    else:
        user_id = message.from_user.id
        measurements = await dtf.get_measurements(user_id)

        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        await message.delete()
        msg = await message.answer(text=f"Введённые значения {name}:\n"
                                        f"{nums_string}\n"
                                        f"Выберите, в какую папку сохранить запись",
                                   reply_markup=await ukb.new_measurement_witch_folder(measurements),
                                   parse_mode="HTML",
                                   disable_notification=True)
        await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_new_meas_back_to_select_folder")
async def func_new_measurement_done_clb(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nums = data.get("nums", [])
    nums_string = "\n".join([str(x) for x in nums])
    name = data["name"]
    id = data["msg_id"]

    user_id = callback.from_user.id
    measurements = await dtf.get_measurements(user_id)

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    msg = await callback.message.answer(text=f"Введённые значения {name}:\n"
                                             f"{nums_string}\n"
                                             f"Выберите, в какую папку сохранить запись",
                                        reply_markup=await ukb.new_measurement_witch_folder(measurements),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_new_meas_new_folder")
async def func_new_measurement_new_folder_name(callback: CallbackQuery, state: FSMContext):
    id = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    msg = await callback.message.answer(text="Придумайте название и запишите его",
                                        reply_markup=ukb.new_measurement_back_from_folder_name,
                                        disable_notification=True)
    await state.set_state(st.NewMeasurement.waiting_for_folder_name)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data.startswith("cd_new_meas_w_in_dir:"))
async def func_new_measurement_select_folder(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data["msg_id"]

    measurement = (callback.data.split(":", 1)[1]).replace("¤", " ")
    quantity = data["name"]
    value = data.get("nums", [])
    instrum_err = data["instrument_error"]
    access = callback.from_user.id

    confidence = float((await dtf.get_settings(access))["confidence"])
    _, nominal_value, error = await MeasurementProcess({quantity: array(value)}).random_error(quantity=quantity,
                                                                                   instrument_error=instrum_err,
                                                                                   confidence=confidence)

    await dtf.write_measurement(measurement, quantity, value, instrum_err, access)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    msg = await callback.message.answer(text="Запись сохранена!\n\n"
                                              "Случайная погрешность:\n"
                                              f"<i>{nominal_value} +/- {error}</i>\n\n"
                                              "Можете также сохранить запись в серию",
                                        reply_markup=ukb.just_added_new_measurement_menu,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(measurement=measurement)
    await state.update_data(nominal_value=nominal_value)
    await state.update_data(error=error)
    await state.update_data(msg_id=msg)

@router.message(st.NewMeasurement.waiting_for_folder_name)
async def func_new_measurement_save(message: Message, state: FSMContext):
    await state.update_data(measurement=message.text)
    data = await state.get_data()
    id = data["msg_id"]

    value = data.get("nums", [])
    instrum_err = data["instrument_error"]
    quantity = data["name"]
    access = message.from_user.id
    measurement = data["measurement"]
    if len(measurement) > 20:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        msg = await message.answer(text="⚠️Пожалуйста, ограничьтесь 20 символами (не больше) ⚠️\n\n"
                                        "Запишите снова")
        await state.update_data(msg_id=msg)
    else:
        await dtf.write_measurement(measurement, quantity, value, instrum_err, access)
    
        confidence = float((await dtf.get_settings(access))["confidence"])
        _, nominal_value, error = await MeasurementProcess({quantity: array(value)}).random_error(quantity=quantity,
                                                                                       instrument_error=instrum_err,
                                                                                       confidence=confidence)
    
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        await message.delete()
        msg = await message.answer(text="Запись сохранена!\n\n"
                                        "Случайная погрешность:\n"
                                        f"<i>{nominal_value} +/- {error}</i>\n\n"
                                        "Можете также сохранить запись в серию",
                                   reply_markup=ukb.just_added_new_measurement_menu,
                                   parse_mode="HTML",
                                   disable_notification=True)
        await state.update_data(nominal_value=nominal_value)
        await state.update_data(error=error)
        await state.update_data(msg_id=msg)

"""NEW MEASUREMENT HALF-END"""

"""ADD TO SERIES"""

@router.callback_query(F.data == "cd_new_meas_add_to_ser")
async def func_new_measurement_select_series(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data["msg_id"]

    user_id = callback.from_user.id
    measurement = data["measurement"]
    series_list = await dtf.get_series_list(user_id, measurement)

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    msg = await callback.message.answer(text=f"Выберите, в какую серию сохранить запись",
                                        reply_markup=await ukb.new_measurement_witch_series(series_list),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_new_meas_new_series")
async def func_new_measurement_new_series_name(callback: CallbackQuery, state: FSMContext):
    id = (await state.get_data())["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    msg = await callback.message.answer(text="Придумайте название и запишите его",
                                        disable_notification=True)
    await state.set_state(st.NewMeasurement.waiting_for_series_name)
    await state.update_data(msg_id=msg)

@router.message(st.NewMeasurement.waiting_for_series_name)
async def func_new_measurement_save_to_series(message: Message, state: FSMContext):
    await state.update_data(series=message.text)
    data = await state.get_data()
    id = data["msg_id"]

    series_name = data["series"]
    if (len(series_name) > 20) or (" " in series_name):
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        msg = await message.answer(text="⚠️Пожалуйста, ограничьтесь 20 символами (не больше) ⚠️ (пробел нельзя)\n\n"
                                        "Запишите снова")
        await state.update_data(msg_id=msg)
    else:
        access = message.from_user.id

        nominal_value = data["nominal_value"]
        error = data["error"]
        measurement = data["measurement"]

        await dtf.write_series(measurement, series_name, nominal_value, error, access)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=id.message_id)
        await message.delete()
        await message.answer(text=f"Запись добавлена в серию {series_name}!\n\n"
                                  f"Отправьте файл или воспользуйтесь кнопками",
                             reply_markup=ukb.main_menu,
                             parse_mode="HTML",
                             disable_notification=True)
        quantity = data["name"]
        await dtf.delete_measurement(access, measurement, quantity)
        await state.update_data()
        await state.set_state(st.MainMenu.waiting_for_file)


@router.callback_query(F.data.startswith("cd_new_meas_add_to_ser:"))
async def func_new_measurement_select_folder(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    id = data["msg_id"]

    series = (callback.data.split(":", 1)[1])
    access = callback.from_user.id

    nominal_value = data["nominal_value"]
    error = data["error"]
    measurement = data["measurement"]

    await dtf.update_series(access, measurement, series, nominal_value, error)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=id.message_id)
    await callback.message.answer(text=f"Запись добавлена в серию {series}!\n\n"
                                       f"Отправьте файл или воспользуйтесь кнопками",
                                  reply_markup=ukb.main_menu,
                                  parse_mode="HTML",
                                  disable_notification=True)
    quantity = data["name"]
    await dtf.delete_measurement(access, measurement, quantity)
    await state.update_data()
    await state.set_state(st.MainMenu.waiting_for_file)

"""ADD TO SERIES END"""
"""NEW MEASUREMENT END"""

"""MY_MEASUREMENTS"""

@router.callback_query(F.data == "cd_my_meas_no_meas")
async def func_my_meas_no_meas(callback: CallbackQuery):
    await callback.answer(text="Перейдите меню, добавьте запись ✏️ или отправьте файл")

@router.callback_query(F.data == "cd_my_meas")
async def func_my_meas(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    measurements = await dtf.get_measurements(user_id)
    msg = await callback.message.edit_text(text="Выберите запись 💾",
                                           reply_markup=await ukb.my_meas_witch_meas(measurements),
                                           parse_mode="HTML")
    await state.update_data(msg_id=msg)

@router.callback_query(F.data.startswith("cd_my_meas_witch_meas:"))
async def func_my_meas_quantities(callback: CallbackQuery, state: FSMContext):
    msg_id = (await state.get_data())["msg_id"]
    measurement = callback.data.split(":", 1)[1].replace("¤", " ")
    user_id = callback.from_user.id
    await state.update_data(measurement=measurement)

    series_list = await dtf.get_series_list(user_id, measurement)
    series_list = [(series + ":s") for series in series_list]
    quantities_list = await dtf.get_quantities(user_id, measurement)
    quantities_list = [(quantity + ":m") for quantity in quantities_list]

    quantities = series_list + quantities_list
    if msg_id != "don't delete":
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id.message_id)
    msg = await callback.message.answer(text="С какой переменной работать?\n\n"
                                             "Если нужно построить график аппроксимирующей функции, то сейчас выберите "
                                             "независимую величину <i>(ось х)</i>",
                                        reply_markup=await ukb.my_meas_witch_quantity(quantities),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg, measurement=measurement)

@router.callback_query(F.data.startswith("cd_my_meas_quantity:"))
async def func_my_meas_quantity_selected(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_id = data["msg_id"]

    quantity = callback.data.split(":")[1]
    name_postfix = callback.data.split(":")[2]
    await state.update_data(quantity=quantity)
    measurement = data["measurement"]
    user_id = callback.from_user.id
    await state.update_data(measurement=measurement)
    if name_postfix == "s":
        nominals, errors = await dtf.get_series(user_id, measurement, quantity)
        VALUES_X = {quantity: [ufloat(nominal, error) for nominal, error in zip(nominals, errors)]}
        await state.update_data(VALUES_X=VALUES_X)
        values_str = [f"{nominal} +/- {error}" for nominal, error in zip(nominals, errors)]
        values_str = "\n".join(values_str)
        random_error_or_no_str = ""
        kb = await ukb.my_meas_in_series(measurement)
    else:
        values, instrum_error = await dtf.get_from_measurement(user_id, measurement, quantity)
        VALUES_X = {quantity: array(values)}
        await state.update_data(VALUES_X=VALUES_X)
        values_str = [str(value) for value in values]
        values_str = "\n".join(values_str)

        confidence = float((await dtf.get_settings(user_id))["confidence"])
        _, nominal_value, error = await MeasurementProcess({quantity: array(values)}).random_error(quantity,
                                                                                                   instrum_error,
                                                                                                   confidence)
        random_error_or_no_str = f"Случайная погрешность:\n<i>{nominal_value} +/- {error}</i>\n\n"

        await state.update_data(nominal_value=nominal_value)
        await state.update_data(error=error)
        kb = await ukb.my_meas_in_measurement(measurement)

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id.message_id)
    msg = await callback.message.answer(text=f"<b>{quantity}</b>\n"
                                             f"{values_str}\n\n"
                                             f"{random_error_or_no_str}"
                                             f"Если вы хотите выбрать зависимую величину <i>(ось у) для аппроксимации"
                                             f"</i>, то нажмите кнопку <i>\"Зависимая величина 🔎\"</i>",
                                        reply_markup=kb,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_my_meas_add_to_series")
async def func_my_meas_add_to_series(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    user_id = callback.from_user.id
    measurement = data["measurement"]
    series_list = await dtf.get_series_list(user_id, measurement)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Выберите серию, в которую нужно записать",
                                        reply_markup=await ukb.my_meas_witch_series(series_list),
                                        disable_notification=True)
    await state.update_data(msg_id=msg)


@router.callback_query(F.data.startswith("cd_my_meas_add_to_ser:"))
async def func_my_meas_select_series(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    series = (callback.data.split(":", 1)[1])
    await state.update_data(quantity=series)

    nominal_value = data["nominal_value"]
    error = data["error"]

    user_id = callback.from_user.id
    measurement = data["measurement"]
    quantity = data["quantity"]
    await dtf.delete_measurement(user_id, measurement, quantity)
    await dtf.update_series(user_id, measurement, series, nominal_value, error)

    series_list = await dtf.get_series_list(user_id, measurement)
    series_list = [(series + ":s") for series in series_list]
    quantities_list = await dtf.get_quantities(user_id, measurement)
    quantities_list = [(quantity + ":m") for quantity in quantities_list]
    quantities = series_list + quantities_list

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text=f"Запись сохранена в серию {series}!\n\nС какой переменной работать?\n\n"
                                             "Если нужно построить график аппроксимирующей функции, то сейчас выберите "
                                             "независимую величину <i>(ось х)</i>",
                                        reply_markup=await ukb.my_meas_witch_quantity(quantities),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_my_meas_new_series")
async def func_my_meas_new_series(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Придумайте и отправьте название серии",
                                        reply_markup=ukb.my_meas_back_from_new_ser,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)
    await state.set_state(st.MyMeasurements.waiting_for_series_name)





@router.message(st.MyMeasurements.waiting_for_series_name)
async def func_my_meas_added_to_new_ser(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    if (len(message.text) > 20) or " " in message.text:
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text="⚠️Пожалуйста, ограничьтесь 20 символами (не больше) ⚠️(пробел нельзя)\n\n"
                                        "Запишите снова")
        await state.update_data(msg_id=msg)

    else:
        nominal = data["nominal_value"]
        error = data["error"]
        series = message.text
        await state.update_data(quantity=series)

        user_id = message.from_user.id
        measurement = data["measurement"]
        quantity = data["quantity"]

        await dtf.write_series(measurement, series, nominal, error, user_id)
        await dtf.delete_measurement(user_id, measurement, quantity)

        series_list = await dtf.get_series_list(user_id, measurement)
        series_list = [(series + ":s") for series in series_list]
        quantities_list = await dtf.get_quantities(user_id, measurement)
        quantities_list = [(quantity + ":m") for quantity in quantities_list]
        quantities = series_list + quantities_list

        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text=f"Запись сохранена в серию {series}!\n\nС какой переменной работать?\n\n"
                                        f"Если нужно построить график аппроксимирующей функции, то сейчас выберите "
                                        f"независимую величину <i>(ось х)</i>",
                                   reply_markup=await ukb.my_meas_witch_quantity(quantities),
                                   parse_mode="HTML",
                                   disable_notification=True)
        await state.update_data(msg_id=msg)






@router.callback_query(F.data == "cd_my_meas_select_y")
async def func_my_meas_select_y(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    user_id, measurement = callback.from_user.id, data["measurement"]
    quantity = data["quantity"]

    series_list = await dtf.get_series_list(user_id, measurement)
    series_list = [(series + ":s") for series in series_list]
    quantities_list = await dtf.get_quantities(user_id, measurement)
    quantities_list = [(quantity + ":m") for quantity in quantities_list]

    quantities = series_list + quantities_list

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Выберите зависимую величину ниже.",
                                        reply_markup=await ukb.my_meas_witch_y(quantities, quantity),
                                        disable_notification=True)
    await state.update_data(msg_id = msg)

@router.callback_query(F.data.startswith("cd_my_meas_y:"))
async def func_selected_y(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    X_NAME = data["quantity"]
    Y_NAME = callback.data.split(":")[1]
    await state.update_data(X_NAME=X_NAME)
    await state.update_data(Y_NAME=Y_NAME)
    postfix = callback.data.split(":")[2]
    user_id, measurement = callback.from_user.id, data["measurement"]
    if postfix == "s":
        nominals, errors = dtf.get_series(user_id, measurement, Y_NAME)
        VALUES_Y = {Y_NAME: [ufloat(nominal, error) for nominal, error in zip(nominals, errors)]}
        await state.update_data(VALUES_Y=VALUES_Y)
    else:
        values, _ = await dtf.get_from_measurement(user_id, measurement, Y_NAME)
        VALUES_Y = {Y_NAME: array(values)}
        await state.update_data(VALUES_Y=VALUES_Y)

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Выберите функцию зависимости или отправьте прямо сюда другую функцию. \n\n<i>В "
                                             "инструкции на последней странице показано, как правильно вводить функцию "
                                             "(буквально так, как будто вы вводите выражение на Python).</i>",
                                        reply_markup=await ukb.my_meas_select_func_for_approx(X_NAME, Y_NAME),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.set_state(st.MyMeasurements.waiting_for_approx_function)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data.startswith("my_meas_approx:"))
async def func_do_approx(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text="Обработка...")
    data = await state.get_data()
    user_id = callback.from_user.id
    msg = data["msg_id"]

    X_NAME, Y_NAME = data["X_NAME"], data["Y_NAME"]
    X_VALUES, Y_VALUES = data["VALUES_X"], data["VALUES_Y"]
    VALUES = X_VALUES | Y_VALUES
    dependence = [X_NAME, Y_NAME]
    measurement = data["measurement"]
    function_type = callback.data.split(":")[1]
    if function_type == "linear":
        function = f"k * {X_NAME} + b"
    if function_type == "quadratic":
        function = f"a * ({X_NAME} ** 2) + b * {X_NAME} + c"

    APPROX_BYTES_FLOW = await MeasurementProcess(VALUES).approx(dependence=dependence,
                                                                function=function)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)

    if APPROX_BYTES_FLOW == "length mismatch error":
        measurements = await dtf.get_measurements(user_id)
        msg = await callback.message.answer(text="⚠️<b>Длина зависимых и независимых величин должна быть одинаковой."
                                                 "</b>⚠️ Выберите заново",
                                            reply_markup=await ukb.my_meas_witch_meas(measurements),
                                            parse_mode="HTML",
                                            disable_notification=True)
        await state.clear()
        await state.update_data(msg_id=msg)
        return
    if APPROX_BYTES_FLOW == "too few points error":
        msg = await callback.message.answer(text="⚠️<b>Количество точек должно быть больше количества искомых "
                                                 "параметров.</b>⚠️\n\nВыберите функцию зависимости или отправьте "
                                                 "прямо сюда другую функцию. \n\n<i>В инструкции на последней странице "
                                                 "показано, как правильно вводить функцию (буквально так, как будто вы "
                                                 "вводите выражение на Python).</i>",
                                            reply_markup=await ukb.my_meas_select_func_for_approx(X_NAME, Y_NAME),
                                            parse_mode="HTML",
                                            disable_notification=True)
        await state.update_data(msg_id=msg)
        return

    GRAPHIC = BufferedInputFile(APPROX_BYTES_FLOW.getvalue(), filename="graphic.png")
    await callback.message.answer_photo(photo=GRAPHIC,
                                        caption="<i>Картинка не удалится из этого чата</i>",
                                        reply_markup=await ukb.new_meas_approx_done(measurement),
                                        parse_mode="HTML")
    msg = "don't delete"
    await state.update_data(msg_id=msg)

@router.message(st.MyMeasurements.waiting_for_approx_function)
async def func_do_approx_by_user_func(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data["msg_id"]

    X_NAME, Y_NAME = data["X_NAME"], data["Y_NAME"]
    X_VALUES, Y_VALUES = data["VALUES_X"], data["VALUES_Y"]
    VALUES = X_VALUES | Y_VALUES
    dependence = [X_NAME, Y_NAME]
    measurement = data["measurement"]

    function = str(message.text)
    try:
        APPROX_BYTES_FLOW = await MeasurementProcess(VALUES).approx(dependence=dependence,
                                                                    function=function)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

        if APPROX_BYTES_FLOW == "length mismatch error":
            msg = await message.answer(text="⚠️<b>Длина зависимых и независимых величин должна быть одинаковой</b>.⚠️",
                                       reply_markup=await ukb.my_meas_select_func_for_approx(X_NAME, Y_NAME),
                                       parse_mode="HTML",
                                       disable_notification=True)
            await state.update_data(msg_id=msg)
            return
        if APPROX_BYTES_FLOW == "too few points error":
            msg = await message.answer(text="⚠️<b>Количество точек должно быть больше количества искомых параметров</b>"
                                            ".⚠️\n\nВыберите функцию зависимости или отправьте прямо сюда другую "
                                            "функцию. \n\n<i>В инструкции на последней странице показано, как "
                                            "правильно вводить функцию (буквально так, как будто вы вводите "
                                            "выражение на Python).</i>",
                                       reply_markup=await ukb.my_meas_select_func_for_approx(X_NAME, Y_NAME),
                                       parse_mode="HTML",
                                       disable_notification=True)
            await state.update_data(msg_id=msg)
            return

        GRAPHIC = BufferedInputFile(APPROX_BYTES_FLOW.getvalue(), filename="graphic.png")
        await message.answer_photo(photo=GRAPHIC,
                                   caption="<i>Картинка не удалится из этого чата</i>",
                                   reply_markup=await ukb.new_meas_approx_done(measurement),
                                   parse_mode="HTML")
        msg = "don't delete"
        await state.update_data(msg_id=msg)
    except ValueError:
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        photo = FSInputFile("application/assets/Instruction/page6.png")
        msg = await message.answer_photo(photo=photo,
                                         caption="Ой! Похоже вы ввели функцию не так, как положено:(\n"
                                                 "Введите ещё раз по образцу.\nСверху картинка-подсказка:)")
        await state.update_data(msg_id=msg)

"""MY MEASUREMENT -> INDIRECT ERRORS"""
...
"""MY MEASUREMENT INDIRECT ERRORS END"""

"""GET FILE"""

@router.message(st.MainMenu.waiting_for_file)
async def func_get_file(message: Message, state: FSMContext):
    msg = (await state.get_data())["msg_id"]
    if not message.document:
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text="Похоже вы отправили не файл 🫤\n\n"
                                        "Отправьте файл или воспользуйтесь кнопками.",
                                   reply_markup=ukb.main_menu,
                                   disable_notification=True)
        await state.update_data(msg_id=msg)
        return

    document = message.document
    file_id = document.file_id

    file = await message.bot.get_file(file_id)
    file_bytes = await message.bot.download_file(file.file_path)
    file_bytes.seek(0)
    # buf = BytesIO()
    # buf.write(file_bytes.read())

    try:
        if document.file_name.endswith(".csv"):
            MEASUREMENTS = await MeasurementLoader(file_bytes).unpack(mode="csv")
        elif document.file_name.endswith(".xlsx"):
            MEASUREMENTS = await MeasurementLoader(file_bytes).unpack(mode="xlsx")
        else:
            await message.delete()
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            msg = await message.answer(text="Принимаю только .csv и .xlsx 🫤\n\n"
                                            "Отправьте файл или воспользуйтесь кнопками.",
                                       reply_markup=ukb.main_menu,
                                       disable_notification=True)
            await state.update_data(msg_id=msg)
            return

        await state.update_data(MEASUREMENTS_FROM_FILE=MEASUREMENTS)

        folders = await dtf.get_measurements(message.from_user.id)
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text="Отлично! Выберите, куда добавить данные файла.",
                                   reply_markup=await ukb.get_file_witch_folder(folders),
                                   parse_mode="HTML")
        await state.update_data(msg_id=msg)

    except Exception as e:
        print(e)
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text="🫤Что-то пошло не так! Пожалуйста, посмотрите, "
                                        "как заполнять файл в инструкции /instruction.\n\n"
                                        "Отправьте файл или воспользуйтесь кнопками.",
                                   reply_markup=ukb.main_menu,
                                   disable_notification=True)
        await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_get_file_new_folder")
async def func_get_file_new_folder(callback: CallbackQuery, state: FSMContext):
    msg = (await state.get_data())["msg_id"]

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Введите название для новой папки",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)
    await state.set_state(st.GetFolder.waiting_for_folder_name)


@router.message(st.GetFolder.waiting_for_folder_name)
async def func_get_file_get_folder_name(message: Message, state: FSMContext):
    folder_name = message.text
    data = await state.get_data()
    msg = data["msg_id"]
    if len(folder_name) > 20:
        await message.delete()
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        msg = await message.answer(text="⚠️Пожалуйста, ограничьтесь 20 символами (не больше) ⚠️\n\n"
                                        "Запишите снова")
        await state.update_data(msg_id=msg)
        return

    MEASUREMENTS = data["MEASUREMENTS_FROM_FILE"]
    access = message.from_user.id
    instrum_err = (await dtf.get_settings(access))["confidence"]
    for quantity, quant_data in MEASUREMENTS.items():
        await dtf.write_measurement(folder_name, quantity, quant_data, instrum_err, access)

    msg = await message.answer(text="Успешно!\n\n"
                                    "Отправьте файл или воспользуйтесь кнопками.",
                               reply_markup=ukb.main_menu,
                               parse_mode="HTML",
                               disable_notification=True)
    await state.update_data()
    await state.update_data(msg_id=msg)
    await state.set_state(st.MainMenu.waiting_for_file)

@router.callback_query(F.data.startswith("cd_get_file_folder:"))
async def func_write_file_in_folder(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    measurements = data["MEASUREMENTS_FROM_FILE"]
    access = callback.from_user.id
    instrum_err = (await dtf.get_settings(access))["confidence"]

    folder_name = callback.data.split(":")[1].replace("¤", " ")

    for quantity, quant_data in measurements.items():
        await dtf.write_measurement(folder_name, quantity, quant_data, instrum_err, access)
    msg = data["msg_id"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Успешно!\n\n"
                                             "Отправьте файл или воспользуйтесь кнопками.",
                                        reply_markup=ukb.main_menu,
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data()
    await state.update_data(msg_id=msg)
    await state.set_state(st.MainMenu.waiting_for_file)


"""GET FILE END"""

"""SETTINGS"""

@router.callback_query(F.data == "cd_settings")
async def func_settings_opened(callback: CallbackQuery, state: FSMContext):

    access = callback.from_user.id
    settings = await dtf.get_settings(access)
    confidence, separator, ser_detector = settings["confidence"], settings["separator"], settings["detect_series"]
    confidence = round(confidence, 2)
    msg = await callback.message.edit_text(text=f"Текущие настройки:\n"
                                                f"Доверительная вероятность: <code>{confidence}</code>\n"
                                                f"Разделитель файла .csv: <code>{separator}</code>\n"
                                                f"Авто определение серии: <code>В разработке</code>\n\n"
                                                f"Выберите, что хотите изменить.",
                                           reply_markup=ukb.settings,
                                           parse_mode="HTML")
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_settings_confidence")
async def func_witch_setting(callback: CallbackQuery, state: FSMContext):
    msg = (await state.get_data())["msg_id"]

    access = callback.from_user.id
    confidence = round((await dtf.get_settings(access))["confidence"], 2)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text=f"Напишите новое значение (<code>{confidence}</code> текущее)",
                                        reply_markup=ukb.settings_param,
                                        parse_mode="HTML",
                                        disable_notification=True)

    await state.update_data(set_param="confidence", msg_id=msg)
    await state.set_state(st.Settings.wait_for_param_value)


@router.callback_query(F.data == "cd_settings_separator")
async def func_witch_setting(callback: CallbackQuery, state: FSMContext):
    msg = (await state.get_data())["msg_id"]

    access = callback.from_user.id
    separator = (await dtf.get_settings(access))["separator"]
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text=f"Напишите новое значение (\" {separator} \" текущее)",
                                        reply_markup=ukb.settings_param,
                                        parse_mode="HTML",
                                        disable_notification=True)

    await state.update_data(set_param="separator", msg_id=msg)
    await state.set_state(st.Settings.wait_for_param_value)

@router.callback_query(F.data == "cd_settings_auto_ser")
async def func_witch_setting(callback: CallbackQuery):
    await callback.answer(text="Эта крутая фича пока в разработке")

@router.message(st.Settings.wait_for_param_value)
async def func_get_new_set_param(message: Message, state: FSMContext):
    await message.delete()
    data = await state.get_data()
    msg = data["msg_id"]
    param = data["set_param"]
    new_param = message.text
    if param == "confidence":
        try:
            new_param = float(new_param)
        except:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            msg = await message.answer(text="Введите дробь с точкой от нуля до единицы")
            await state.update_data(msg_id=msg)
            return

    access = message.from_user.id

    await dtf.update_settings(access, new_param, param)

    settings = await dtf.get_settings(access)
    confidence, separator, ser_detector = settings["confidence"], settings["separator"], settings["detect_series"]
    confidence = round(confidence, 2)

    await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
    msg = await message.answer(text=f"Успешно.\n\n"
                                    f"Текущие настройки:\n"
                                    f"Доверительная вероятность: <code>{confidence}</code>\n"
                                    f"Разделитель файла .csv: <code>{separator}</code>\n"
                                    f"Авто определение серии: <code>В разработке</code>\n\n"
                                    f"Выберите, что хотите изменить.",
                               reply_markup=ukb.settings,
                               parse_mode="HTML",
                               disable_notification=True)

    await state.clear()
    await state.update_data()
    await state.update_data(msg_id = msg)

"""SETTINGS END"""

"""DELETER"""

@router.callback_query(F.data == "cd_my_meas_del_exp")
async def func_delete_experiment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    msg = data["msg_id"]
    measurement = data["measurement"]

    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text=f"<b>Точно удалить эксперимент {measurement}?</b>",
                                        reply_markup=ukb.sure_delete_exp,
                                        parse_mode="HTML",
                                        disable_notification=False)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_sure_delete_exp")
async def func_sure_delete_exp(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    msg = data["msg_id"]
    measurement = data["measurement"]
    access = callback.from_user.id

    await dtf.delete_exp(measurement, access)
    measurements = await dtf.get_measurements(access)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Успешно!\nВыберите запись 💾",
                                        reply_markup=await ukb.my_meas_witch_meas(measurements),
                                        parse_mode="HTML",
                                        disable_notification=False)
    await state.update_data(msg_id=msg)

@router.callback_query(F.data == "cd_sure_not_delete_exp")
async def func_sure_delete_exp(callback: CallbackQuery, state: FSMContext):
    msg = (await state.get_data())["msg_id"]
    access = callback.from_user.id

    measurements = await dtf.get_measurements(access)
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=msg.message_id)
    msg = await callback.message.answer(text="Выберите запись 💾",
                                        reply_markup=await ukb.my_meas_witch_meas(measurements),
                                        parse_mode="HTML",
                                        disable_notification=True)
    await state.update_data(msg_id=msg)
