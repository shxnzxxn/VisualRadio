# Presentation Layer(표현 계층)
# 웹 페이지, API 엔드포인트 등을 담당하는 계층입니다.
# 주로 Flask의 @app.route() 데코레이터를 이용하여 구현합니다.


from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import json
import os
import services
from models import db;

app = Flask(__name__)
CORS(app)  # 모든 라우트에 대해 CORS 허용

# DB세팅
# 주의! create database radioDB; 먼저 
app.config.from_pyfile('config.py')
db.init_app(app)
with app.app_context():
    db.create_all()  # 테이블이 자동으로 생성되는 명령



@app.route('/')
def index():
    return 'Hello!'


############################################## 수집기 요청 ##################

# 가정 : 컨텐츠화하는 포맷은 "멘트" 하나뿐이다.

# 수집기의 요청 목록
# 1. wav를 저장하는 요청
# 2. 저장된 wav를 처리하는 요청 

# ▼ 볼 필요 X
# # 수집기 요청 1 : 저장
# # json : {'radio_name', 'radio_date', 'wav': - }
# @app.route('/save', methods=['POST'])
# def request_save():
#     global radio_url
#     # 넘어온 json 데이터 처리
#     json = request.get_json
#     r_name = json.get('radio_name')
#     r_date = json.get('radio_date')
#     wav = request.json.get('wav');
#     global_setting(r_name, r_date)
#     # 서비스 호출 & 응답결과 반환
#     try:
#         # 데이터 저장
#         user = services.save_wav(wav, radio_url)
#         return jsonify({'message': 'wav를 성공적으로 저장'}), 200
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400


# 수집기 요청 2 : 처리 
@app.route('/start', methods=['POST'])
def start(wav):
    # 넘어온 json 데이터 처리
    json_data = request.json  # key = radio_name, radio_date
    radio_name = json_data[0]
    date = json_data[1]


    # TODO: 이미 처리한 회차인지 체크하기
    # - DB에서 완료여부 확인
    # - ▼ 미처리 회차라면 쭉 진행

    # 서비스 로직 수행
    try:
        # 분할
        services.split(radio_name, date)

        # stt
        services.stt(radio_name, date)

        # txt 컨텐츠 제작
        services.make_txt(radio_name, date)

        return jsonify({'message': '컨텐츠화 완료'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    


############################################## 프론트 요청 ##############################################

# 전체 라디오 프로그램 정보 요청 ㅇ
@app.route('/all')
def get_all():
    all = services.get_all_radio_programs()
    return jsonify(all)

# 라디오 프로그램 이름, 날짜 요청 ㅇ (위 메서드 대신 있는 임시 요청)
@app.route('/program_info', methods=['GET'])
def get_program_info():
    # 임시로 박아두자 (sub2 페이지 하나니까)
    program_info = {
        'radio_name': 'brunchcafe',
        'date': '23/02/26'
    }
    return jsonify(program_info)


# 지정된 회차의 스크립트 요청 ㅇ
@app.route('/<string:radio_name>/<string:date>/script', methods=['GET'])
def get_script(radio_name, date):
    json_data = read_json_file(storage_path(radio_name, date) + '\\result\\script.json')
    return jsonify(json_data)


# 지정된 회차의 섹션 정보 리턴 ㅇ
@app.route('/<string:radio_name>/<string:date>/section', methods=['GET'])
def get_sections(radio_name, date):
    json_data = read_json_file(storage_path(radio_name, date) + '\\result\\section_time.json')
    return jsonify(json_data)


# 지정된 회차의 이미지들 리턴 ㅇ
@app.route('/<string:radio_name>/<string:date>/images', methods=['GET'])
def get_images(radio_name, date):
    file_path = storage_path(radio_name, date) + '\\result\\images.json'
    data = read_json_file(file_path)
    return jsonify(data)


# 지정된 회차의 음성 데이터 리턴 ㅇ
@app.route('/<string:radio_name>/<string:date>/wave', methods=['GET'])
def get_wave(radio_name, date):
    wav = open(storage_path(radio_name, date) + '\\raw.wav', 'rb')
    response = send_file(wav, mimetype="audio/wav", as_attachment=False)
    return response


# TODO: 지정된 회차의 전체 text
@app.route('/<string:radio_name>/<string:date>/txt', methods=['GET'])
def get_txt(radio_name, date):
    # time, text 키를 가진 json데이터를, text만 있는 문자열로 바꾼다.
    script_path = storage_path(radio_name, date) + '\\result\\script.json'
    txt = ''
    return jsonify(txt)


# 광고 컨텐츠
@app.route('/ad', methods=['GET'])
def get_ad():
    # (프로토타입) 고정된 광고 컨텐츠 리턴
    return open('./VisualRadio/templates/ad.html', encoding='utf-8')


###################################################################################

def storage_path(radio_name, radio_date):
    return os.getcwd() + '\\VisualRadio\\radio_storage\\' + radio_name + '\\' + radio_date

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


########################



if __name__ == '__main__':
    app.run()