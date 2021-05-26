import subprocess
from datetime import datetime, timedelta
import time
import schedule
import requests
import re

# T0 get the area code:
# 1) Get the state code under https://cdn-api.co-vin.in/api/v2/admin/location/states
# 2) Get the area code from https://cdn-api.co-vin.in/api/v2/admin/location/districts/<state code>
# '265' = Bangalore Urban
# '294' = BBMP
areacodes = []
pincodes = [
    "416520",
    "412115",
    "411004",
    "411040",
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
        print("Something went wrok. But I am still alive.")


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
                if session["available_capacity"] > 0 and session["min_age_limit"] < 45:
                    print(
                        "{} Yeppi vaccine available :). Search code: {}, {}, {}, {}, {}".format(
                            datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                            code,
                            session["available_capacity_dose2"],
                            session["vaccine"],
                            session["fee"],
                            session["date"],
                            center["name"],
                            center["address"],
                        )
                    )
                    msg = f"Pincode: {code}\nDose 2 Available Capacity: {session['available_capacity_dose2']}\nVaccine: {session['vaccine']}\nCenter Name: {center['name']}\nFee: Rs.{['fee']}\nDate: {['date']}"
                    bashCmd = ["telegram-send", msg]
                    process = subprocess.Popen(bashCmd, stdout=subprocess.PIPE)
                    return
    print("No vaccine yet :(")


# check_vaccine_availability()
schedule.every(5).seconds.do(check_vaccine_availability)
print("Vaccine monitoring started.")
while True:
    schedule.run_pending()
    time.sleep(1)
