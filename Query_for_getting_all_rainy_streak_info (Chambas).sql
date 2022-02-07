SELECT rain_value AS value,
       id_pluviometer AS pluviometer,
       strftime('%Y', register_date) as Year,
       strftime('%d', register_date) as Day
  FROM Registers
 WHERE (strftime('%m', register_date) = '12' ) AND
       (id_pluviometer = 70 OR
        id_pluviometer = 82 OR
        id_pluviometer = 62 OR
        id_pluviometer = 61 OR
        id_pluviometer = 2 OR
        id_pluviometer = 100 OR
        id_pluviometer = 103 OR
        id_pluviometer = 101 OR
        id_pluviometer = 45 OR
        id_pluviometer = 46 OR
        id_pluviometer = 73 OR
        id_pluviometer = 99)
order by Year;