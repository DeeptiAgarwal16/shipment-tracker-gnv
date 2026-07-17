"""
Zoho Books Shipment Tracking Auto-Sync
Merged: track_shipments + zoho_tracking_sync
Python 2.7 compatible syntax
"""

import requests
import time
import sys
import os
import re
import json
from datetime import datetime, timedelta

# CONFIG
ZOHO_CLIENT_ID     = "1000.4GV2IR7R5DCC78LYOD09M7QVVYQNEK"
ZOHO_CLIENT_SECRET = "205b0dfa107949703a7767461f8688bee9e4d6cb46"
ZOHO_ORG_ID        = "60003179555"
ZOHO_REFRESH_TOKEN = "1000.0c5d14a108525382b54430f360066d05.92f07893f7a87f293128f49f006a7bd3"

DELHIVERY_API_TOKEN    = "ef7c20d325f594aee3e962f75616688bd885eda6"
DISPATCH_SOLUTIONS_KEY = "dsp_3f82e97c4b7f4b6bb932a1d91e"
DISPATCH_BASE_URL      = "https://dispatchsolutions.in/api/v1/track"

DTDC_LTL_URL       = "https://api.mywebxpress.com/tms/dtdc/ops/Docket/TrackDocket/DTDC"
DTDC_LTL_TOKEN     = "T/wN4rfyi4Sm7AEnKpiTsO7ZqRDsw0AhRk5H9Vo3a3ul+gkgeEnOuJoJ8/rTfwFo"
DTDC_LTL_KEY       = "3a28b4665dd27839b106cdfdca9201"
DTDC_SX_AUTH_URL   = "https://blktracksvc.dtdc.com/dtdc-api/api/dtdc/authenticate"
DTDC_SX_TRACK_URL  = "https://blktracksvc.dtdc.com/dtdc-tracking-api/dtdc-api/rest/JSONCnTrk/getTrackDetails"
DTDC_SX_TRACK_URL2 = "http://dtdcstagingapi.dtdc.com/dtdc-tracking-api/dtdc-api/rest/JSONCnTrk/getTrackDetails"
DTDC_SX_USER       = "GL018_trk_json"
DTDC_SX_PASS       = "chwzf"

BLUEDART_LIC_KEY   = "pkkpkigulku3iv4htmg8vijpuopmhivv"
BLUEDART_LOGIN_ID  = "MAA43911"
BLUEDART_PASSWORD  = "Arun@12345"
BLUEDART_LOGIN_ID2 = "MAA280851"
BLUEDART_LOGIN_ID3 = "MAA510484"

DELAY_BETWEEN = 0.8

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Zoho native status map
# ZOHO_NATIVE_STATUS = {
# "In-Transit": "Shipped",
# "Out For Delivery": "Shipped",
# "Failed Delivery Attempt": "Shipped",
# "Shipped": "Shipped",
# "Customs Clearance": "Shipped",
# "Ready For Pickup": "Shipped",
# "Delayed": "Shipped",

# "Delivered": "Delivered",
# "Delivered to PO": "Delivered",
# "White Glove Delivery": "Delivered",
# "Delivered from PickUp Point": "Delivered",

# "NOT FOUND": "Shipped",
# "ERROR": "Shipped",
# }
# ZOHO_NATIVE_STATUS_LOWER = {k.strip().lower(): v for k, v in ZOHO_NATIVE_STATUS.items() if k}

# DISPATCH_STATUS_MAP = {
#     # Initial pickup/booking
#     "out for pickup": "Ready For Pickup",
#     "data received": "Shipped",
#     "picked up": "Shipped",
#     "consignment booked": "Shipped",
#     "shipment booked": "Shipped",
#     "ready to dispatch": "Shipped",

#     # Transit
#     "in transit": "In-Transit",
#     "trip arrived": "In-Transit",
#     "trip departed": "In-Transit",
#     "vehicle departed": "In-Transit",
#     "shipment received at facility": "In-Transit",
#     "in transit to destination": "In-Transit",
#     "reached destination hub": "In-Transit",
#     "bag added to trip": "In-Transit",
#     "manifested": "In-Transit",
#     "added to bag": "In-Transit",
#     "unlock": "In-Transit",
#     "pending": "In-Transit",

#     # Delayed
#     "vehicle delayed": "Delayed",
#     "vehicle delayed - controllable": "Delayed",
#     "vehicle delayed - non controllable": "Delayed",

#     # Out for delivery
#     "out for delivery": "Out For Delivery",
#     "out for delivery attempt": "Out For Delivery",
#     "dispatched": "Out For Delivery",

#     # Delivered
#     "delivered": "Delivered",
#     "pod audit - delivered": "Delivered",
#     "pod - delivered": "Delivered",
#     "delivered to consignee": "Delivered",
#     "shipment delivered": "Delivered",
#     "code verified delivery": "Delivered",
#     "delivery completed": "Delivered",

#     # Failed delivery
#     "undelivered": "Failed Delivery Attempt",
#     "delivery attempted": "Failed Delivery Attempt",
#     "consignee not available": "Failed Delivery Attempt",
#     "consignee unavailable": "Failed Delivery Attempt",
#     "delivery failed": "Failed Delivery Attempt",
#     "pod audit - incorrect": "Failed Delivery Attempt",
#     "pod audit - unclear": "Failed Delivery Attempt",
#     "pod audit - rejected": "Failed Delivery Attempt",
#     "pod - not delivered": "Failed Delivery Attempt",

#     # Return (best available mapping)
#     "rto": "Failed Delivery Attempt",
#     "return": "Failed Delivery Attempt",
#     "rto initiated": "Failed Delivery Attempt",
#     "return accepted": "Failed Delivery Attempt",
#     "return in transit": "Failed Delivery Attempt",
#     "return delivered": "Failed Delivery Attempt",

#     # No equivalent Zoho status
#     "lost": "Delayed",
#     "damaged": "Delayed",
#     "pod audit - damaged": "Delayed",

#     "NOT FOUND": "Not Found",
#     "ERROR": "Error",
# }
# BD_STATUS = {
#     # Delivered
#     "dl": "Delivered",
#     "dlv": "Delivered",
#     "d": "Delivered",
#     "shipment delivered": "Delivered",
#     "delivered": "Delivered",
#     "delivery done": "Delivered",

#     # Out For Delivery
#     "od": "Out For Delivery",
#     "outdlv": "Out For Delivery",
#     "out for delivery": "Out For Delivery",

#     # In Transit
#     "it": "In-Transit",
#     "intransit": "In-Transit",
#     "in transit": "In-Transit",
#     "in transit. await delivery information": "In-Transit",
#     "pending": "In-Transit",

#     # Shipped
#     "pu": "Shipped",
#     "picked up": "Shipped",
#     "shipment picked up": "Shipped",
#     "bk": "Shipped",
#     "booked": "Shipped",
#     "shipment booked": "Shipped",

#     # Failed Delivery
#     "nd": "Failed Delivery Attempt",
#     "not delivered": "Failed Delivery Attempt",

#     # RTO
#     "rt": "Failed Delivery Attempt",
#     "rto": "Failed Delivery Attempt",
#     "return to origin": "Failed Delivery Attempt",

#     # Customs
#     "cr": "Customs Clearance",

#     "NOT FOUND": "Not Found",
#     "ERROR": "Error",
# }
ZOHO_NATIVE_STATUS = {
"in_transit": "Shipped",
"out_for_delivery": "Shipped",
"delivery_attempted": "Shipped",
"shipped": "Shipped",
"customs_clearance": "Shipped",
"ready_for_pickup": "Shipped",
"delayed": "Shipped",

"delivered": "Delivered",
"delivered_po_box": "Delivered",
"white_glove_delivery": "Delivered",
"pickup_point_delivery": "Delivered",

"NOT FOUND": None,
"ERROR": None,
}
ZOHO_NATIVE_STATUS_LOWER = {k.strip().lower(): v for k, v in ZOHO_NATIVE_STATUS.items() if k}

DISPATCH_STATUS_MAP = {
    # Initial pickup/booking
    "out for pickup":                     "ready_for_pickup",
    "data received":                      "shipped",
    "picked up":                          "shipped",
    "consignment booked":                 "shipped",
    "shipment booked":                    "shipped",
    "ready to dispatch":                  "shipped",

    # Transit
    "in transit":                         "in_transit",
    "trip arrived":                       "in_transit",
    "trip departed":                      "in_transit",
    "vehicle departed":                   "in_transit",
    "shipment received at facility":      "in_transit",
    "in transit to destination":          "in_transit",
    "reached destination hub":            "in_transit",
    "bag added to trip":                  "in_transit",
    "manifested":                         "in_transit",
    "added to bag":                       "in_transit",
    "unlock":                             "in_transit",

    # Delayed
    "vehicle delayed":                    "delayed",
    "vehicle delayed - controllable":     "delayed",
    "vehicle delayed - non controllable": "delayed",

    # Out for delivery
    "out for delivery":                   "out_for_delivery",
    "out for delivery attempt":           "out_for_delivery",
    "dispatched":                         "out_for_delivery",

    # Delivered
    "delivered":                          "delivered",
    "pod audit - delivered":              "delivered",
    "pod - delivered":                    "delivered",
    "delivered to consignee":             "delivered",
    "shipment delivered":                 "delivered",
    "code verified delivery":             "delivered",
    "delivery completed":                 "delivered",

    # Failed delivery
    "undelivered":                        "delivery_attempted",
    "delivery attempted":                 "delivery_attempted",
    "consignee not available":            "delivery_attempted",
    "consignee unavailable":              "delivery_attempted",
    "delivery failed":                    "delivery_attempted",
    "pod audit - incorrect":              "delivery_attempted",
    "pod audit - unclear":                "delivery_attempted",
    "pod audit - rejected":               "delivery_attempted",
    "pod - not delivered":                "delivery_attempted",

    # Return (best available mapping)
    "rto":                                "delivery_attempted",
    "return":                             "delivery_attempted",
    "rto initiated":                      "delivery_attempted",
    "return accepted":                    "delivery_attempted",
    "return in transit":                  "delivery_attempted",
    "return delivered":                   "delivery_attempted",

    # No equivalent Zoho status
    "lost":                               "delayed",
    "damaged":                            "delayed",
    "pod audit - damaged":                "delayed",
}
BD_STATUS = {
    # Delivered
    "dl": "delivered",
    "dlv": "delivered",
    "d": "delivered",
    "shipment delivered": "delivered",
    "delivered": "delivered",
    "delivery done": "delivered",

    # Out For Delivery
    "od": "out_for_delivery",
    "outdlv": "out_for_delivery",
    "out for delivery": "out_for_delivery",

    # In Transit
    "it": "in_transit",
    "intransit": "in_transit",
    "in transit": "in_transit",
    "in transit. await delivery information": "in_transit",

    # Shipped
    "pu": "shipped",
    "picked up": "shipped",
    "shipment picked up": "shipped",
    "bk": "shipped",
    "booked": "shipped",
    "shipment booked": "shipped",

    # Failed Delivery
    "nd": "delivery_attempted",
    "not delivered": "delivery_attempted",

    # RTO
    "rt": "delivery_attempted",
    "rto": "delivery_attempted",
    "return to origin": "delivery_attempted",

    # Customs
    "cr": "customs_clearance",
}
# ZOHO_NATIVE_STATUS = {
#     "Delivered":        "delivered",
#     "In Transit":       "shipped",
#     "Out for Delivery": "shipped",
#     "Picked Up":        "shipped",
#     "Manifested":       "shipped",
#     "Booked":           "shipped",
#     "Undelivered":      "shipped",
#     "RTO":              "shipped",
#     "RTO Delivered":    "delivered",
#     "NOT FOUND":        None,
#     "ERROR":            None,
# }
# DISPATCH_STATUS_MAP = {
#     "out for pickup":                     "Out for Pickup",
#     "data received":                      "Booked",
#     "picked up":                          "Picked Up",
#     "in transit":                         "In Transit",
#     "out for delivery":                   "Out for Delivery",
#     "delivered":                          "Delivered",
#     "undelivered":                        "Undelivered",
#     "rto":                                "RTO",
#     "return":                             "RTO",
#     "lost":                               "Lost",
#     "damaged":                            "Damaged",
#     "pod audit - delivered":              "Delivered",
#     "pod audit - incorrect":              "Undelivered",
#     "pod audit - unclear":                "Undelivered",
#     "pod audit - rejected":               "Undelivered",
#     "pod audit - damaged":                "Damaged",
#     "pod - delivered":                    "Delivered",
#     "pod - not delivered":                "Undelivered",
#     "delivered to consignee":             "Delivered",
#     "shipment delivered":                 "Delivered",
#     "code verified delivery":             "Delivered",
#     "delivery completed":                 "Delivered",
#     "trip arrived":                       "In Transit",
#     "trip departed":                      "In Transit",
#     "vehicle departed":                   "In Transit",
#     "vehicle delayed - controllable":     "In Transit",
#     "vehicle delayed - non controllable": "In Transit",
#     "vehicle delayed":                    "In Transit",
#     "shipment received at facility":      "In Transit",
#     "in transit to destination":          "In Transit",
#     "reached destination hub":            "In Transit",
#     "bag added to trip":                  "In Transit",
#     "manifested":                         "In Transit",
#     "added to bag":                       "In Transit",
#     "consignment booked":                 "Booked",
#     "shipment booked":                    "Booked",
#     "ready to dispatch":                  "Booked",
#     "out for delivery attempt":           "Out for Delivery",
#     "dispatched":                         "Out for Delivery",
#     "delivery attempted":                 "Undelivered",
#     "consignee not available":            "Undelivered",
#     "consignee unavailable":              "Undelivered",
#     "delivery failed":                    "Undelivered",
#     "rto initiated":                      "RTO",
#     "return accepted":                    "RTO",
#     "return in transit":                  "RTO",
#     "return delivered":                   "RTO Delivered",
#     "unlock":                             "In Transit",
# }

# BlueDart status code map
# BD_STATUS = {
#     "dl":  "Delivered",        "dlv": "Delivered",
#     "d":   "Delivered",
#     "shipment delivered":               "Delivered",
#     "delivered":                        "Delivered",
#     "delivery done":                    "Delivered",
#     "od":  "Out for Delivery",  "outdlv": "Out for Delivery",
#     "out for delivery":                 "Out for Delivery",
#     "it":  "In Transit",        "intransit": "In Transit",
#     "in transit":                       "In Transit",
#     "in transit. await delivery information": "In Transit",
#     "pu":  "Picked Up",         "picked up": "Picked Up",
#     "shipment picked up":               "Picked Up",
#     "bk":  "Booked",            "booked": "Booked",
#     "shipment booked":                  "Booked",
#     "nd":  "Undelivered",       "not delivered": "Undelivered",
#     "rt":  "RTO",               "rto": "RTO",
#     "return to origin":                 "RTO",
#     "cr":  "Customs Clearance",
# }


# Token caches
_token_cache    = {"v": None, "expires": 0}
_sx_token       = {"v": None}
_bd_token_cache = {}


# HELPERS

def safe_json(r):
    try:
        return r.json()
    except Exception:
        return None


def clean(s):
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s)).strip()


def fmt_dt(s):
    """ISO datetime to DD-Mon-YYYY HH:MM"""
    s = clean(s)
    if not s or s in ("None", "nan", ""):
        return ""
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})", s)
    if m:
        y, mo, d, h, mi = m.groups()
        return "{}-{}-{} {}:{}".format(d, months[int(mo)], y, h, mi)
    m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m2:
        y, mo, d = m2.groups()
        return "{}-{}-{}".format(d, months[int(mo)], y)
    return s


def fmt_dmy(date_str, time_str=""):
    """DDMMYYYY plus HHMM to DD-Mon-YYYY HH:MM"""
    d = clean(str(date_str))
    t = clean(str(time_str))
    if not d or d in ("None", "nan", ""):
        return ""
    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = re.match(r"^(\d{2})(\d{2})(\d{4})$", d)
    if m:
        dd, mo, yyyy = m.groups()
        base = "{}-{}-{}".format(dd, months[int(mo)], yyyy)
        tc = re.sub(r":", "", t)
        if tc and re.match(r"^\d{4,6}$", tc):
            base += " {}:{}".format(tc[:2], tc[2:4])
        return base
    if re.match(r"^\d{2}/\d{2}/\d{4}$", d):
        p = d.split("/")
        base = "{}-{}-{}".format(p[0], months[int(p[1])], p[2])
        tc = re.sub(r":", "", t)
        if tc and re.match(r"^\d{4,6}$", tc):
            base += " {}:{}".format(tc[:2], tc[2:4])
        return base
    return d


def parse_bd_date(val):
    """Convert BlueDart date formats to DD-Mon-YYYY.
    Handles: 03 April 2026, 03/04/2026, 2026-04-03
    """
    if not val or str(val).strip() in ("", "None", "null"):
        return ""
    val = str(val).strip()
    months_full = {
        "january": "Jan", "february": "Feb", "march": "Mar", "april": "Apr",
        "may": "May", "june": "Jun", "july": "Jul", "august": "Aug",
        "september": "Sep", "october": "Oct", "november": "Nov", "december": "Dec"
    }
    months_short = {
        "jan": "Jan", "feb": "Feb", "mar": "Mar", "apr": "Apr",
        "may": "May", "jun": "Jun", "jul": "Jul", "aug": "Aug",
        "sep": "Sep", "oct": "Oct", "nov": "Nov", "dec": "Dec"
    }
    mon_list = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m = re.match(r"(\d{1,2})\s+(\w+)\s+(\d{4})", val)
    if m:
        d, mo, y = m.groups()
        mo_l = mo.lower()
        mo_s = months_full.get(mo_l) or months_short.get(mo_l[:3]) or mo[:3].title()
        return "{}-{}-{}".format(d.zfill(2), mo_s, y)
    m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})", val)
    if m2:
        y, mo, d = m2.groups()
        return "{}-{}-{}".format(d, mon_list[int(mo)], y)
    m3 = re.match(r"(\d{2})/(\d{2})/(\d{4})", val)
    if m3:
        d, mo, y = m3.groups()
        return "{}-{}-{}".format(d, mon_list[int(mo)], y)
    return val


def make_err(courier, awb, status, remarks):
    return {
        "courier": courier, "awb": awb, "status": status,
        "edd": "", "delivered_date": "", "remarks": remarks
    }


def is_surface_awb(awb):
    return bool(re.match(r"^[A-Za-z]", awb.strip()))


def is_ltl_awb(awb):
    return bool(re.match(r"^11\d{10}$", awb.strip()))


def norm_dispatch_status(raw):
    if not raw:
        return ""
    r = raw.strip().lower()
    if r in DISPATCH_STATUS_MAP:
        return DISPATCH_STATUS_MAP[r]
    for k, v in DISPATCH_STATUS_MAP.items():
        if k in r:
            return v
    return raw.strip().title()


def norm_bd_status(raw):
    if not raw:
        return ""
    return BD_STATUS.get(raw.strip().lower(), raw.strip().title())


# COURIER ROUTING
# Dropdown values:
#   "Aashrey Logistics_Delhivery"   -> Dispatch Solutions (LR/Delhivery)
#   "Aashrey Logistics_Blue Dart"   -> Dispatch Solutions (BlueDart)
#   "Blue Dart"                     -> BlueDart direct API
#   "Aashrey Logistics_DTDC"        -> Dispatch Solutions first, DTDC API fallback
#   "DTDC"                          -> DTDC direct API (surface or LTL by AWB)
#   "Delhivery B2C"                 -> Delhivery direct API

def get_route(carrier):
    c = (carrier or "").strip().lower()

    if c == "courier_ashrey_delhivery":
        return "dispatch_lr"

    if c == "courier_ashrey_bluedart":
        return "bluedart"

    if c == "courier_ashrey_dtdc":
        return "dispatch_dtdc"

    if c == "courier_bluedart":
        return "bluedart"

    if c == "courier_dtdc":
        return "dtdc_own"

    if c == "courier_delhivery b2c":
        return "delhivery"

    return "unknown"


# ZOHO AUTH

def get_access_token(context):
    if _token_cache["v"] and time.time() < _token_cache["expires"] - 60:
        return _token_cache["v"]
    r = requests.post(
        "https://accounts.zoho.in/oauth/v2/token",
        data={
            "refresh_token": ZOHO_REFRESH_TOKEN,
            "client_id":     ZOHO_CLIENT_ID,
            "client_secret": ZOHO_CLIENT_SECRET,
            "grant_type":    "refresh_token",
        },
        timeout=15
    )
    d = r.json()
    if "access_token" not in d:
        context.log.INFO("ERROR getting Zoho access token: {}".format(d))
        return None
    _token_cache["v"]       = d["access_token"]
    _token_cache["expires"] = time.time() + int(d.get("expires_in", 3600))
    return _token_cache["v"]

def auth_headers_shipped(context):
    return {
        "Authorization": "Zoho-oauthtoken {}".format(get_access_token(context)),
        "Content-Type":  "application/json",
    }
def auth_headers_delivered(context):
    return {
        "Authorization": "Zoho-oauthtoken {}".format(get_access_token(context)),
        "Content-Type":  "application/x-www-form-urlencoded",
    }


def zoho_get(context, endpoint, params=None):
    p = {"organization_id": ZOHO_ORG_ID}
    if params:
        p.update(params)
    r = requests.get(
        "https://www.zohoapis.in/books/v3/{}".format(endpoint),
        headers=auth_headers_shipped(context), params=p, timeout=15
    )
    return r.json()


def zoho_post(context, endpoint, body, extra_headers=None):
    headers = auth_headers_shipped(context)
    if extra_headers:
        headers.update(extra_headers)
    r = requests.post(
        "https://www.zohoapis.in/books/v3/{}".format(endpoint),
        headers=headers,
        params={"organization_id": ZOHO_ORG_ID},
        data=json.dumps(body),
        timeout=15
    )
    return r.json()

def zoho_post_delivered(context, endpoint, body, extra_headers=None):
    headers = auth_headers_delivered(context)
    if extra_headers:
        headers.update(extra_headers)
    r = requests.post(
        "https://www.zohoapis.in/books/v3/{}".format(endpoint),
        headers=headers,
        params={"organization_id": ZOHO_ORG_ID},
        # data=json.dumps(body),
        data = body,
        timeout=15
    )
    return r.json()

def zoho_put(context, endpoint, body, extra_params=None):
    params = {"organization_id": ZOHO_ORG_ID}
    if extra_params:
        params.update(extra_params)
    params["JSONString"] = json.dumps(body)
    r = requests.put(
        "https://www.zohoapis.in/books/v3/{}".format(endpoint),
        params=params,
        headers=auth_headers_shipped(context)
    )
    return r.json()


# ZOHO SHIPMENT FETCHING

def get_all_shipments(context):
    shipments = []
    page = 1

    cutoff_date = datetime.strptime("2026-07-01", "%Y-%m-%d").date()

    while True:
        data = zoho_get(context, "shipmentorders", {
            "per_page": 200,
            "page": page,
            "sort_column": "date",
            "sort_order": "D",
            "status": "shipped"
        })

        batch = data.get("shipmentorders") or []

        if not batch:
            context.log.INFO("Page {}: 0 shipments, stopping.".format(page))
            break

        # Keep only shipments on or after 2026-07-01
        filtered_batch = []
        for shipment in batch:
            shipment_date = datetime.strptime(
                shipment["date"], "%Y-%m-%d"
            ).date()

            if shipment_date >= cutoff_date:
                filtered_batch.append(shipment)

        context.log.INFO(
            "Page {}: {} shipment(s) kept".format(page, len(filtered_batch))
        )

        shipments.extend(filtered_batch)

        last_date = datetime.strptime(batch[-1]["date"], "%Y-%m-%d").date()
        if last_date < cutoff_date:
            break

        if not data.get("page_context", {}).get("has_more_page", False):
            break

        page += 1
        time.sleep(0.2)

    return shipments


def get_shipment_detail(context, shipment_id):
    data = zoho_get(context, "shipmentorders/{}".format(shipment_id))
    return data.get("shipmentorder") or {}


def get_cf_value(detail, label):
    for cf in (detail.get("custom_fields") or []):
        if cf.get("label", "").strip().lower() == label.strip().lower():
            return str(cf.get("value") or "").strip()
    return ""

from datetime import datetime

def format_date(del_date):
    formats = [
        "%d-%b-%Y %H:%M:%S",
        "%d-%b-%Y %H:%M",
        "%d-%B-%Y %H:%M:%S",
        "%d-%B-%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%b-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(del_date.strip(), fmt).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass

    raise ValueError("Unsupported date format: {}".format(del_date))
# ZOHO UPDATE

def update_shipment(context, shipment_id, status, edd, del_date, dry_run=True):

    native = ZOHO_NATIVE_STATUS.get(status)
    if not native and status:
        native = ZOHO_NATIVE_STATUS_LOWER.get(status.strip().lower())
    if not native:
        context.log.INFO("SKIP update: status '{}' has no Zoho native mapping".format(status))
        return False

    shipment      = zoho_get(context, "shipmentorders/{}".format(shipment_id))
    shipment_data = shipment["shipmentorder"]
    context.log.INFO("Zoho native status from detail: {}".format(shipment_data.get("status")))

    package_ids = [p["package_id"] for p in shipment_data["packages"]]

    if dry_run:
        context.log.INFO("[DRY-RUN] Zoho POST skipped.")
        return True

    if native.lower() == "shipped":
        update_body = {
            "shipment_number": shipment_data["shipment_number"],
            "date":            shipment_data["date"],
            "delivery_method": shipment_data["delivery_method"],
            "status": status,
        }
        context.log.INFO("Would Update Zoho= {}".format(update_body))
        result = zoho_post(context, "shipmentorders/{}/setstatusasshipped".format(shipment_id), update_body)
        if result.get("code") == 0:
            context.log.INFO("Shipped status updated successfully")
            return True
    elif native.lower() == "delivered":
        update_body = {
            "shipment_number": shipment_data["shipment_number"],
            "date":            shipment_data["date"],
            "delivery_method": shipment_data["delivery_method"],
            "status": status,
            "event_time": format_date(del_date),
        }
        context.log.INFO("Would Update Zoho= {}".format(update_body))
        result = zoho_post_delivered(
            context,
            "shipmentorders/{}/setstatusasdelivered".format(shipment_id),
            update_body,
            extra_headers={"X-Update-Body": json.dumps(update_body)}
        )
        if result.get("code") == 0:
            context.log.INFO("Delivered status updated successfully")
            return True
    else:
        context.log.INFO("SKIP update: status '{}' has no Zoho native mapping".format(status))
        return False



    # del_date_formatted = format_date(del_date)
    # update_body = {
    #     "shipment_number": shipment_data["shipment_number"],
    #     "date":            shipment_data["date"],
    #     "delivery_method": shipment_data["delivery_method"],
    #     # "shipment_sub_status": status,
    #     "delivery_date": del_date_formatted,
    #     # "shipmentorder_custom_fields": [
    #     #     {"api_name": "cf_api_tracking_status", "value": status},
    #     #     {"api_name": "cf_delivery_date",          "value": del_date}
    #     # ]
    # }

    # if dry_run:
    #     context.log.INFO("[DRY-RUN] Zoho POST skipped.")
    #     return True
        
    # update_result = zoho_put(
    #     context,
    #     "shipmentorders/{}".format(shipment_id),
    #     update_body,
    #     {"package_ids": package_ids}
    # )

    # if update_result.get("code") == 0:
    #     context.log.INFO("Sub-Status updated successfully.")
    #     # if native.lower() == "delivered":
    #     #     result = zoho_post(context, "shipmentorders/{}/status/{}".format(shipment_id, native.lower()), body)
    #     #     if result.get("code") == 0:
    #     #         context.log.INFO("Delivered status updated successfully")
    #     #         return True
    #     #     else:
    #     #         context.log.INFO(" Native status update blocked: {} (code={})".format(
    #     #             result.get("message", ""), result.get("code")))
    #     #         return False
    #     # else:
    #     #     return True
    # else:
    #     context.log.INFO(" Custom fields update failed: {} (code={})".format(
    #         update_result.get("message", ""), update_result.get("code")))
    #     return False


# DELHIVERY DIRECT API

def track_delhivery(awb):
    is_lr = bool(re.match(r"^\d{9}$", awb.strip()))
    primary, fallback = ("ref_ids", "waybill") if is_lr else ("waybill", "ref_ids")
    try:
        hdrs = dict(list(HEADERS.items()) + [("Authorization", "Token {}".format(DELHIVERY_API_TOKEN))])
        r = requests.get(
            "https://track.delhivery.com/api/v1/packages/json/",
            headers=hdrs, params={primary: awb}, timeout=15
        )
        data  = safe_json(r) or {}
        ships = data.get("ShipmentData") or []
        if not ships:
            r2    = requests.get(
                "https://track.delhivery.com/api/v1/packages/json/",
                headers=hdrs, params={fallback: awb}, timeout=15
            )
            data  = safe_json(r2) or {}
            ships = data.get("ShipmentData") or []
        if not ships:
            return make_err("Delhivery", awb, "NOT FOUND", "No shipment data from API")
        s          = ships[0].get("Shipment", {}) or {}
        status_obj = s.get("Status") or {}
        if isinstance(status_obj, dict):
            status  = status_obj.get("Status") or status_obj.get("status") or ""
            remarks = status_obj.get("Instructions") or status_obj.get("remark") or ""
        else:
            status  = str(status_obj)
            remarks = ""
        edd = (s.get("PromisedDeliveryDate") or s.get("ExpectedDeliveryDate")
               or s.get("expectedDate") or s.get("EDD") or "")
        del_date = s.get("DeliveryDate") or s.get("DeliveryDateTime") or s.get("deliveryDate") or ""
        if not del_date and "deliver" in str(status).lower():
            for scan in reversed(s.get("Scans") or []):
                sd = scan.get("ScanDetail") or {}
                if "deliver" in str(sd.get("Scan", "")).lower():
                    del_date = sd.get("ScanDateTime") or sd.get("StatusDateTime") or ""
                    break
        raw_status = clean(status)
        
        norm_status = norm_dispatch_status(raw_status)
        return {
            "courier": "Delhivery", "awb": awb, "status": norm_status,
            "edd": fmt_dt(clean(str(edd))), "delivered_date": fmt_dt(clean(str(del_date))),
            "remarks": clean(remarks) or raw_status
        }
    except Exception as e:
        return make_err("Delhivery", awb, "CONNECTION ERROR", str(e))


# DTDC LTL API (mywebxpress, numeric AWB)

def track_dtdc_ltl(awb):
    try:
        hdrs = dict(list(HEADERS.items()) + [
            ("XX-Authentication-Token", DTDC_LTL_TOKEN),
            ("api-key", DTDC_LTL_KEY),
            ("Content-Type", "application/json"),
        ])
        r = requests.post(
            DTDC_LTL_URL, headers=hdrs,
            data=json.dumps({"TrkType": "cnno", "strCnno": awb.strip().upper(), "addtnlDtl": "Y"}),
            timeout=15
        )
        if r.status_code != 200:
            return make_err("DTDC", awb, "HTTP {}".format(r.status_code), r.text[:200])
        data = safe_json(r)
        if not data:
            return make_err("DTDC", awb, "PARSE ERROR", "Empty response")
        if not data.get("IsSuccess", True):
            return make_err("DTDC", awb, "NOT FOUND", data.get("strError") or "IsSuccess=false")
        consignment = data.get("CONSIGNMENT") or {}
        header      = consignment.get("CNHEADER") or {}
        if not header:
            return make_err("DTDC", awb, "NOT FOUND", "No CNHEADER")
        raw_status = clean(header.get("strStatus") or "")
        
        status   = norm_dispatch_status(raw_status)
        edd      = fmt_dmy(header.get("EDD") or "")
        del_date = fmt_dmy(header.get("strStatusTransOn") or "", header.get("strStatusTransTime") or "")
        remarks  = clean(header.get("strRemarks") or "") or raw_status
        actions  = (consignment.get("CNBODY") or {}).get("CNACTION") or []
        if actions:
            l    = actions[-1]
            loc  = clean(l.get("strOrigin") or l.get("strDestination") or "")
            dt   = fmt_dmy(l.get("strActionDate", ""), l.get("strActionTime", "")) if l.get("strActionDate") else ""
            parts = [p for p in [
                clean(l.get("strAction") or ""),
                "at {}".format(loc) if loc else "",
                "on {}".format(dt)  if dt  else "",
            ] if p]
            if parts:
                remarks = " ".join(parts)
        origin = clean(header.get("strOrigin") or "")
        dest   = clean(header.get("strDestination") or "")
        if origin and dest and origin != dest:
            remarks = "{} | {} to {}".format(remarks, origin, dest).strip(" |")
        return {"courier": "DTDC", "awb": awb, "status": status,
                "edd": edd, "delivered_date": del_date, "remarks": remarks}
    except Exception as e:
        return make_err("DTDC", awb, "API ERROR", str(e))


# DTDC SURFACE API (blktracksvc GL018, alpha AWB)

def _get_sx_token():
    if _sx_token["v"]:
        return _sx_token["v"]
    try:
        r = requests.get(
            DTDC_SX_AUTH_URL,
            params={"username": DTDC_SX_USER, "password": DTDC_SX_PASS},
            headers=HEADERS, timeout=15
        )
        if r.status_code == 200:
            t = r.text.strip().strip('"')
            if t:
                _sx_token["v"] = t
                return t
    except Exception:
        pass
    return ""


def track_dtdc_surface(awb):
    token = _get_sx_token()
    if not token:
        return make_err("DTDC-Surface", awb, "AUTH FAILED", "Cannot authenticate with blktracksvc.dtdc.com")
    try:
        payload = json.dumps({"trkType": "cnno", "strcnno": awb.strip().upper(), "addtnlDtl": "Y"})
        hdrs    = dict(list(HEADERS.items()) + [
            ("Content-Type", "application/json"),
            ("x-access-token", token),
        ])
        r = requests.post(DTDC_SX_TRACK_URL, headers=hdrs, data=payload, timeout=15)
        if r.status_code == 404:
            r = requests.post(DTDC_SX_TRACK_URL2, headers=hdrs, data=payload, timeout=15)
        if r.status_code == 401:
            _sx_token["v"] = None
            token = _get_sx_token()
            if token:
                hdrs["x-access-token"] = token
                r = requests.post(DTDC_SX_TRACK_URL, headers=hdrs, data=payload, timeout=15)
                if r.status_code == 404:
                    r = requests.post(DTDC_SX_TRACK_URL2, headers=hdrs, data=payload, timeout=15)
        if r.status_code != 200:
            return make_err("DTDC-Surface", awb, "HTTP {}".format(r.status_code), r.text[:200])
        data = safe_json(r)
        if not data:
            return make_err("DTDC-Surface", awb, "PARSE ERROR", "Empty response")
        if not data.get("statusFlag", True):
            errors = data.get("errorDetails") or []
            msg = "; ".join(e.get("value", "") for e in errors if e.get("value")) if errors else "No data"
            return make_err("DTDC-Surface", awb, "NOT FOUND", msg)
        header = data.get("trackHeader") or {}
        if not header:
            return make_err("DTDC-Surface", awb, "NOT FOUND", "No trackHeader")
        raw_status = clean(header.get("strStatus") or "")
        if not raw_status:
            return make_err("DTDC-Surface", awb, "NOT FOUND", "Empty status")
        
        status = norm_dispatch_status(raw_status)
        edd_raw = ""
        for k in ["strExpectedDeliveryDate", "strRevExpectedDeliveryDate", "strEDD", "edd", "EDD"]:
            v = header.get(k) or ""
            if v and str(v).strip() not in ("", "None", "null", "0", "00000000"):
                edd_raw = str(v)
                break
        if not edd_raw:
            for k, v in header.items():
                if v and any(x in k.lower() for x in ["edd", "expected", "promised"]):
                    if str(v).strip() not in ("", "None", "null", "0", "00000000"):
                        edd_raw = str(v)
                        break
        edd      = fmt_dmy(edd_raw)
        del_date = fmt_dmy(header.get("strStatusTransOn") or "", header.get("strStatusTransTime") or "")
        scans    = data.get("trackDetails") or []
        if scans:
            l    = scans[-1]
            loc  = clean(l.get("strOrigin") or "")
            dt   = fmt_dmy(l.get("strActionDate", ""), l.get("strActionTime", "")) if l.get("strActionDate") else ""
            rem  = clean(l.get("sTrRemarks") or l.get("strRemarks") or "")
            parts = [p for p in [
                clean(l.get("strAction") or ""),
                "at {}".format(loc) if loc else "",
                "on {}".format(dt)  if dt  else "",
                "({})".format(rem)  if rem.lower() not in ("", "null", "none") else "",
            ] if p]
            remarks = " ".join(parts)
        else:
            remarks = clean(header.get("strRemarks") or "")
        origin = clean(header.get("strOrigin") or "")
        dest   = clean(header.get("strDestination") or "")
        if origin and dest and origin != dest:
            remarks = "{} | {} to {}".format(remarks, origin, dest).strip(" |")
        return {"courier": "DTDC-Surface", "awb": awb, "status": status,
                "edd": edd, "delivered_date": del_date, "remarks": remarks}
    except requests.exceptions.ConnectionError:
        result = track_dispatch(awb, "DTDC-Surface", ["ecom", "express", "ltl"])
        if result["status"] not in ("NOT FOUND", "CONNECTION ERROR", "PARSE ERROR", "AUTH ERROR"):
            return result
        return make_err("DTDC-Surface", awb, "CONNECTION ERROR",
                        "Cannot reach blktracksvc.dtdc.com - check internet/VPN or firewall")
    except Exception as e:
        return make_err("DTDC-Surface", awb, "API ERROR", str(e))


# DISPATCH SOLUTIONS Ashrey 3PL API

def track_dispatch(awb, label, endpoints=None):
    if endpoints is None:
        endpoints = ["ecom", "express", "ltl"]
    for ep in endpoints:
        try:
            r = requests.get(
                "{}/{}/{}".format(DISPATCH_BASE_URL, ep, awb),
                headers=dict(list(HEADERS.items()) + [("api-key", DISPATCH_SOLUTIONS_KEY)]),
                timeout=15
            )
            if r.status_code == 200:
                data = safe_json(r)
                if data and data.get("success"):
                    d     = data.get("data") or {}
                    scans = d.get("trackingData") or []
                    if not scans:
                        continue
                    latest   = scans[0]
                    raw_desc = clean(latest.get("scan_description") or latest.get("remark") or "")
                    status   = norm_dispatch_status(raw_desc) or norm_dispatch_status(clean(d.get("remark") or ""))
                    if not status:
                        continue
                    del_date = ""
                    for scan in scans:
                        if norm_dispatch_status(clean(scan.get("scan_description") or "")) == "Delivered" and not del_date:
                            del_date = fmt_dt(clean(scan.get("scan_datetime") or scan.get("scan_date") or ""))
                            break
                    edd_raw = d.get("edd") or d.get("EDD") or d.get("expectedDeliveryDate") or ""
                    edd     = fmt_dt(clean(str(edd_raw))) if edd_raw else ""
                    loc     = clean(latest.get("location") or "")
                    sc_dt   = fmt_dt(clean(latest.get("scan_datetime") or ""))
                    courier = clean(d.get("courier") or "")
                    parts   = [p for p in [
                        raw_desc,
                        "at {}".format(loc)   if loc   else "",
                        "on {}".format(sc_dt) if sc_dt else "",
                    ] if p]
                    return {
                        "courier":        "{} ({})".format(label, courier) if courier else label,
                        "awb":            awb,
                        "status":         status,
                        "edd":            edd,
                        "delivered_date": del_date,
                        "remarks":        " ".join(parts),
                    }
            elif r.status_code == 401:
                return make_err(label, awb, "AUTH ERROR", "Invalid Dispatch Solutions API key")
        except requests.exceptions.ConnectionError:
            return make_err(label, awb, "CONNECTION ERROR", "Cannot reach dispatchsolutions.in")
        except Exception:
            continue
    return make_err(label, awb, "NOT FOUND",
                    "AWB not found on Dispatch Solutions ({})".format("/".join(endpoints)))


# BLUEDART DIRECT API

def _get_bd_token(login_id, password):
    if _bd_token_cache.get(login_id):
        return _bd_token_cache[login_id]
    try:
        r = requests.post(
            "https://apigateway.bluedart.com/in/transportation/token/v1/login",
            headers=dict(list(HEADERS.items()) + [("Content-Type", "application/json")]),
            data=json.dumps({"clientid": login_id, "password": password}),
            timeout=15
        )
        if r.status_code == 200:
            data  = safe_json(r) or {}
            token = data.get("JWTToken") or data.get("token") or data.get("access_token") or ""
            if token:
                if not token.startswith("Bearer "):
                    token = "Bearer {}".format(token)
                _bd_token_cache[login_id] = token
                return token
    except Exception:
        pass
    return ""


def _bd_track_request(login_id, token, awb, fmt="json"):
    return requests.get(
        "https://apigateway.bluedart.com/in/transportation/tracking/v1",
        headers=dict(list(HEADERS.items()) + [("JWTToken", token)]),
        params={
            "handler": "tnt", "action": "custawbquery",
            "loginid": login_id, "awb": "awb",
            "numbers": awb, "format": fmt,
            "lickey": BLUEDART_LIC_KEY,
            "verno": "1.3", "scan": "1",
        },
        timeout=15
    )


def _parse_bd_response(r, awb):
    text = r.text.strip()
    if not text:
        return None

    # Try JSON first
    try:
        data = r.json()
        if isinstance(data, list):
            data = data[0] if data else {}
        ships = data.get("ShipmentData") or []

        pass  # ShipmentData debug log removed
        if ships:
            s          = ships[0].get("Shipment") or ships[0]
            status_obj = s.get("Status") or {}
            if isinstance(status_obj, dict):
                raw_status = (status_obj.get("StatusType") or status_obj.get("Status")
                              or status_obj.get("StatusDescription") or status_obj.get("status") or "")
                remarks    = status_obj.get("Instructions") or status_obj.get("StatusDescription") or ""
            else:
                raw_status = str(status_obj)
                remarks    = ""
            status      = norm_bd_status(raw_status)
            edd         = parse_bd_date(s.get("ExpectedDeliveryDate") or s.get("PromisedDeliveryDate") or s.get("EDD") or "")
            status_date = parse_bd_date(s.get("StatusDate") or s.get("DeliveryDate") or "")
            del_date    = status_date if "deliver" in status.lower() else ""
            if not del_date and "deliver" in status.lower():
                for scan in reversed(s.get("Scans") or []):
                    sd = scan.get("ScanDetail") or {}
                    if "deliver" in str(sd.get("Scan", "")).lower():
                        del_date = parse_bd_date(sd.get("ScanDateTime") or "")
                        break
            if status:
                return {"courier": "BlueDart", "awb": awb, "status": status,
                        "edd": edd, "delivered_date": del_date, "remarks": clean(remarks)}
        # Flat JSON fallback
        raw_status = (data.get("StatusType") or data.get("Status") or
                      data.get("ShipmentStatus") or data.get("status") or "")
        status     = norm_bd_status(raw_status)
        if status:
            edd      = parse_bd_date(data.get("ExpectedDeliveryDate") or data.get("EDD") or "")
            st_d     = parse_bd_date(data.get("StatusDate") or data.get("DeliveryDate") or "")
            del_date = st_d if "deliver" in status.lower() else ""
            return {"courier": "BlueDart", "awb": awb, "status": status,
                    "edd": edd, "delivered_date": del_date,
                    "remarks": clean(str(data.get("StatusDescription") or data.get("Remarks") or ""))}
    except Exception:
        pass

    # Try XML
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(text)

        def fx(tag):
            el = root.find(".//" + tag)
            return el.text.strip() if el is not None and el.text else ""

        raw_status  = (fx("StatusType") or fx("Status") or fx("ShipmentStatus") or fx("StatusCode") or "")
        status      = norm_bd_status(raw_status)
        edd         = parse_bd_date(fx("ExpectedDeliveryDate") or fx("PromisedDeliveryDate") or fx("EDD"))
        status_date = parse_bd_date(fx("StatusDate") or fx("DeliveryDate") or fx("ActualDeliveryDate"))
        del_date    = status_date if "deliver" in status.lower() else ""
        remarks     = fx("StatusDescription") or fx("Remarks") or fx("Instructions") or ""
        if "not linked" in remarks.lower() or remarks.strip().upper() in ("DL", "OD", "IT", "PU", "BK", "ND", "RT"):
            remarks = ""
        if not status:
            for kw, mapped in [
                ("Delivered", "Delivered"), ("Out for Delivery", "Out for Delivery"),
                ("In Transit", "In Transit"), ("Picked Up", "Picked Up"), ("Booked", "Booked")
            ]:
                if kw.lower() in text.lower():
                    status = mapped
                    break
        if status:
            return {"courier": "BlueDart", "awb": awb, "status": status,
                    "edd": edd, "delivered_date": del_date, "remarks": clean(remarks)}
    except Exception:
        pass

    return None


def track_bluedart(awb, context):
    awb = awb.strip()
    for login_id, password in [
        (BLUEDART_LOGIN_ID,  BLUEDART_PASSWORD),
        (BLUEDART_LOGIN_ID2, BLUEDART_PASSWORD),
        (BLUEDART_LOGIN_ID3, BLUEDART_PASSWORD),
    ]:
        if not login_id:
            continue
        try:
            token = _get_bd_token(login_id, password)
            if token:
                r = _bd_track_request(login_id, token, awb, fmt="json")
                if r.status_code == 401:
                    _bd_token_cache.pop(login_id, None)
                    token = _get_bd_token(login_id, password)
                    if token:
                        r = _bd_track_request(login_id, token, awb, fmt="json")
                if r.status_code == 200:
                    result = _parse_bd_response(r, awb)
                    if result:
                        return result
        except Exception:
            pass
        try:
            r2 = requests.get(
                "https://api.bluedart.com/servlet/RoutingServlet",
                params={
                    "handler": "tnt", "action": "custawbquery",
                    "loginid": login_id, "awb": "awb",
                    "numbers": awb, "format": "xml",
                    "lickey": BLUEDART_LIC_KEY, "verno": "1.3", "scan": "1"
                },
                headers=HEADERS, timeout=15
            )
            if r2.status_code == 200 and r2.text.strip():
                result = _parse_bd_response(r2, awb)
                if result:
                    return result
        except Exception:
            pass

    # Fallback to Dispatch Solutions
    result = track_dispatch(awb, "BlueDart", ["ecom", "express", "ltl"])
    if result["status"] not in ("NOT FOUND", "CONNECTION ERROR", "PARSE ERROR", "AUTH ERROR"):
        return result
    return make_err("BlueDart", awb, "FETCH FAILED",
                    "All BlueDart API attempts failed. Check: IP whitelisted? Credentials active?")


# MAIN COURIER ROUTER

def track(awb, carrier, context):
    route = get_route(carrier)

    if route == "delhivery":
        return track_delhivery(awb)

    if route == "dispatch_lr":
        return track_dispatch(awb, "Delhivery-LR")

    if route == "dispatch_bluedart":
        return track_dispatch(awb, "Ashrey-BlueDart")

    if route == "bluedart":
        return track_bluedart(awb, context)

    if route == "dispatch_dtdc":
        # Try Dispatch Solutions first, fall back to DTDC direct API
        result = track_dispatch(awb, "Ashrey-DTDC")
        if result["status"] not in ("NOT FOUND", "CONNECTION ERROR", "PARSE ERROR", "AUTH ERROR", "FETCH FAILED"):
            return result
        context.log.INFO("  Dispatch Solutions failed for Aashrey-DTDC, falling back to DTDC direct API...")
        if is_surface_awb(awb):
            return track_dtdc_surface(awb)
        else:
            return track_dtdc_ltl(awb)

    if route == "dtdc_own":
        if is_surface_awb(awb):
            return track_dtdc_surface(awb)
        else:
            return track_dtdc_ltl(awb)

    return make_err("Unknown", awb, "NOT FOUND", "Carrier '{}' not recognized in dropdown.".format(carrier))


# DISCOVER MODE

def discover(context):
    context.log.INFO("=" * 60)
    context.log.INFO("CUSTOM FIELDS for shipmentorders:")
    context.log.INFO("=" * 60)
    data  = zoho_get(context, "settings/customfields", {"module": "shipmentorders"})
    items = data if isinstance(data, list) else data.get("customfields") or []
    if not items:
        context.log.INFO("None found. Raw: {}".format(json.dumps(data)[:500]))
    for cf in items:
        if isinstance(cf, dict):
            context.log.INFO("  customfield_id : {}".format(cf.get("customfield_id")))
            context.log.INFO("  label          : {}".format(cf.get("label")))
            context.log.INFO("  field_name     : {}".format(cf.get("field_name")))
            context.log.INFO("  data_type      : {}".format(cf.get("data_type")))

    context.log.INFO("=" * 60)
    context.log.INFO("FIRST SHIPMENT fields from GET detail:")
    context.log.INFO("=" * 60)
    data = zoho_get(context, "shipmentorders", {"per_page": 1, "page": 1})
    shps = data.get("shipmentorders") or []
    if shps:
        sid    = shps[0].get("shipment_id")
        detail = get_shipment_detail(context, sid)
        context.log.INFO("  Shipment      : {}".format(shps[0].get("shipment_number") or sid))
        context.log.INFO("  carrier       : {}".format(detail.get("carrier")))
        context.log.INFO("  tracking_number: {}".format(detail.get("tracking_number")))
        context.log.INFO("  status        : {}".format(detail.get("status")))
        context.log.INFO("  tracking_status: {}".format(detail.get("tracking_status")))
        for cf in (detail.get("custom_fields") or []):
            context.log.INFO("    label='{}' id='{}' value='{}'".format(
                cf.get("label"), cf.get("customfield_id"), cf.get("value")))


# DEBUG MODE

def debug_find_shipments(context):
    context.log.INFO("Org ID: {}".format(ZOHO_ORG_ID))
    for ep in ["shipmentorders", "shipments", "packages", "invoices"]:
        try:
            data = zoho_get(context, ep, {"per_page": 5, "page": 1})
            lk   = next((k for k, v in data.items()
                         if isinstance(v, list) and k not in ("custom_fields", "errors")), None)
            if lk:
                context.log.INFO("  OK   /{} count={}".format(ep, len(data[lk])))
            else:
                context.log.INFO("  FAIL /{} code={} {}".format(
                    ep, data.get("code", "?"), str(data.get("message", ""))[:60]))
        except Exception as e:
            context.log.INFO("  ERR  /{} {}".format(ep, str(e)))


# MAIN SYNC

def main(context, dry_run=True):
    context.log.INFO("=" * 60)
    context.log.INFO("Zoho Books Shipment Tracking Sync")
    context.log.INFO("Mode: {}".format("DRY-RUN (print only)" if dry_run else "LIVE (will update Zoho)"))
    context.log.INFO("=" * 60)
    context.log.INFO("Fetching shipments from Zoho Books (all pages)...")

    shipments = get_all_shipments(context)
    context.log.INFO("Total shipments fetched: {}".format(len(shipments)))
    # shipments = shipments[50:100]

    if not shipments:
        context.log.INFO("WARNING: No shipments found. Check Org ID / token.")
        return

    updated = 0
    skipped = 0
    errors  = 0
    no_awb  = 0

    for shp in shipments:
        shipment_id = shp.get("shipment_id") or shp.get("shipmentorder_id") or ""
        shipment_no = (shp.get("shipment_order_number") or shp.get("shipment_number")
                       or shipment_id or "")
        awb         = str(shp.get("tracking_number") or "").strip()
        carrier     = str(shp.get("carrier") or "").strip()
        cur_status  = str(shp.get("status") or "").strip().lower()

        # If no AWB in summary, fetch full detail
        if not awb:
            detail  = get_shipment_detail(context, shipment_id)
            time.sleep(0.2)
            awb     = str(detail.get("tracking_number") or "").strip()
            carrier = str(detail.get("carrier") or "").strip()
            if not awb:
                awb     = get_cf_value(detail, "Tracking Number") or get_cf_value(detail, "Tracking#")
                carrier = carrier or get_cf_value(detail, "Carrier") or get_cf_value(detail, "Courier")

        context.log.INFO("Shipment: {} | AWB: {} | Carrier: {} | Status: {}".format(
            shipment_no, awb or "(none)", carrier or "(none)", cur_status))

        if not awb or awb.lower() in ("nan", "none", ""):
            context.log.INFO("  SKIP: No AWB")
            no_awb += 1
            continue

        if cur_status == "delivered":
            context.log.INFO("  SKIP: Already Delivered in Zoho")
            skipped += 1
            continue

        route = get_route(carrier)
        if route == "unknown":
            context.log.INFO("  SKIP: Carrier '{}' is not in the tracked dropdown list.".format(carrier))
            skipped += 1
            continue

        try:
            context.log.INFO("  Carrier recognized (route={}), calling tracking API...".format(route))
            result   = track(awb, carrier, context)
            status   = result.get("status") or ""
            del_date = result.get("delivered_date") or result.get("delivery_date") or ""
            edd      = result.get("edd") or ""
            remarks  = result.get("remarks") or ""

            context.log.INFO("  API result: status={} | EDD={} | Delivered={} | Remarks={}".format(
                status, edd, del_date, remarks))

            if status in ("NOT FOUND", "CONNECTION ERROR", "PARSE ERROR",
                          "AUTH ERROR", "FETCH FAILED", "AUTH FAILED", ""):
                context.log.INFO("  Could not get tracking data: {}".format(remarks))
                errors += 1
                # continue

            ok = update_shipment(context, shipment_id, status, edd, del_date, dry_run=dry_run)
            if ok:
                updated += 1
            else:
                context.log.INFO("  NOTE: {} native status update blocked by Zoho (AWB:{})".format(
                    shipment_no, awb))
                skipped += 1

            time.sleep(DELAY_BETWEEN)

        except Exception as e:
            context.log.INFO("  ERROR processing {}: {}".format(shipment_no, str(e)))
            errors += 1

    context.log.INFO("=" * 60)
    context.log.INFO("SUMMARY: Updated={} | Skipped={} | No-AWB={} | Errors={}".format(
        updated, skipped, no_awb, errors))
    context.log.INFO("=" * 60)


# ZOHO FUNCTION ENTRY POINT

def runner(context, basicIO):
    try:
        moduleObject = json.loads(basicIO.getParameter("shipment_order"))
        context.log.INFO("Shipment Order Received")

        organizationObject = json.loads(basicIO.getParameter("organization"))
        context.log.INFO("Organization ID: {}".format(organizationObject["organization_id"]))

        # dry_run=True means print results only, do NOT post to Zoho
        # Change to dry_run=False when ready to go live
        main(context, dry_run=False)

    except Exception as e:
        context.log.INFO("ERROR in runner: {}".format(str(e)))