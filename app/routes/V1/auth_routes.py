import flask
from flask import render_template
from flask import Blueprint, Response, request, current_app, json
from app.services import AuthorizationService
import qrcode
from io import BytesIO
from flask import send_file, request
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
auth: flask.blueprints.Blueprint = Blueprint('auth', __name__)


@auth.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        data = request.json
        name = data.get('name', None)
        surname = data.get('surname', None)
        patronymic = data.get('patronymic', None)
        password = data.get('password', None)
        tokens = data.get('tokens',None)
        if not all([name, surname,patronymic,password,tokens]):
            return current_app.response_class(
                response=json.dumps({'error': 'No params provided'}),
                status=400,
                mimetype='application/json'
            )

        w_id = AuthorizationService.register(name, surname, patronymic,password,tokens)

        if w_id:
            return current_app.response_class(
                response=json.dumps({"msg": "Worker registered successfully", "worker_id": w_id}),
                status=200,
                mimetype='application/json'
            )
        else:
            return current_app.response_class(
                response=json.dumps({'error': 'An error occurred during register'}),
                status=500,
                mimetype='application/json'
            )
    elif request.method == 'GET':
        return render_template('register.html')


@auth.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    surname = data.get('surname', '')
    name = data.get('name', '')
    patronymic = data.get('patronymic', '')
    password = data.get('password', '')

    qr_text = f"name{name},surname{surname},patronymic{patronymic},password{password}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=20,
        border=4,
    )
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save("qrcode.png")

    pdf_file = "qrcode.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)
    width, height = letter

    qr_size = 300
    x = (width - qr_size) / 2
    y = (height - qr_size) / 2

    c.drawImage("qrcode.png", x, y, width=qr_size, height=qr_size)
    c.save()

    return current_app.response_class(
        response=json.dumps({"msg": "QR code generated"}),
        status=200,
        mimetype='application/json'
    )



@auth.route('/login', methods=['POST'])
def login() -> Response:
    data = request.json
    qrcode = data.get('qrcode')
    qrcode_data = qrcode.split(",")
    surname = qrcode_data[1][7:]
    name = qrcode_data[0][4:]
    patronymic = qrcode_data[2][10:]
    password = qrcode_data[3][8:]
    token = AuthorizationService.login(name, surname, patronymic,password)

    if token:
        return current_app.response_class(
            response=json.dumps({"msg": "Successfully logged in", "token": token}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'An error occurred during login'}),
            status=500,
            mimetype='application/json'
        )

@auth.route('/refresh',methods=['POST'])
def refresh() -> Response:
    data = request.json
    name = data.get("name", None)
    surname = data.get("surname", None)
    patronymic = data.get("patronymic", None)
    token = AuthorizationService.refresh(name,surname,patronymic)
    if token:
        return current_app.response_class(
            response=json.dumps({"msg": "Обновленная сессия", "token": token}),
            status=200,
            mimetype='application/json'
        )
    else:
        return current_app.response_class(
            response=json.dumps({'error': 'Ошибка при обновлении'}),
            status=500,
            mimetype='application/json'
        )

