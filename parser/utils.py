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
            "departure_flight_number": flight_num,
            "departure_date": dept_date,
            "arrival_date": arr_date,
            "arrival_flight_number": flight_num,
            "number_of_package": number_of_package,
            "weight": str(weight)
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
            "weight": str(data["QDWeight"])
        }
        bkd_stage = []
        for stage in data["FreightStatusDetails"]:
            if stage["StatusCode"] == "BKD":
                bkd_stage.append(stage)
        departure_stage = bkd_stage[0]
        arrival_stage = bkd_stage[-1]
        resp.update({
            "departure_flight_number": departure_stage["MDCarrierCode"] + departure_stage["MDFlightNum"],
            "departure_date": time.strftime('%d-%b-%Y %H:%M:%S', time.gmtime(departure_stage["DTTime"]["Seconds"])).upper(),
            "arrival_date": time.strftime('%d-%b-%Y %H:%M:%S', time.gmtime(arrival_stage["ATTime"]["Seconds"])).upper(),
            "arrival_flight_number": arrival_stage["MDCarrierCode"] + arrival_stage["MDFlightNum"]
        })
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
    resp = {}
    if r.status_code == 200:
        data = r.json()
        resp = {
            "tracking_number": tracking_number,
            "origin": data["trackingShipment"]["originStationCode"],
            "destination": data["trackingShipment"]["destinationStationCode"],
            "departure_flight_number": data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["carrierCode"] + 
                data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["flightNumber"],
            "departure_date": data["inTransitStage"]["trackingStageCards"][0]["latestTrackingEvent"]["eventDateTime"].upper(),
            "arrival_date": data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["eventDateTime"].upper(),
            "arrival_flight_number": data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["carrierCode"] + 
                data["preDeliveryStage"]["trackingStageCards"][0]["latestTrackingEvent"]["flightNumber"],
            "number_of_package": data["trackingShipment"]["shipmentCargo"]["pieces"],
            "weight": data["trackingShipment"]["shipmentCargo"]["weight"]
        }
    return resp


def get_nz_info(tracking_number):
    url = "https://www.airnewzealandcargo.com/feeds/cargo-status?awb={}".format(tracking_number)
    r = requests.get(url=url)
    resp = {}
    if r.status_code == 200:
        data = r.json()
        resp = {
            "tracking_number": tracking_number,
            "weight": data["details"]["weight"],
            "number_of_package": data["details"]["pieces"]
        }
        if len(data["segments"]) == 1:
            resp.update(
                {
                    "origin": data["segments"][0]["origin"],
                    "destination": data["segments"][0]["destination"],
                    "arrival_date": "{} {}:00".format(data["segments"][0]["eta"][:11].replace(" ", "-").upper(), data["segments"][0]["eta"][11:] if len(data["segments"][0]["eta"]) > 12 else "00:00"),
                    "departure_date": "{} {}:00".format(data["segments"][0]["etd"][:11].replace(" ", "-").upper(), data["segments"][0]["etd"][11:] if len(data["segments"][0]["etd"]) > 12 else "00:00"),
                    "arrival_flight_number": data["segments"][0]["flight"],
                    "departure_flight_number": data["segments"][0]["flight"],
                }
            )
        else:
            depart_stage = data["segments"][0]
            arr_stage = data["segments"][-1]
            resp.update(
                {
                    "origin": depart_stage["origin"],
                    "destination": arr_stage["destination"],
                    "arrival_date": "{} {}:00".format(arr_stage["eta"][:11].replace(" ", "-").upper(), arr_stage["eta"][11:] if len(arr_stage) > 12 else "00:00"),
                    "departure_date": "{} {}:00".format(depart_stage["etd"][:11].replace(" ", "-").upper(), depart_stage["etd"][11:] if len(depart_stage) > 12 else "00:00"),
                    "arrival_flight_number": arr_stage["flight"],
                    "departure_flight_number": depart_stage["flight"],
                }
            )
        return resp
    return resp


def get_ua_info(tracking_number):
    url = "https://www.unitedcargo.com/TrackingServlet?BranchCode=&CompanyName=Test&DocumentNumbers={}".format(tracking_number)
    r = requests.get(url=url)
    if r.status_code == 200:
        data= r.json()[0]
        resp = {}
        if "MasterConsignment" in data:
            resp.update({
                "origin": data["MasterConsignment"]["Origin"],
                "destination": data["MasterConsignment"]["Destination"],
                "weight": str(data["MasterConsignment"]["Weight"]),
                "number_of_package": data["MasterConsignment"]["Pieces"]
            })
            if "ReportedStatusList" in data and len(data["ReportedStatusList"]) > 0:
                for item in data["ReportedStatusList"]:
                    if item["Station"] == resp["destination"] and item["StatusCode"] == "ARR":
                        resp.update({
                            "arrival_date": item["StatusDateTime"],
                            "arrival_flight_number": item["FlightSuffix"] + item["FlightNumber"]
                        })
                    elif item["Station"] == resp["origin"] and item["StatusCode"] == "DEP":
                        resp.update({
                            "departure_date": item["StatusDateTime"],
                            "departure_flight_number": item["FlightSuffix"] + item["FlightNumber"]
                        })
    return resp

def get_mh_info(tracking_number):
    url = "https://www.maskargo.com/online_awb_info/index.php"
    r = requests.post(
        url=url,
        data={
            "code": "232",
            "awb": tracking_number[4:]
        }
    )
    resp = {}
    if r.status_code == 200:
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            awb_td = soup.find_all("td", class_="awb-no")[0]
            origin_td= awb_td.next_sibling
            dest_td = origin_td.next_sibling
            package_num_td = dest_td.next_sibling
            weight_td = package_num_td.next_sibling
            resp = {
                "tracking_number": tracking_number,
                "origin": origin_td.text,
                "destination": dest_td.text,
                "number_of_package": package_num_td.text,
                "weight": weight_td.text
            }
            detail_table = soup.find_all("table")[1]
            tr_list = detail_table.find_all("tr")
            flight_data = []
            for tr in tr_list[2:]:
                tds = tr.find_all("td")
                flight_data.append({
                    "code": tds[0].text,
                    "status": tds[1].text,
                    "from": tds[2].text,
                    "to": tds[3].text,
                    "carrier": tds[4].text,
                    "pieces": tds[5].text,
                    "weight": tds[6].text,
                    "sdt": tds[7].text,
                    "sat": tds[8].text
                })
            for data in flight_data:
                if data["status"] == "FLIGHT DEPARTED" and data["from"] == resp["origin"]:
                    carrier_flt = data["carrier"].split("/")
                    flt_num = carrier_flt[0]
                    dep_date = carrier_flt[1]
                    resp.update({
                        "departure_date": "{} {} 20{} 00:00:00".format(dep_date[:2],dep_date[2:5],dep_date[5:]),
                        "departure_flight_number": flt_num
                    })
                if data["status"] == "FLIGHT DEPARTED" and data["to"] == resp["destination"]:
                    carrier_flt = data["carrier"].split("/")
                    flt_num = carrier_flt[0]
                    dep_date = carrier_flt[1]
                    resp.update({
                        "arrival_date": "{} {} 20{} 00:00:00".format(dep_date[:2],dep_date[2:5],dep_date[5:]),
                        "arrival_flight_number": flt_num
                    })
            return resp
        except Exception as e:
            print(str(e))
            return resp
    return resp

def get_ups_info(tracking_number):
    url = "https://aircargo.ups.com/en-US/Tracking?awbPrefix=406&awbNumber={}".format(tracking_number[4:])
    r = requests.get(url)
    resp = {}
    if r.status_code == 200:
        try:
            soup = BeautifulSoup(r.text, 'html.parser')
            track_header = soup.find("div", id="TrackHeader")
            track_header_left = track_header.find("div", class_="text-left").find_all("strong")
            track_header_right = track_header.find("div", class_="text-right").find("p").text.split(" ")
            resp = {
                "tracking_number": tracking_number,
                "origin": track_header_left[1].text.replace(" ",""),
                "destination": track_header_left[2].text.replace(" ",""),
                "number_of_package": track_header_right[1],
                "weight": ""
            }
            flight_data =[]
            table = soup.find("div", id="tabular").find("table")
            tr_list = table.find_all("tr")
            for tr in tr_list[1:]:
                tds = tr.find_all("td")
                flight_data.append(
                    {
                        "status": tds[0].text,
                        "station": tds[1].text,
                        "flight": tds[2].text,
                        "event_time": tds[4].text
                    }
                )
            for data in flight_data:
                if data["status"] == "Departed" and data["station"] == resp["origin"]:
                    resp.update({
                        "departure_flight_number": data["flight"].split(" ")[0],
                        "departure_date": data["event_time"]
                    })
                if data["status"] == "Arrived" and data["station"] == resp["destination"]:
                    resp.update({
                        "arrival_flight_number": data["flight"].split(" ")[0],
                        "arrival_date": data["event_time"]
                    })
        except Exception as e:
            return resp
    return resp