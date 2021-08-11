import requests
from bs4 import BeautifulSoup
import logging
import json
import time

logger = logging.getLogger()

def get_japan_airline(tracking_number):
    url = "https://www.cargoweb.jal.co.jp/JalCargoWeb/en/intlTracingResult.do"
    data = {
        "searchType": "00", 
        "awbNoPrefix1": "131", 
        "awbNoSuffix1": tracking_number[4:], 
        "houseNo": ""
    }
    page = requests.post(url=url, data=data)
    soup = BeautifulSoup(page.text, 'html.parser')
    # Get origin, dest, number_of_package, weight
    detail_div = soup.find("div", class_="details clearfix")
    if detail_div:
        origin = detail_div.contents[1].contents[1].get_text()
        dest = detail_div.contents[3].contents[1].get_text()
        number_of_package = detail_div.contents[5].contents[1].get_text()
        weight = detail_div.contents[7].contents[1].get_text().split(" ")[0]
        
        # Get fligt_num, departure_date, arrive_date
        flight_num = soup.find("td", class_="bds").get_text()
        tbody_content = soup.find("table", class_="tbl").tbody.contents
        dept_date = tbody_content[5].contents[11].get_text()
        arr_date = tbody_content[7].contents[7].get_text()
        resp = {
            "tracking_number": tracking_number,
            "origin": origin,
            "destination": dest,
            "flight_number": flight_num,
            "departure_date": dept_date,
            "arrive_date": arr_date,
            "number_of_package": number_of_package,
            "weight": weight
        }
    else:
        resp = {}
    return resp


def get_cx_info(tracking_number):
    url = "https://www.cathaypacificcargo.com/ManageYourShipment/TrackYourShipment/tabid/108/SingleAWBNo/{}-/language/en-US/Default.aspx".format(tracking_number)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    info_tag = soup.find(id="dnn_ctr779_ViewTnT_ctl00_objFreightStatus")
    resp = {}
    if info_tag:
        data = json.loads(info_tag["value"])
        resp = {
            "tracking_number": tracking_number,
            "origin": data["Origin"],
            "destination": data["Destination"],
            "number_of_package": data["QDPieces"],
            "weight": data["QDWeight"]
        }
        shipment_history = []
        for stage in data["FreightStatusDetails"]:
            if stage["StatusCode"] == "BKD":
                shipment_history.append(
                    {
                        "from": stage["MDPort1"],
                        "to": stage["MDPort2"],
                        "flight_number": stage["MDCarrierCode"] + stage["MDFlightNum"],
                        "departure_date": time.strftime('%d %b %Y  %H:%M:%S', time.gmtime(stage["DTTime"]["Seconds"])),
                        "arrive_date": time.strftime('%d %b %Y  %H:%M:%S', time.gmtime(stage["ATTime"]["Seconds"]))
                    }
                )
        resp["shipment_history"] = shipment_history
    return resp


def get_ek_info(tracking_number):
    r = requests.get("https://www.skycargo.com/shipping-services/track-shipments?type=AWB&id=176-28979020")
    cookies = r.cookies.get_dict()
    token = cookies.get("__RequestVerificationToken")
    url = "https://www.skycargo.com/eksc/Surface/TrackShipment/TrackShipmentResult?Length=13"
    data = {
        "__RequestVerificationToken": token,
        "search-opt":"AWB",
        "awbpre":176,
        "docNumber":28979020,
        "pageid":19386,
        "TrackShip": False
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    page = requests.post(
        url=url,
        data=data,
        headers=headers,
        cookies=cookies
    )
    return page.text
    #soup = BeautifulSoup(page.text, 'html.parser')


def get_qr_info(tracking_number):
    url = "https://freight.qantas.com/tracking/journey/{}".format(tracking_number)
    r = requests.get(url=url)
    print(1111)
    resp = {}
    if r.status_code == 200:
        data = r.json()
        resp = {
            "tracking_number": tracking_number,
            "origin": data["trackingShipment"]["originStationCode"],
            "destination": data["trackingShipment"]["destinationStationCode"],
            "departure_flight_number": data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["carrierCode"] + 
                data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["flightNumber"],
            "departure_date": data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["eventDateTime"],
            "arrival_date": data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["eventDateTime"],
            "arrival_flight_number": data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["carrierCode"] + 
                data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["flightNumber"],
            "number_of_package": data["trackingShipment"]["shipmentCargo"]["pieces"],
            "weight": data["trackingShipment"]["shipmentCargo"]["weight"]
        }
    return resp