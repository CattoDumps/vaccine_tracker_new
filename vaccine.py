import subprocess
from datetime import datetime, timedelta
import time
import schedule
import requests
import re

areacodes = []
pincodes = [
    "416520",
    "412115",
    "411004",
    "411007",
    "411001",
    "411057",
    "411030",
    "411058",
    "411057",
    "411006",
    "411011",
    "411028",
    "411017",
    "411026",
    "411027",
    "411018",
    "411044",
]

def check_vaccine_availability():
    try:
        for areacode in areacodes:
            query_cowin(areacode, False)
        for pin in pincodes:
            query_cowin(pin, True)
    except:
        print("Something went wrong. But I am still alive.")

def query_cowin(code, is_pincode):
    print("Checking vaccine for {}".format(code))
    date_to_check = (datetime.today() + timedelta(days=1)).strftime("%d-%m-%Y")
    query_url = "api/v2/appointment/sessions/public/calendarByDistrict?district_id"
    if is_pincode:
        query_url = "api/v2/appointment/sessions/public/calendarByPin?pincode"
    query_url = "https://www.cowin.gov.in/{}={}&date={}".format(
        query_url, code, date_to_check
    )
    print(query_url)
    response = requests.get(query_url)
    vaccine_center_list = response.json()
    check_availability(code, vaccine_center_list)

def check_availability(code, vaccine_center_list):
    for center in vaccine_center_list["centers"]:
        if "sessions" in center:
            for session in center["sessions"]:
                for fee in center["vaccine_fees"]:
                    if session["available_capacity_dose1"] > 10 and session["min_age_limit"] < 45:
                        print(
                            "{} Yeppi vaccine available :). Search code: {}, {}, {}, {}, {}".format(
                                datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                                code,
                                session["available_capacity_dose1"],
                                session["vaccine"],
                                center["district_name"],
                                fee["fee"],
                                session["date"],
                                center["name"],
                                center["address"],
                            )
                        )
                        msg = f"Pincode: {code}\nDistrict: {center['district_name']}\n\nDose 1 Available Capacity: {session['available_capacity_dose1']}\nVaccine: {session['vaccine']}\n\nCenter Name: {center['name']}\n\nDate: {session['date']}\nFees: ₹{fee['fee']}"
                        bashCmd = ["telegram-send", msg]
                        process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
                        return
    print("No vaccine yet :(")

# check_vaccine_availability()
schedule.every(5).seconds.do(check_vaccine_availability)
print("Vaccine monitoring started.")
while True:
    schedule.run_pending()
    time.sleep(5)
