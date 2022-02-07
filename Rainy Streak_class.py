# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pickle
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import scipy.integrate as integrate


class Rainy_Streak:
    """
    Clase para calcular coeficiente de concentración temporal diaria
    """

    def __init__(self, df_to_proccess, file_name):
        self.separated_months = self.fill_data_list(df_to_proccess)
        self.df_final = pd.DataFrame(columns=['rainy_days_count', 'rainy_streak_count', 'rainy_streak_med_long'])

        for month in self.separated_months:
            rainy_days_count, rainy_streak_count, rainy_streak_med_long = self.get_rainy_streak(month)

            self.df_final = self.df_final.append({'rainy_days_count': rainy_days_count, 
                                                  'rainy_streak_count': rainy_streak_count, 
                                                  'rainy_streak_med_long':rainy_streak_med_long},
                                 ignore_index=True)

        self.rainy_days_mean = self.df_final['rainy_days_count'].mean()
        self.rainy_streak_mean= self.df_final['rainy_streak_count'].mean()
        self.rainy_streak_med_long_mean = self.df_final['rainy_streak_med_long'].mean()


        # self.info_on_a_row = pd.Series(precip_data['Registro'])
        # self.file_name = file_name
        # self.max_registered_value = self.info_on_a_row.max()
        # self.sum_registered_values = self.info_on_a_row.sum()
        # self.mean = self.info_on_a_row.mean()
        # self.variance = self.info_on_a_row.var()
        # self.std_dev = self.info_on_a_row.std()
        #
        # self.rainy_days_count, self.rainy_streak_count, self.rainy_streak_med_long = self.get_rainy_streak(
        #     self.info_on_a_row)
        # self.rainy_prob = self.rainy_days_count / len(self.info_on_a_row)
        # self.dry_prob = 1 - self.rainy_prob
        # self.rainy_day_after_rain_prob = (self.rainy_days_count - self.rainy_streak_count) / self.rainy_days_count
        # self.rainy_besson = (self.rainy_day_after_rain_prob - self.rainy_prob) / self.dry_prob
        #
        # print(self.rainy_streak_count)
        # print(self.rainy_streak_med_long)
        # print(self.rainy_prob)
        # print(self.rainy_day_after_rain_prob)
        # print(self.rainy_besson)

    def fill_data_list(self, df_to_proccess, ignore_empty_months=True):
        """
        Agarra el arreglo de valores originales, que están a continuación uno del otro y los separa en
        una lista de listas con los valores para cada mes, para ser procesados de forma independiente.
        """
        init_day = 0
        precip_sum = 0
        list_to_return = []
        tmp_list = []
        for i in df_to_proccess.index:
            if df_to_proccess['Day'][i] > init_day:
                init_day = df_to_proccess['Day'][i]
                tmp_list.append(df_to_proccess['value'][i])
                precip_sum += df_to_proccess['value'][i]
            else:
                tmp_list.append(df_to_proccess['value'][i])
                if ignore_empty_months:
                    if precip_sum > 0:
                        list_to_return.append(tmp_list)
                else:
                    list_to_return.append(tmp_list)
                tmp_list = []
                init_day = 0
                precip_sum = 0
        return list_to_return

    def get_rainy_streak(self, data):
        my_stack = list(data)
        rainy_days_count = 0
        full_result = []
        rainy_streaks_list = []
        accumulated = 0
        streak_lenght = 0
        while my_stack:
            s = my_stack.pop(0)
            if s != 0:
                accumulated += s
                streak_lenght += 1
            else:
                if streak_lenght:
                    full_result.append((streak_lenght, accumulated))
                    rainy_streaks_list.append(streak_lenght)
                    rainy_days_count += streak_lenght
                    # print(full_result)
                accumulated = 0
                streak_lenght = 0
            # print(s)
        rainy_streak_count = len(full_result)
        rainy_streak_med_long = 0 if rainy_streak_count == 0 else rainy_days_count / rainy_streak_count
        return rainy_days_count, rainy_streak_count, rainy_streak_med_long

    def exp_function_to_fit(self, x, a, b):
        return a * x * np.exp(b * x)

    def plot_function(self):
        fig = plt.figure()
        axes = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # left, bottom, width, height (range 0 to 1)
        axes.plot(self.df['cumulative_percentage_of_rainy_days_ni_X'],
                  self.df['cumulative_percentage_of_rainfall_amounts_Pi_Y'],
                  'm+', label="Datos experimentales")
        axes.plot(self.xnew, self.ynew_exp, 'r', label='Función ajustada')
        axes.plot(self.xnew, self.ynew_exidist, 'b', label='Línea de equidistribución')
        axes.fill_between(self.xnew, self.ynew_exp, self.ynew_exidist,
                          alpha=0.5)  # representación gráfica de S'=5000-A'

        axes.set_title("Valor de CI calculado: {0}".format(self.ci))
        axes.set_xlabel('Suma acumulativa: Ni (%)')
        axes.set_ylabel('Suma acumulativa: Pi (%)')

        function = ('{0}x*exp({1}x)'
                    .format(round(self.pars_exp[0], 3), round(self.pars_exp[1], 3)))

        from matplotlib.offsetbox import AnchoredText
        at = AnchoredText('f(x)={0}\n R^2 = {1}'
                          .format(function, round(self.R_2, 4)),
                          prop=dict(size=9, color='m'), frameon=True, loc='lower right')
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.3")
        axes.add_artist(at)
        axes.text(40, 30, "S' = 5000-A'")
        axes.legend()
        # fig.savefig(fname=self.file_name + '.svg', format="svg")
        fig.savefig(fname=self.file_name + '.png', dpi=250, format="png")
        # fig.show()


# file_route = ''
# resume_df = pd.DataFrame()
# pluviometer_data = pd.read_csv('test_data.csv')
# rainy_streak = Rainy_Streak(pluviometer_data, 'output')

excel_path = 'Full_data.xlsx'
xlsx = pd.ExcelFile(excel_path)
# lee todas las pestañas
# para el dataframe, en df_dict se obtiene un diccionario con un dataframe por cada sheet del excel
# df_dict = pd.read_excel(xlsx, sheet_name=None)

# df_dict = pd.read_excel(xlsx, sheet_name='01')
# df_to_proccess = df_dict.loc[:, ['value', 'Day']]
# rainy_streak = Rainy_Streak(df_to_proccess, 'output')



resume_df = pd.DataFrame()
with pd.ExcelWriter('output.xlsx') as writer:
    for month in range(12):
        print(month+1)
        df_dict = pd.read_excel(xlsx, sheet_name=month)
        df_to_proccess = df_dict.loc[:, ['value', 'Day']]
        rainy_streak = Rainy_Streak(df_to_proccess, 'output')
        
        pd_test = pd.DataFrame([[
            rainy_streak.rainy_days_mean, 
            rainy_streak.rainy_streak_mean,
            rainy_streak.rainy_streak_med_long_mean
        ]],
            columns=['Promedio de días lluviosos',
                     'Cantidad promedio de rachas',
                     'Duración media de las rachas',
                      ],
            index=['mes ' + str(month+1)])
        
        resume_df = resume_df.append(pd_test)
    print(resume_df)
    resume_df.to_excel(writer, sheet_name='Resumen')