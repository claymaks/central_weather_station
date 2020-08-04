import flask
import requests
import json
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

account_sid = 'AC580efece0695b543dde0bdb4242cf6cf'
auth_token = '25a9a5c44fc36bc1b7bf1459973f3af7'
client = Client(account_sid, auth_token)

weather_api_key = "f58b1008dd338eed6c6475e77e69fb48"
base_url = "http://api.openweathermap.org/data/2.5/onecall?"
lat = 42.277650
lon = -83.731970
exclude = "minutely,hourly,daily"

complete_url = base_url + f"lat={lat}&lon={lon}&exclude={exclude}&appid={weather_api_key}"

app = flask.Flask(__name__)

@app.route("/sms/update", methods=['GET', 'POST'])
def sms_update():
    resp = MessagingResponse()
    
    recv = requests.get(complete_url).json()
    current = recv["current"]
    temp_k = current["temp"]
    temp_f = int(((temp_k - 273.15) * 9/5 + 32) * 10) / 10
    
    resp.message("The temperature in Ann Arbor is " + str(temp_f) + " degrees F")   
    
    return str(resp)

if __name__ == "__main__":
    app.run()
