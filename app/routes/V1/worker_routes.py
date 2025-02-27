import flask
import pandas as pd
from flask import Blueprint, render_template
from app.services import WorkerService
worker: flask.blueprints.Blueprint = Blueprint('worker', __name__)

@worker.route('', methods=['GET'])
def workers():
    workers = WorkerService.get_workers()
    dataframe = pd.DataFrame(workers, columns=['full_name', 'password'])

    dataframe.columns = ['ФИО', 'Пароль']

    return render_template(
        "Users.html",
        table=dataframe.to_html(classes='table table-dark border rounded', justify='left', index=False)
    )