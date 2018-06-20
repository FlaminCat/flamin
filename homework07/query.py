from tabulate import tabulate
import psycopg2

conn = psycopg2.connect("host=localhost port=5432 dbname=postgres user=postgres password=secret")
cursor = conn.cursor()

def fetch_all(cursor):
    colnames = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    return [{colname:value for colname, value in zip(colnames, record)} for record in records]

""" Вопрос 1. Сколько мужчин и женщин представлено в этом наборе данных? """

cursor.execute(
    """
    SELECT gender, AVG(height) as avg_height, AVG(weight) as avg_weight
		FROM train
		GROUP BY gender
    """
)
print('Вопрос 1')
print(tabulate(fetch_all(cursor), "keys", "psql"))

"""Вопрос 2. Кто в среднем реже указывает, что употребляет алкоголь – мужчины или женщины?"""

cursor.execute(
    """
    SELECT DISTINCT 
    ((SELECT COUNT(*) FROM train WHERE (alco::INT) = 1 AND gender = 1) / 
    (SELECT COUNT(*) FROM train WHERE gender = 1)::numeric) * 100 as alco_women_percent
    FROM train
    """
)
print('Вопрос 2')
print('Процент женщин, указавших употребление алкоголя')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute(
    """
    SELECT DISTINCT 
    ((SELECT COUNT(*) FROM train WHERE (alco::INT) = 1 AND gender = 2) / 
    (SELECT COUNT(*) FROM train WHERE gender = 2)::numeric) * 100 as alco_men_percent
    FROM train
    """
)
print('Процент мужчин, указавших употребление алкоголя')
print(tabulate(fetch_all(cursor), "keys", "psql"))

"""Вопрос 3. Во сколько раз (округленно) процент курящих среди мужчин больше, чем процент курящих среди женщин?"""

cursor.execute(
    """
    SELECT DISTINCT ROUND(
    (SELECT (AVG(smoke::int)) FROM train WHERE gender = 2) /
    (SELECT (AVG(smoke::int)) FROM train WHERE gender = 1)) as difference_smoke_percent
    FROM train
    """
)
print('Вопрос 3')
print(tabulate(fetch_all(cursor), "keys", "psql"))

"""Вопрос 4. Догадайтесь, в чём здесь измеряется возраст, и ответьте, 
на сколько месяцев (примерно) отличаются медианные значения возраста курящих и некурящих."""

cursor.execute(
    """
    CREATE FUNCTION _final_median(anyarray) RETURNS float8 AS $$ 
        WITH q AS
        (
            SELECT val
            FROM unnest($1) val
            WHERE VAL IS NOT NULL
            ORDER BY 1
        ),
        cnt AS
        (
            SELECT COUNT(*) AS c FROM q
        )
        SELECT AVG(val)::float8
        FROM 
        (
            SELECT val FROM q
            LIMIT  2 - MOD((SELECT c FROM cnt), 2)
            OFFSET GREATEST(CEIL((SELECT c FROM cnt) / 2.0) - 1,0)  
        ) q2;
    $$ LANGUAGE SQL IMMUTABLE;
 
    CREATE AGGREGATE median(anyelement) (
        SFUNC=array_append,
        STYPE=anyarray,
        FINALFUNC=_final_median,
        INITCOND='{}'
    );
    """
)

cursor.execute(
    """
    SELECT DISTINCT ROUND(
    ((SELECT MEDIAN(age) FROM train WHERE (smoke::int) = 0) - 
    (SELECT MEDIAN(age) FROM train WHERE (smoke::int) = 1)) / 30) AS difference_smoke_age
    FROM train
    """
)
print('Вопрос 4')
print(tabulate(fetch_all(cursor), "keys", "psql"))

""" Вопрос 5. Сформировано 2 подвыборки курящих мужчин возраста от 60 до 64 лет включительно: 
первая с верхним артериальным давлением строго меньше 120 мм рт.ст. и концентрацией холестерина – 4 ммоль/л, 
а вторая – с верхним артериальным давлением от 160 (включительно) до 180 мм рт.ст. (не включительно) и концентрацией холестерина – 8 ммоль/л.
Во сколько раз (округленно) отличаются доли больных людей (согласно целевому признаку, cardio) в этих двух подвыборках? """

cursor.execute(
    """
    SELECT DISTINCT ROUND(
    (SELECT COUNT(*) FROM train
    WHERE (ap_hi < 120) AND (cholesterol = 1) AND ((cardio::int) = 1)) /
    (SELECT COUNT(*) FROM train
    WHERE (ap_hi < 180) AND (160 <= ap_hi) AND (cholesterol = 3) AND ((cardio::int) = 1)))
    FROM TRAIN
    WHERE gender = 2 AND (60 <= ((age::int) / 365)) AND (((age::int) / 365) <= 64)
    """
)
print('Вопрос 5')
print(tabulate(fetch_all(cursor), "keys", "psql"))

"""Вопрос 6. Постройте новый признак – BMI. Для этого надо вес в килограммах поделить на квадрат роста в метрах. 
Нормальными считаются значения BMI от 18.5 до 25. Выберите верные утверждения.
Утверждения:
- Медианный BMI по выборке превышает норму
- У женщин в среднем BMI ниже, чем у мужчин
- У здоровых в среднем BMI выше, чем у больных
- В сегменте здоровых и непьющих мужчин в среднем BMI ближе к норме, чем в сегменте здоровых и непьющих женщин"""

cursor.execute(
    """
    SELECT MEDIAN (weight / ((height / 100) ^ 2))
    FROM train
    """
)
print('Вопрос 6')
print('Медианный BMI по выборке')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute(
    """
    SELECT (CASE WHEN gender = 1 THEN 'female' ELSE 'male' END) as sex, 
    AVG(weight / ((height / 100) ^ 2)) as avg_bmi
    FROM train
    GROUP BY gender
    """
)
print('Средний BMI по выборке среди мужчин и женщин')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute(
    """
    SELECT (CASE WHEN cardio = True THEN 'sick' ELSE 'healthy' END), 
    AVG(weight / ((height / 100) ^ 2)) as avg_bmi
    FROM train
    GROUP BY cardio
    """
)
print('Средний BMI по выборке среди здоровых и больных')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute(
    """
    SELECT (CASE WHEN gender = 1 THEN 'female' ELSE 'male' END) as sex, AVG(weight / ((height / 100) ^ 2)) as avg_bmi
    FROM train
    WHERE cardio = False AND alco = FALSE
    GROUP BY gender
    """
)
print('Средний BMI по выборке среди здоровых и непьющих мужчин и женщин')
print(tabulate(fetch_all(cursor), "keys", "psql"))

"""Вопрос 7. Можно заметить, что в данных много грязи и неточностей.
Отфильтруйте следующие сегменты пациентов:
- указанное нижнее значение артериального давления строго выше верхнего
- рост строго меньше 2.5%-перцентили или строго больше 97.5%-перцентили 
- вес строго меньше 2.5%-перцентили или строго больше 97.5%-перцентили
Сколько процентов данных (округленно) мы выбросили?"""

cursor.execute(
    """
    SELECT DISTINCT ROUND(
    (SELECT COUNT(*) FROM train
    WHERE (ap_lo > ap_hi) 
    OR height < (SELECT PERCENTILE_DISC(0.025) WITHIN GROUP (ORDER BY height) FROM train)
    OR (SELECT PERCENTILE_DISC(0.975) WITHIN GROUP (ORDER BY height) FROM train) < height
    OR weight < (SELECT PERCENTILE_DISC(0.025) WITHIN GROUP (ORDER BY weight) FROM train)
    OR (SELECT PERCENTILE_DISC(0.975) WITHIN GROUP (ORDER BY weight) FROM train) < weight)::numeric /
    (SELECT COUNT(*) FROM train)::numeric * 100) as dirty_percent
    FROM train
    """
)
print('Вопрос 7')
print(tabulate(fetch_all(cursor), "keys", "psql"))


