from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from parser.utils import *
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:root@localhost:3306/flask'
db = SQLAlchemy(app)

#Model
class Airline(db.Model):
    __tablename__ = "airline"
    id = db.Column(db.Integer, primary_key=True)
    alpha2_code = db.Column(db.String(2))
    airline_label_name = db.Column(db.String(45))
    alpha3_code = db.Column(db.String(3))
    awb_code = db.Column(db.String(3))
    headquarter_country_id = db.Column(db.Integer)
    tail_logo_url = db.Column(db.String(2048))
    tracking_url = db.Column(db.String(200))
    regex_pattern = db.Column(db.String(150))
    is_neutral_mawb_flag = db.Column(db.String(100))
    headquarter_country = db.Column(db.String(2))
    full_plan_image = db.Column(db.String(100))
    organisation_id = db.Column(db.Integer)
    compliance_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Airline %r>' % self.airline_label_name

class AirlineSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Airline
        sqla_session = db.session
    id = fields.Number(dump_only=True)
    alpha2_code = fields.String()
    airline_label_name = fields.String()
    alpha3_code = fields.String()
    awb_code = fields.String()
    headquarter_country_id = fields.Number()
    tail_logo_url = fields.String()
    tracking_url = fields.String()
    regex_pattern = fields.String()
    is_neutral_mawb_flag = fields.String()
    headquarter_country = fields.String()
    full_plan_image = fields.String()
    organisation_id = fields.Number()
    compliance_id = fields.Number()


@app.route('/')
def health_check():
	return 'Airline API...Working'

@app.route('/airline')
def get_airline():
    all_airlines = Airline.query.all()
    airline_schema = AirlineSchema(many=True)
    airlines = airline_schema.dump(all_airlines)
    return make_response(jsonify(airlines))

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