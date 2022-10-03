#!/usr/bin/python3

import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, session, render_template, flash
from requests.auth import HTTPBasicAuth
from flask import json
from flask import jsonify

from forms import PredictForm
import requests
# import json
# from start_transaction_request_builder import StartTransactionRequestBuilder
# from flask import json
from flask import jsonify
from flask import Request
from flask import Response
import urllib3
# import json
import xmltodict
import pprint
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY=os.environ.get('SECRET_KEY', 'development key')
))

# strings = {
#     "CheckingStatus": ["no_checking", "less_0", "0_to_200", "greater_200"],
#     "CreditHistory": ["outstanding_credit", "prior_payments_delayed", "credits_paid_to_date", "all_credits_paid_back", "no_credits"],
#     "EmploymentDuration": ["unemployed", "less_1", "1_to_4", "4_to_7", "greater_7"],
#     "ExistingSavings": ["unknown", "less_100", "100_to_500", "500_to_1000", "greater_1000"],
#     "ForeignWorker": ["yes", "no"],
#     "Housing": ["own", "free", "rent"],
#     "InstallmentPlans": ["none", "stores", "bank"],
#     "Job": ["skilled", "management_self-employed", "unemployed", "unskilled"],
#     "OwnsProperty": ["car_other", "savings_insurance", "unknown", "real_estate"],
#     "Sex": ["female", "male"],
#     "Telephone": ["yes", "none"],
#     "LoanPurpose": ["repairs", "appliances", "car_new", "furniture", "car_used", "business", "radio_tv", "education", "vacation", "other", "retraining"],
#     "OthersOnLoan": ["none", "co-applicant", "guarantor"]
# }

# # min, max, default value
# floats = {
#     "InstallmentPercent": [1, 10, 3],
#     "LoanAmount": [200, 750000, 3500]
# }

# # min, max, default value
# ints = {
#     "Age": [18, 80, 35],
#     "Dependents": [0, 10, 1],
#     "CurrentResidenceDuration": [1, 10, 3],
#     "ExistingCreditsCount": [1, 7, 1],
#     "LoanDuration": [1, 72, 24]
# }

# labels = ["No Risk", "Risk"]


# def generate_input_lines():
#     result = f'<table>'

#     counter = 0
#     for k in floats.keys():
#         minn, maxx, vall = floats[k]
#         if (counter % 2 == 0):
#             result += f'<tr>'
#         result += f'<td>{k}'
#         result += f'<input type="number" class="form-control" min="{minn}" max="{maxx}" step="1" name="{k}" id="{k}" value="{vall}" required (this.value)">'
#         result += f'</td>'
#         if (counter % 2 == 1):
#             result += f'</tr>'
#         counter = counter + 1

#     counter = 0
#     for k in ints.keys():
#         minn, maxx, vall = ints[k]
#         if (counter % 2 == 0):
#             result += f'<tr>'
#         result += f'<td>{k}'
#         result += f'<input type="number" class="form-control" min="{minn}" max="{maxx}" step="1" name="{k}" id="{k}" value="{vall}" required (this.value)">'
#         result += f'</td>'
#         if (counter % 2 == 1):
#             result += f'</tr>'
#         counter = counter + 1

#     counter = 0
#     for k in strings.keys():
#         if (counter % 2 == 0):
#             result += f'<tr>'
#         result += f'<td>{k}'
#         result += f'<select class="form-control" name="{k}">'
#         for value in strings[k]:
#             result += f'<option value="{value}" selected>{value}</option>'
#         result += f'</select>'
#         result += f'</td>'
#         if (counter % 2 == 1):
#             result += f'</tr>'
#         counter = counter + 1

#     result += f'</table>'

#     return result


# app.jinja_env.globals.update(generate_input_lines=generate_input_lines)


def get_token():
    auth_token = os.environ.get('AUTH_TOKEN')
    api_token = os.environ.get("API_TOKEN")
    token_request_url = os.environ.get("TOKEN_REQUEST_URL")

    if (auth_token):
        # All three are set. bad bad!
        if (api_token and auth_token):
            raise EnvironmentError('[ENV VARIABLES] please set either "AUTH_TOKEN" or "API_TOKEN". Not both.')
        # Only TOKEN is set. good.
        else:
            return auth_token
    else:
        # Nothing is set. bad!
        if not (api_token and token_request_url):
            raise EnvironmentError('[ENV VARIABLES] Please set "API_TOKEN" as "AUTH_TOKEN" is not set.')
        # Only USERNAME, PASSWORD are set. good.
        else:
            token_response = requests.post(token_request_url, data={"apikey": api_token, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
            if token_response.status_code == 200:
                return token_response.json()["access_token"]
            else:
                raise Exception(f"Authentication returned {token_response.status_code}: {token_response.text}")


class riskForm():
    @app.route('/', methods=('GET', 'POST'))
    def startApp():
        form = PredictForm()
        return render_template('index.html', form=form)

    @app.route('/predict', methods=['GET', 'POST'])
    def predict():

        # if request.method == 'POST':
        #     ID = 999

        #     session['ID'] = ID
        #     data = {}

        #     for k, v in request.form.items():
        #         data[k] = v
        #         session[k] = v

        scoring_href = os.environ.get('MODEL_URL')

        if not (scoring_href):
            raise EnvironmentError('[ENV VARIABLES] Please set "URL".')

        form = PredictForm()
        if form.submit():
        ############## start user input data code form ###################

            if(form.bmi.data == None): 
                python_object = []
            else:
                python_object = [form.age.data, form.sex.data, float(form.bmi.data),
                form.children.data, form.smoker.data, form.region.data]
            #Transform python objects to  Json

            userInput = []
            userInput.append(python_object)
        ################ End Code #########################

        ############## start parse XML SOAP and Extract Data values with input check valid #################
            xml = '''
            <?xml version="1.0" encoding="UTF-8"?>
            <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
            <SOAP-ENV:Body><SOAP-CHK:Success xmlns:SOAP-CHK = "http://soaptest1/soaptest/" xmlns="urn:candle-soap:attributes"><TABLE name="O4SRV.TSITSTSH">
            <OBJECT>Status_History</OBJECT>
            <DATA>
                <ROW>
                    <row>55</row>
                    <row>male</row>
                    <row>72.45</row>
                    <row>2</row>
                    <row>no</row>
                    <row>cairo</row>
                </ROW>
            </DATA>
            </TABLE>
            </SOAP-CHK:Success></SOAP-ENV:Body></SOAP-ENV:Envelope>
            '''

            soup = BeautifulSoup(xml, 'xml')
            userInput2 = []
            Terms = soup.select('ROW > row')
            # userInput2 = []
            for i in Terms:
                userInput2.append(i.text)
            print("data from xml: ", userInput2)
            age = int(userInput2[0])
            sex = str(userInput2[1])
            bmi = float(userInput2[2])
            children = int(userInput2[3])
            smoker = str(userInput2[4])
            region = str(userInput2[5])
            finall_userInput = [[age, sex, bmi, children, smoker, region]]
    ################ End Code ####################################################


                # NOTE: manually define and pass the array(s) of values to be scored in the next line
            payload_scoring = {"input_data": [{"fields": ["age", "sex", "bmi",
                "children", "smoker", "region"], "values": userInput }]}

            print("Payload is: ")
            print(payload_scoring)
            header_online = {
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + get_token()
            }
            response_scoring = requests.post(
                scoring_href,
                verify=True,
                json=payload_scoring,
                headers=header_online)

            output = json.loads(response_scoring.text)
            print(output)
            for key in output:
                ab = output[key]
            

            for key in ab[0]:
                bc = ab[0][key]
            
            roundedCharge = round(bc[0][0],2)
            # print("amr belasy")
            form.abc = roundedCharge # this returns the response back to the front page
            form.jsonf = output

            print(xmltodict.unparse(output, pretty=True))
            form.xml = xmltodict.unparse(output, pretty=True)

            return render_template('index.html', form=form)

        else:
            return render_template('index.html', form=form)


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
port = os.environ.get('PORT', '5000')
host = os.environ.get('HOST', '0.0.0.0')
if __name__ == "__main__":
    app.run(host=host, port=int(port))

