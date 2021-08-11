from flask import Flask, make_response, jsonify
from parser.utils import *
app = Flask(__name__)

@app.route('/')
def health_check():
	return 'Airline API...Working'

@app.route('/get_info_by_tracking/<tracking_number>', methods=["GET"])
def get_tracking_url(tracking_number):
    resp = {}
    awb_code = tracking_number[:3]
    if awb_code == "131":
        resp = get_japan_airline(tracking_number)
    elif awb_code == "160":
        resp = get_cx_info(tracking_number)
    elif awb_code == "176":
        resp = get_ek_info(tracking_number)
    return make_response(jsonify(resp))

if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True)