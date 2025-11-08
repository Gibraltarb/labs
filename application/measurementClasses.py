import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
from scipy import stats
from scipy.optimize import curve_fit
import sympy as sp
from uncertainties import ufloat, nominal_value
import pandas as pd
from io import BytesIO
import base64
import ast
from application.utils import round_m


class MeasurementLoader():

    def __init__(self, measurement):
        self.measurement = measurement

    async def _unpack_fsm(self, counter):
        """
        :param counter: number of values for a quantity
        :return: universal data array for the math processing stage: {quantity: [values]}
        """
        xoryx = 0
        if list(self.measurement.keys())[-1][0] == "y":
            xoryx = 1

        x = np.array([self.measurement[f"x{index}"] for index in range(1, counter + 1)])
        if xoryx == 0:
            return {"x": x}
        if xoryx == 1:
            y = np.array([self.measurement[f"y{index}"] for index in range(1, counter + 1)])
            return {"x": x, "y": y}

    async def _unpack_csv(self, sep=";"):
        """
        :param sep: separator between columns for reading csv tables. Use in pandas.read_csv(..., sep=sep)
        :raises ValueError: if no values are found for sent table
        :return: universal data array for the math processing stage: {quantity: [values], ...}
        """

        data = self.measurement
        table = pd.read_csv(data, sep=sep)
        table.columns = [col.strip() for col in table.columns]
        result = {quantity: np.array(table[quantity].tolist())
                  for quantity in table.columns
                  if table[quantity].dropna().tolist()}
        if not result:
            raise ValueError(f"В таблице не найдено доступных значений для unpack_csv")
        return result

    async def _unpack_xlsx(self, sheet_name=0):
        """
        :param sheet_name: name or index of the sheet to load. Default = 0 (first sheet in the table)
        :raises ValueError: if no values are found for sent table
        :return: universal data array for the math processing stage: {quantity: [values], ...}
        """

        data = self.measurement
        table = pd.read_excel(data, sheet_name=sheet_name)
        table.columns = [col.strip() for col in table.columns]
        result = {quantity: np.array(table[quantity].tolist())
                  for quantity in table.columns
                  if table[quantity].dropna().tolist()}
        if not result:
            raise ValueError(f"В таблице не найдено доступных значений для unpack_xlsx")
        return result

    async def unpack(self, mode: str, **kwargs) -> dict:
        """
        :param mode: unpack mode, literally the extension of file to load: "csv", "xlsx". "fsm" - state data in aiogram
        :param kwargs: some params for additional params for specific unpack-methods: sheet_name=0, sep=";", ...
        :raises ValueError: if the data unpacking mode is unknown
        :return: universal data array for the math processing stage: {quantity: [values], ...}
        """

        mode = mode.lower()

        if mode == "fsm":
            return await self._unpack_fsm(**kwargs)
        if mode == "csv":
            return await self._unpack_csv(**kwargs)
        if mode == "xlsx":
            return await self._unpack_xlsx(**kwargs)
        raise ValueError(f"Неизвестный режим распаковки данных '{mode}'. Поддерживаемые режимы: csv, fsm, xlsx")

class MeasurementProcess(dict):

    def __init__(self, measurement: dict):
        self.measurement = measurement

    async def _len_check(self) -> bool:
        """
        :return: True means all quantities have the same number of values, False - different
        """

        lengths = [len(values) for values in self.measurement.values()]
        return all(length == lengths[0] for length in lengths)

    async def _assemble_series(self, quantities, instrument_error, confidence=0.95):
        """
        :param quantities: a sequence of data sets for a variable ["t-1", "t-2", ...]
        :param instrument_error:
        :param confidence: param for calculating Student's t-test coef
        :return: dictionary with one element where key is name of quantity
                 and value is list of ufloat values {"t": [13 +/- 1, 14 +/- 1.5]}
        """

        q = quantities[0].split("-", 1)[0]
        return {f"{q}": [await self.random_error(self.measurement[quantity], confidence, instrument_error) for quantity in quantities]}

    async def mean(self, quantity):
        """
        :param quantity: defines an array of values for which the method should be applied
        :return: mean value of the selected quantity array
        """
        return self.measurement[quantity].mean()

    async def random_error(self, quantity, instrument_error, confidence=0.95):
        """
        :param quantity: defines an array of values for which the method should be applied
        :param confidence: param for calculating Student's t-test coef
        :return: uncertainties.ufloat value (mean value +/- error); mean value; error
        """

        measurements = self.measurement[quantity]
        length = len(measurements)
        std = measurements.std(ddof=1)
        error = stats.t.ppf((1 + confidence) / 2, length - 1) * std / np.sqrt(length)
        mean, mean_ufl = await round_m(measurements.mean(), m=4), measurements.mean()
        ins_error = (instrument_error / 3) * stats.t.ppf((1 + confidence) / 2, 1000000)
        absolute_error, absolute_error_ufl =  (await round_m(np.sqrt((error ** 2) + (ins_error ** 2)), m=4),
                                               np.sqrt((error ** 2) + (ins_error ** 2)))
        return ufloat(mean_ufl, absolute_error_ufl), mean, absolute_error

    async def indirect(self, function, instrument_error, confidence=0.95):
        """
        :param function: a math expression for which the error is calculated
        :param confidence: param for calculating Student's t-test coef
        :raises ValueError: if the expression could not be calculated
        :return: uncertainties.ufloat value (mean +/- error) for expression result
        """

        from uncertainties.umath import __dict__ as ufuncs

        numpy_things = ["np", "e", "pi", "log", "sin", "cos", "exp", "sqrt", "inf", "acos", "asin", "atan"]
        tree = ast.parse(function, mode="eval")
        quantities = {node.id for node in ast.walk(tree)
                      if isinstance(node, ast.Name)
                      and node.id not in numpy_things
                      }
        u_quantities = {}
        for quantity in quantities:
            if quantity not in self.measurement:
                raise ValueError(f"Переменная {quantity} отсутствует в множестве экспериментальных данных")
            uval, _, _ = await self.random_error(quantity, confidence, instrument_error)
            u_quantities[quantity] = uval
        u_quantities.update(ufuncs)
        try:
            result = eval(function, {"np": np, "e": np.e, "pi": np.pi, "log": np.log, "sin": np.sin, "cos": np.cos,
                                     "exp": np.exp, "sqrt": np.sqrt, "inf": np.inf, "acos": np.acos, "asin": np.asin,
                                     "atan": np.atan}, u_quantities)
            nominal_value = result.n
            error = result.s

        except Exception as e:
            raise ValueError(f"Не удалось вычислить выражение {function}. Ошибка: {e}")

        return result, nominal_value, error

    async def approx(self, dependence=["x", "y"], function="k * x + b"):
        """
        :param dependence: list of strings. First str is name of independent quantity, second - dependent
        :param function: assumed dependency function
        :raises ValueError: if quantity not founded; if not found independent in selected function
        :return: A picture with a graph, a function, a correlation coefficient, and points.
                 All of this is encoded in a byte flow
        """

        DRAW_X_ERRORBAR = False
        DRAW_Y_ERRORBAR = False
        print(1)
        try:
            x_quantity = dependence[0]
            y_quantity = dependence[1]
            if type(self.measurement[x_quantity][0]) == ufloat:
                DRAW_X_ERRORBAR = True
                x_data = []
                x_err_data = []
                for x in self.measurement[x_quantity]:
                    x_data.append(x.n)
                    x_err_data.append(x.s)
                x_data, x_err_data = np.array(x_data), np.array(x_err_data)
            else:
                x_data = self.measurement[x_quantity]

            if type(self.measurement[y_quantity][0]) == ufloat:
                DRAW_Y_ERRORBAR = True
                y_data = []
                y_err_data = []
                for x in self.measurement[x_quantity]:
                    y_data.append(x.n)
                    y_err_data.append(x.s)
                y_data, y_err_data = np.array(y_data), np.array(y_err_data)
            else:
                y_data = self.measurement[y_quantity]

        except: raise ValueError("Одна из переменных не была найдена. Не удалось построить зависимость")
        print(2)

        if f"{x_quantity}" not in function:
            raise ValueError("В функции не обнаружена независимая величина, выбранная пользователем")
        print(3)

        if len(x_data) != len(y_data):
            return "length mismatch error"
        print(4)

        if "=" in function:
            function = function.split("=", 1)[1].strip()

        numpy_things = ["np", "e", "pi", "log", "sin", "cos", "exp", "sqrt", "inf", "acos", "asin", "atan"]
        tree = ast.parse(function, mode="eval")
        quantities = sorted({node.id for node in ast.walk(tree)
                             if isinstance(node, ast.Name)
                             and node.id != x_quantity
                             and node.id not in numpy_things
                             })

        print(quantities)
        if len(quantities) + 1 > len(x_data):
            return "too few points error"

        lambda_code = f"lambda {', '.join([x_quantity] + quantities)}: {function}"
        f = eval(lambda_code, {"np": np, "e": np.e, "pi": np.pi, "log": np.log, "sin": np.sin, "cos": np.cos,
                               "exp": np.exp, "sqrt": np.sqrt, "inf": np.inf, "acos": np.acos, "asin": np.asin,
                               "atan": np.atan})
        popt, pcov = curve_fit(f, x_data, y_data)
        f = np.vectorize(f)
        interval = (max(x_data) - min(x_data)) / 2
        x_fit = np.linspace(min(x_data) - interval, max(x_data) + interval, 250)
        y_fit = np.array(f(x_fit, *popt))

        # Confidence of approximating function
        all_symbols = [x_quantity] + quantities
        symbols_dict = dict(zip(all_symbols, sp.symbols(all_symbols)))
        f_sym = sp.sympify(function, locals=symbols_dict)
        y_err = []
        for xi in x_fit:
            subs_dict = {symbols_dict[x_quantity]: xi}
            for name, value in zip(quantities, popt):
                subs_dict[symbols_dict[name]] = value
            J = np.array([float(sp.diff(f_sym, symbols_dict[quantity]).evalf(subs=subs_dict))
                          for quantity in quantities])
            sigma = np.sqrt(J @ pcov @ J.T)
            y_err.append(sigma)
        y_err = np.array(y_err)

        # Pearson's correlation coefficient
        PearsonR, _ = stats.pearsonr(x_data, y_data)

        # drawing a function graphic with pyplot
        coefsList = []
        for qtty, vle in zip(quantities, popt):
            coefsList.append(f"{qtty} = {vle:.3f}")
        coefs = ", ".join(coefsList)

        plt.figure(figsize=(10, 10))
        plt.plot(x_fit, y_fit, color="#809bce", label=f"Аппроксимирующая функция\n"
                                                      f"Коэффициенты: {coefs}\n"
                                                       f"r = {PearsonR:.3f} (только для линейной зависимости)")
        plt.fill_between(x_fit, y_fit - y_err, y_fit + y_err, color="#a8dcd1",
                         alpha=0.3, label="Доверительный интервал")
        plt.scatter(x_data, y_data, marker=".", color="#ff715b", label="Исходные данные")

        if DRAW_X_ERRORBAR:
            plt.errorbar(x_data, y_data, xerr=x_err_data, color="#a8dcd1")
        if DRAW_Y_ERRORBAR:
            plt.errorbar(x_data, y_data, yerr=y_err_data, color="#a8dcd1")

        plt.xlabel(f"{x_quantity}")
        plt.ylabel(f"{y_quantity}")
        plt.title(f"(tg: @cessing_bot)\nВаша зависимость {y_quantity} от {x_quantity}")
        plt.legend()
        plt.grid()

        # save graphic as bytes flow
        buf = BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)

        graph = Image.open(buf)
        logo_watermark = Image.open("application/assets/watermarks/cessing_logo_watermark.png")
        scale_logo = graph.width // 10
        logo_watermark = logo_watermark.resize((scale_logo, int(scale_logo * logo_watermark.height / logo_watermark.width)),
                                               Image.LANCZOS)
        position_logo = ((graph.width // 2) + 300, logo_watermark.height - 100)


        graph.paste(logo_watermark, position_logo, logo_watermark)

        buf = BytesIO()
        graph.save(buf, format="PNG")
        buf.seek(0)

        return buf