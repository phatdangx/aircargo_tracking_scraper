# Get cargo info by tracking number

Used to get the package information from user input

**URL** : `/get_info_by_tracking/<tracking_number>`

**Method** : `GET`

**Auth required** : NO

**Sample**
GET /get_info_by_tracking/131-57483344
```json
{
    "tracking_number": "131-57483344",
    "weight": "125.0",
    "origin": "NRT",
    "destination": "MEL",
    "number_of_package": "1",
    "shipment_history": [
        {
            "from": "NRT",
            "to": "MEL",
            "flight_number": "JL773",
            "arrive_date": "19JUL",
            "departure_date": "19JUL",
        }
    ]
}
```