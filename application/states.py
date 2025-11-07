from aiogram.fsm.state import State, StatesGroup

class Instruction(StatesGroup):
    instruction_state = State()

class MainMenu(StatesGroup):
    waiting_for_file = State()

class GetFolder(StatesGroup):
    waiting_for_folder_name = State()

class NewMeasurement(StatesGroup):
    waiting_for_num = State()
    waiting_for_instrum_err = State()
    waiting_for_name = State()
    waiting_for_folder_name = State()
    waiting_for_series_name = State()

class MyMeasurements(StatesGroup):
    start = State()
    waiting_for_series_name = State()
    waiting_for_approx_function = State()

class Settings(StatesGroup):
    wait_for_param_value = State()