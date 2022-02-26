# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from numba import jit


# import pickle
# import matplotlib.pyplot as plt


class Rainy_Streak:
    """
    Clase para calcular coeficiente de concentración temporal diaria
    """

    def __init__(self, df_to_proccess, file_name):
        self.separated_months = self.fill_data_list(df_to_proccess)
        self.df_final = pd.DataFrame(columns=['rainy_days_count', 'rainy_streak_count', 'rainy_streak_med_long'])

        for month in self.separated_months:
            rainy_days_count, rainy_streak_count, rainy_streak_med_long, streak_counter_if_length_more_than_one, irregularity_index, streak_avg_lenght_if_length_more_than_one = self.get_rainy_streak_data(month)

            rain_probability = rainy_days_count / len(month)

            rain_probability_if_before = 0 if rainy_days_count == 0 else (rainy_days_count - rainy_streak_count) / rainy_days_count
            coef_rainy_besson = (rain_probability_if_before - rain_probability) / (1 - rain_probability)

            self.df_final = self.df_final.append({'rainy_days_count': rainy_days_count,
                                                  'rainy_streak_count': rainy_streak_count,
                                                  'rainy_streak_med_long': rainy_streak_med_long,
                                                  'rain_probability': rain_probability,
                                                  'rain_probability_if_before': rain_probability_if_before,
                                                  'coef_rainy_besson': coef_rainy_besson,
                                                  'streak_counter_if_length_more_than_one': streak_counter_if_length_more_than_one,
                                                  'irregularity_index': irregularity_index,
                                                  'streak_avg_lenght_if_length_more_than_one': streak_avg_lenght_if_length_more_than_one
                                                  },
                                                 ignore_index=True)

        self.rainy_days_mean = self.df_final['rainy_days_count'].mean()
        self.rainy_streak_mean = self.df_final['rainy_streak_count'].mean()
        self.rainy_streak_med_long_mean = self.df_final['rainy_streak_med_long'].mean()
        self.rain_probability_mean = self.df_final['rain_probability'].mean()
        self.rain_probability_if_before_mean = self.df_final['rain_probability_if_before'].mean()
        self.coef_rainy_besson_mean = self.df_final['coef_rainy_besson'].mean()
        self.streak_counter_if_length_more_than_one_mean = self.df_final['streak_counter_if_length_more_than_one'].mean()
        self.irregularity_index_mean = self.df_final['irregularity_index'].mean()
        self.streak_avg_lenght_if_length_more_than_one_mean = self.df_final.streak_avg_lenght_if_length_more_than_one[self.df_final.streak_avg_lenght_if_length_more_than_one > 0].mean()
        
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

    @jit(cache = True)
    def get_rainy_streak_data(self, data):
        my_stack = list(data)
        rainy_days_count = 0
        full_result = []
        rainy_streaks_list = []
        accumulated = 0
        streak_lenght = 0
        streak_counter_if_length_more_than_one = 0
        streak_lenght_if_length_more_than_one = 0
        sum_ln_Pi = 0
        while my_stack:
            s = my_stack.pop(0)
            if s != 0:
                accumulated += s
                streak_lenght += 1
                sum_ln_Pi += abs(np.log((s+1/s)))
            else:
                if streak_lenght:
                    full_result.append((streak_lenght, accumulated))
                    rainy_streaks_list.append(streak_lenght)
                    rainy_days_count += streak_lenght
                    if streak_lenght > 1:
                        streak_counter_if_length_more_than_one += 1
                        streak_lenght_if_length_more_than_one += streak_lenght
                    # print(full_result)
                accumulated = 0
                streak_lenght = 0
            # print(s)
        rainy_streak_count = len(full_result)
        rainy_streak_med_long = 0 if rainy_streak_count == 0 else rainy_days_count / rainy_streak_count
        irregularity_index = (1/(len(data)-1))*sum_ln_Pi
        streak_avg_lenght_if_length_more_than_one = 0 if not streak_counter_if_length_more_than_one else streak_lenght_if_length_more_than_one/streak_counter_if_length_more_than_one
        
        return rainy_days_count, rainy_streak_count, rainy_streak_med_long, streak_counter_if_length_more_than_one, irregularity_index, streak_avg_lenght_if_length_more_than_one
               


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
        print(month + 1)
        df_dict = pd.read_excel(xlsx, sheet_name=month)
        df_to_proccess = df_dict.loc[:, ['value', 'Day']]
        rainy_streak = Rainy_Streak(df_to_proccess, 'output')

        pd_test = pd.DataFrame([[
            rainy_streak.rainy_days_mean,
            rainy_streak.rainy_streak_mean,
            rainy_streak.streak_counter_if_length_more_than_one_mean,
            rainy_streak.streak_avg_lenght_if_length_more_than_one_mean,
            rainy_streak.rainy_streak_med_long_mean,
            rainy_streak.rain_probability_mean,
            rainy_streak.rain_probability_if_before_mean,
            rainy_streak.coef_rainy_besson_mean,
            rainy_streak.irregularity_index_mean,
        ]],
            columns=['Promedio de días lluviosos',
                     'Cantidad promedio de rachas',
                     'Cantidad promedio de rachas de más de un día',
                     'Duración media de las rachas de más de un día',
                     'Duración media de las rachas (Todas)',
                     'Probabilidad media de días lluviosos',
                     'Probabilidad media de días lluviosos si llovió el anterior',
                     'Coeficiente de Besson',
                     'Índice de irregularidad temporal',
                     ],
            index=['mes ' + str(month + 1)])

        resume_df = resume_df.append(pd_test)

    resume_df.to_excel(writer, sheet_name='Resumen')
    print('Terminado!!!')
