import os

from flask import Flask, render_template, request
import sqlite3



def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # -----------------PARTIE FLASK-----------------

    # Accès à la base de données
    conn = sqlite3.connect('inginious.sqlite', check_same_thread=False)

    # Le curseur permettra l'envoi des commandes SQL
    cursor = conn.cursor()

    # valeur de recherche d'élève


    def data(course):
        labels = []
        values = []

        for task, sub in cursor.execute(
                "SELECT task, COUNT(task) FROM submissions WHERE course=(?) GROUP BY task ORDER BY task", (course,)):
            labels.append(task)
            values.append(sub)

        return labels, values

    def date(task):
        list_date = []
        list_sub = []
        for row, sub in cursor.execute("SELECT SUBSTR(submitted_on, 1, 10), COUNT(*) FROM submissions WHERE task=(?) "
                                       "GROUP BY SUBSTR(submitted_on, 1, 10) ORDER BY SUBSTR(submitted_on, 1, 10)",
                                       (task,)):
            if row[0] not in list_date:
                list_date.append(row)
                list_sub.append(sub)
        return list_date, list_sub

    def success_data(course):
        labels = []
        values = []
        value = []

        if course == 'all':
            for success, number in cursor.execute(
                    "SELECT succeeded, COUNT(succeeded) FROM user_tasks GROUP BY succeeded ORDER BY succeeded"):
                if success=='true':
                    labels.append('succeed')
                elif success=='false':
                    labels.append('failed')
                value.append(number)
            total = value[0] + value[1]

            for i in value:
                percent = (i / total) * 100
                values.append(int(percent))

        else:
            for success, number in cursor.execute(
                    "SELECT succeeded, COUNT(succeeded) FROM user_tasks WHERE course=(?) GROUP BY succeeded ORDER BY succeeded",
                    (course,)):
                if success=='true':
                    labels.append('succeed')
                elif success=='false':
                    labels.append('failed')
                value.append(number)
            total = value[0] + value[1]

            for i in value:
                percent = (i / total) * 100
                values.append(int(percent))
        return labels, values

    app = Flask(__name__)

    @app.route('/')
    @app.route('/index.html')
    def index():
        """
        retourne la page index.html
        """
        return render_template('index.html')

    @app.route('/LEPL1402.html')
    def LEPL1402():
        """
        retourne la page LEPL1402.html
        """
        labels, values = data('LEPL1402')

        return render_template('LEPL1402.html', labels=labels, values=values)

    @app.route('/LSINF1101.html')
    def LSINF1101():
        """
        retourne la page LSINF1101.html
        """
        labels, values = data('LSINF1101-PYTHON')

        return render_template('LSINF1101.html', labels=labels, values=values)

    @app.route('/LSINF1252.html')
    def LSINF1252():
        """
        retourne la page LSINF1252.html
        """
        labels, values = data('LSINF1252')

        return render_template('LSINF1252.html', labels=labels, values=values)

    @app.route('/studentstat.html', methods=['GET','POST'])
    def studentstat():
        if request.method == 'POST':
            user = request.form.get('studsearch').lower()
            labels=[]
            values=[]
            for task in cursor.execute(
                    "select task, avg(grade) from submissions where username = (?) group by task order by task", (user,)):

                labels.append(task[0])
                values.append(task[1])


            return render_template('studentstat.html', labels=labels, values=values, user=user)

        return render_template('studentstat.html', labels=('?'), values=0, user='Student')

    @app.route('/date.html', methods=['GET','POST'])
    def page_date():

        dropdown = []
        for row in cursor.execute("SELECT DISTINCT task FROM submissions"):
            dropdown.append(row[0])

        labels, values = date('TextToDic')
        if request.method == 'POST':
            task = request.form.get('dropdown')
            labels, values = date(task)
            return render_template('date.html', labels=labels, values=values, dropdown=dropdown, task=task)

        return render_template('date.html', labels=labels, values=values, dropdown=dropdown, task='TextToDic')

    @app.route('/success_rate.html')
    def success_rate():
        """
        retourne la page success_rate.html
        """
        labels, values = success_data('all')

        return render_template('success_rate.html', labels=labels, values=values)

    @app.route('/LSINF1101_success_rate.html')
    def LSINF1101_success_rate():
        """
        retourne la page success_rate.html
        """
        labels, values = success_data('LSINF1101-PYTHON')

        return render_template('LSINF1101_success_rate.html', labels=labels, values=values)

    @app.route('/LSINF1252_success_rate.html')
    def LSINF1252_success_rate():
        """
        retourne la page success_rate.html
        """
        labels, values = success_data('LSINF1252')

        return render_template('LSINF1252_success_rate.html', labels=labels, values=values)

    @app.route('/LEPL1402_success_rate.html')
    def LEPL1402_success_rate():
        """
        retourne la page success_rate.html
        """
        labels, values = success_data('LEPL1402')

        return render_template('LEPL1402_success_rate.html', labels=labels, values=values)

    @app.route('/difficulty.html')
    def difficulty():
        """
        retourne la page difficulty.html
        """
        labels = []
        values = []
        sql = cursor.execute("select task, AVG_Grade from (select task, AVG(grade) as AVG_Grade from submissions group by task order by AVG_Grade) where AVG_Grade > 0 limit 15;")
        for task, grade in sql:
            labels.append(task)
            values.append(grade)


        return render_template('difficulty.html', labels=labels, values=values)

    return app
