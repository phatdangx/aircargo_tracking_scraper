# Get cargo info by tracking number

Used to get the package information from user input

**URL** : `/get_info_by_tracking/<tracking_number>`

**Method** : `GET`

**Auth required** : NO

**Sample**
GET /get_info_by_tracking/131-57483344
```json
{
    "arrival_date": "27-Jul-2021 18:06:41",
    "arrival_flight_number": "QF7586",
    "departure_date": "25-Jul-2021 17:30:27",
    "departure_flight_number": "QF7586",
    "destination": "SYD",
    "number_of_package": "3",
    "origin": "ORD",
    "tracking_number": "081-56878360",
    "weight": "6300.0"
}
```