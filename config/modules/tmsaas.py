import json

import requests

from config.modules.utils import decrypt_text, log_request, get_site_details

bank = get_site_details()


class TMSaaSAPI:

    @classmethod
    def get_header(cls):
        header = {
            # "client-id": decrypt_text(bank.tmsaasKey)
            "client-id": bank.tmsaasKey
        }
        return header

    @classmethod
    def get_base_url(cls):
        url = str(bank.tmsaasBaseUrl)
        return url

    @classmethod
    def get_networks(cls):
        url = cls.get_base_url() + "/data/creditswitch/networks"
        header = cls.get_header()
        log_request(f"GET Bill Payment Networks Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"GET Bill Payment Networks Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_data_plan(cls, network_name):
        url = cls.get_base_url() + f"/data/plans?provider=creditswitch&network={network_name}"
        header = cls.get_header()
        log_request(f"GET Data Plan(s) Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"GET Data Plan(s) Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def purchase_airtime(cls, **kwargs):
        url = cls.get_base_url() + "/airtime"
        header = cls.get_header()
        payload = dict()
        payload["provider"] = "creditswitch"
        payload["phoneNumber"] = kwargs.get("phone_number")
        payload["network"] = kwargs.get("network")
        payload["amount"] = kwargs.get("amount")
        log_request(f"Purchase Airtime Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Purchase Airtime Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def vend_betting(cls, **kwargs):
        url = cls.get_base_url() + "/betting"
        header = cls.get_header()
        payload = dict()
        amount = float(kwargs.get("amount"))
        payload["provider"] = "creditswitch"
        payload["betProvider"] = kwargs.get("provider")
        payload["customerId"] = kwargs.get("customer_id")
        payload["name"] = kwargs.get("name")
        payload["serviceId"] = kwargs.get("service_id")
        payload["amount"] = amount
        log_request(f"Vend Betting Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Vend Betting Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def purchase_data(cls, **kwargs):
        url = cls.get_base_url() + "/data"
        header = cls.get_header()
        payload = dict()
        payload["planId"] = kwargs.get("plan_id")
        payload["phoneNumber"] = kwargs.get("phone_number")
        payload["provider"] = "creditswitch"
        payload["amount"] = kwargs.get("amount")
        payload["network"] = kwargs.get("network")
        log_request(f"Vend Data Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Vend Data Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_services(cls, service_type):
        url = cls.get_base_url() + f"/serviceBiller/{service_type}"
        header = cls.get_header()
        log_request(f"GET TMSaaS Service Billers Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"TMSaaS Service Billers Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_service_products(cls, service_name, product_code=None):
        url = cls.get_base_url() + f"/{service_name}/products?provider=cdl"
        header = cls.get_header()
        if product_code:
            url = cls.get_base_url() + f"/{service_name}/addons?provider=cdl&productCode={product_code}"
        log_request(f"GET TMSaaS Products Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"TMSaaS Products Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def validate_smart_card(cls, service_name, scn):
        url = cls.get_base_url() + f"/{service_name}/validate"
        header = cls.get_header()
        header["Content-Type"] = "application/x-www-form-urlencoded"
        payload = f"provider=cdl&smartCardNumber={scn}"
        log_request(f"Validate SmartCardNumber TMSaaS:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Validate SmartCardNumber TMSaaS Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def cable_tv_subscription(cls, service_name, **kwargs):
        url = cls.get_base_url() + f"/{service_name}"
        header = cls.get_header()
        header["Content-Type"] = "application/json"
        amount = float(kwargs.get("amount"))
        payload = json.dumps({
                    "provider": "cdl",
                    "monthsPaidFor": kwargs.get("duration"),
                    "customerNumber": kwargs.get("customer_number"),
                    "amount": amount,
                    "customerName": kwargs.get("customer_name"),
                    "productCodes": kwargs.get("product_codes"),
                    "invoicePeriod": kwargs.get("duration"),
                    "smartcardNumber": kwargs.get("smart_card_no")
                })
        log_request(f"Cable TV Subscription Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Cable TV Subscription Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_distribution_company(cls):
        url = cls.get_base_url() + f"/electricity/getDiscos"
        header = cls.get_header()
        log_request(f"GET Distribution Companies Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"GET Distribution Companies Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_betting_providers(cls):
        url = cls.get_base_url() + f"/betting/creditswitch/providers"
        header = cls.get_header()
        log_request(f"GET Betting Provider Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"GET Betting Provider Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def validate_betting(cls, customer_id, provider):
        url = cls.get_base_url() + f"/betting/validate"
        header = cls.get_header()
        payload = dict()
        payload["provider"] = "creditswitch"
        payload["betProvider"] = provider
        payload["customerId"] = customer_id
        log_request(f"Validate Betting Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Validate Betting Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def validate_meter_no(cls, disco_type, meter_no):
        url = cls.get_base_url() + f"/electricity/validate"
        header = cls.get_header()
        payload = dict()
        payload["type"] = disco_type
        payload["customerReference"] = meter_no
        log_request(f"Validate MeterNo Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Validate MeterNo Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def vend_electricity(cls, disco_type, meter_no, amount, phone_number):
        validate_response = cls.validate_meter_no(disco_type, meter_no)
        vending_amount = float(amount)

        response_data = dict()
        response_data["success"] = False
        response_data["message"] = "An error occurred while trying to vend electricity"
        response_data["token"] = None
        response_data["status"] = "pending"
        response_data["transaction_id"] = None

        if "error" in validate_response:
            response_data["message"] = "Meter Validation Error"
            response_data["status"] = "failed"
            return response_data

        if disco_type == "IKEDC_POSTPAID":
            payload = {
                "disco": "IKEDC_POSTPAID",
                "customerReference": meter_no,
                "customerAddress": validate_response["data"]["address"],
                "amount": vending_amount,
                "customerName": validate_response["data"]["name"],
                "phoneNumber": phone_number,
                "customerAccountType": validate_response["data"]["customerAccountType"],
                "accountNumber": validate_response["data"]["accountNumber"],
                "customerAccountId": meter_no,
                "customerDtNumber": validate_response["data"]["customerDtNumber"],
                "contactType": "LANDLORD"
            }

        elif disco_type == "IKEDC_PREPAID":
            payload = {
                "disco": "IKEDC_PREPAID",
                "customerReference": meter_no,
                "customerAccountId": meter_no,
                "canVend": True,
                "customerAddress": validate_response["data"]["address"],
                "meterNumber": meter_no,
                "customerName": validate_response["data"]["name"],
                "customerAccountType": validate_response["data"]["customerAccountType"],
                "accountNumber": validate_response["data"]["accountNumber"],
                "customerDtNumber": validate_response["data"]["customerDtNumber"],
                "amount": vending_amount,
                "phoneNumber": phone_number,
                "contactType": "LANDLORD"
            }

        elif disco_type == "EKEDC_POSTPAID":
            payload = {
                "disco": "EKEDC_POSTPAID",
                "accountNumber": meter_no,
                "amount": vending_amount
            }

        elif disco_type == "EKEDC_PREPAID":
            payload = {
                "disco": "EKEDC_PREPAID",
                "customerReference": meter_no,
                "canVend": True,
                "customerAddress": validate_response["data"]["customerAddress"],
                "meterNumber": meter_no,
                "customerName": validate_response["data"]["customerName"],
                "amount": vending_amount
            }

        elif disco_type == "IBEDC_POSTPAID":
            payload = {
                "disco": "IBEDC_POSTPAID",
                "customerReference": meter_no,
                "amount": vending_amount,
                "thirdPartyCode": "21",
                "customerName": str(validate_response["data"]["firstName"] + " " + validate_response["data"]["lastName"])
            }

        elif disco_type == "IBEDC_PREPAID":
            payload = {
                "disco": "IBEDC_PREPAID",
                "customerReference": meter_no,
                "amount": vending_amount,
                "thirdPartyCode": "21",
                "customerType": "PREPAID",
                "firstName": validate_response["data"]["firstName"],
                "lastName": validate_response["data"]["lastName"]
            }
        else:
            response_data["message"] = "Distribution company type is not valid"
            response_data["status"] = "failed"
            return response_data

        header = cls.get_header()
        url = cls.get_base_url() + f"/electricity/vend"
        log_request(f"Vending Electricity ({disco_type}) Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        req = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Vending Electricity ({disco_type}) Response:\nresponse: {req.text}")

        response = req.json()

        if "error" in response:
            response_data["message"] = response["error"]
            response_data["status"] = "failed"
            return response_data

        provider_status = response["data"]["providerResponse"]["status"]

        response_data["success"] = True
        response_data["message"] = "An error occurred while trying to vend electricity"
        response_data["transaction_id"] = response["data"]["transactionId"]

        if provider_status == "ACCEPTED":
            response_data["status"] = "success"

        if response["data"]["providerResponse"]["token"]:
            response_data["token"] = response["data"]["providerResponse"]["token"]

        return response_data

    @classmethod
    def retry_electricity_vending(cls, transaction_id):
        url = cls.get_base_url() + f"/electricity/query?disco=EKEDC_PREPAID&transactionId={transaction_id}"
        header = cls.get_header()
        log_request(f"Retry Electricity Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"Retry Electricity Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def check_saas_wallet_balance(cls):
        client_id = decrypt_text(bank.tmsaasKey)
        url = cls.get_base_url() + f"/client/wallet/{client_id}"
        header = cls.get_header()
        log_request(f"Check TMSaaS Balance Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"Check TMSaaS Balance Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def perform_liveness_check(cls, bvn, image_url):
        # TM_VERIFICATION_URL = http://188.212.125.218:3030/verification/v1/verification/verifybvnimage
        url = cls.get_base_url() + f"/verification/v1/verification/verifybvnimage"
        header = cls.get_header()
        payload = dict()
        payload["bvn"] = bvn
        payload["image"] = image_url
        log_request(f"Perform Liveness Check Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Perform Liveness Check Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def send_sms(cls, content, receiver):
        url = cls.get_base_url() + f"/sms/send"
        header = cls.get_header()
        header["Content-Type"] = "application/json"
        payload = json.dumps({"message": content, "senderId": bank.tm_sms_sender_id, "recipients": [receiver]})
        log_request(f"Sending TMSaaS SMS Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Sending TMSaaS SMS Response:\nresponse: {response.text}")
        return response.json()



    # Insurance
    @classmethod
    def get_vehicle_insurance_detail(cls, query_type, service_provider=None, vm_id=None):
        url = cls.get_base_url() + f"/insurance/serviceproviders?type=vehicle&provider=uridium"
        if query_type == "make":
            url = cls.get_base_url() + f"/insurance/vehiclemake?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "purpose":
            url = cls.get_base_url() + f"/insurance/vehiclepurpose?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "color":
            url = cls.get_base_url() + f"/insurance/vehiclecolor?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "state":
            url = cls.get_base_url() + f"/insurance/state?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "policy":
            url = cls.get_base_url() + f"/insurance/policy?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "insurance_type":
            url = cls.get_base_url() + f"/insurance/type?type=vehicle&provider=uridium&serviceProvider={service_provider}"
        if query_type == "model":
            url = cls.get_base_url() + f"/insurance/vehiclemodel?type=vehicle&provider=uridium&serviceProvider={service_provider}&vehicleMakeId={vm_id}"

        header = cls.get_header()
        log_request(f"Vehicle Insurance Detail Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"Vehicle Insurance Detail Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_vehicle_insurance_quote(cls, **kwargs):
        url = cls.get_base_url() + f"/insurance/quotes"
        vend_now = kwargs.get("vend_now")
        amount = float(kwargs.get("amount"))
        payload = dict()
        if vend_now == "true":
            url = cls.get_base_url() + f"/insurance/vend"
            payload["amount"] = amount
            payload["quoteId"] = kwargs.get("quote_id")
        payload["insurance_policy_id"] = kwargs.get("policy_id")
        payload["insurance_type_id"] = kwargs.get("insurance_type_id")
        payload["email"] = kwargs.get("email")
        payload["state_code"] = kwargs.get("state_code")
        payload["vehicle_model_id"] = kwargs.get("model")
        payload["vehicle_make_id"] = kwargs.get("make")
        payload["vehicle_color_id"] = kwargs.get("color")
        payload["insured_name"] = kwargs.get("insured_name")
        payload["address"] = kwargs.get("address")
        payload["engine_no"] = kwargs.get("engine_no")
        payload["chassis_no"] = kwargs.get("chassis_no")
        payload["engine_capacity"] = kwargs.get("engine_capacity")
        payload["year_of_make"] = kwargs.get("year")
        payload["vehicle_category_id"] = kwargs.get("category")
        payload["sum_cover"] = kwargs.get("sum_cover")
        payload["phonenumber"] = kwargs.get("phone_number")
        payload["type"] = "vehicle"
        payload["provider"] = "uridium"
        payload["serviceProvider"] = kwargs.get("provider")
        payload["number_plate"] = kwargs.get("plate_number")
        payload["vehicle_purpose_id"] = kwargs.get("purpose")

        header = cls.get_header()
        header["Content-Type"] = "application/x-www-form-urlencoded"
        log_request(f"Vehicle Insurance Quote Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Vehicle Insurance Quote Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def get_my_cover_insurance_plans(cls, insurance_type):
        url = cls.get_base_url() + f"/insurance/plans?provider=mycover&type=health"
        if insurance_type == "gadget":
            url = cls.get_base_url() + f"/insurance/plans?provider=mycover&type=gadget"
        if insurance_type == "content":
            url = cls.get_base_url() + f"/insurance/plans?provider=mycover&type=content"
        header = cls.get_header()
        log_request(f"GET myCover Insurance Plan Request:\nurl: {url}\nheader: {header}")
        response = requests.request("GET", url=url, headers=header)
        log_request(f"GET myCover Insurance Plan Response:\nresponse: {response.text}")
        return response.json()

    @classmethod
    def perform_insurance(cls, insurance_type, **kwargs):
        url = cls.get_base_url() + f"/insurance/vend"
        amount = float(kwargs.get("amount"))
        payload = {
            "firstName": kwargs.get("first_name"),
            "lastName": kwargs.get("last_name"),
            "dob": kwargs.get("dob"),
            "gender": kwargs.get("gender"),
            "email": kwargs.get("email"),
            "phoneNumber": kwargs.get("phone_number"),
            "productId": kwargs.get("product_id"),
            "productName": kwargs.get("product_name"),
            "image": kwargs.get("image"),
            "amount": amount,
            "address": kwargs.get("address"),
            "title": kwargs.get("title"),
        }
        if insurance_type == "health":
            payload.update({
                "provider": "mycover",
                "type": "health",
                "serviceProvider": "MyCoverGenius",
                "paymentPlan": str(kwargs.get("duration")).capitalize()
            })

        if insurance_type in ["shop_content", "office_content", "home_content"]:
            payload.update({
                    "provider": "mycover",
                    "type": "content",
                    "lga": kwargs.get("local_govt"),
                    "isFullYear": True,
                    "identificationName": kwargs.get("indentification_document"),
                    "identificationUrl": kwargs.get("indentification_document_url"),
                    "insuranceStartDate": kwargs.get("insurance_date"),
                    "serviceProvider": "Aiico"
                })
            if insurance_type == "office_content" or "home_content":
                payload.update({
                    "tenancy": kwargs.get("tenancy"),
                    "description": kwargs.get("description"),
                    "preOwnership": ""
                })
            if insurance_type == "office_content":
                payload.update({"officeItems": kwargs.get("items")})
            if insurance_type == "home_content":
                payload.update({"homeItems": kwargs.get("items")})
            if insurance_type == "shop_content":
                payload.update({
                    "shopType": "Box",
                    "natureOfBusiness": kwargs.get("business_type"),
                    "natureOfStock": kwargs.get("stock_type"),
                    "stockKeeping": True,
                    "stockTakingInterval": kwargs.get("stock_interval"),
                    "stockAmount": kwargs.get("stock_amount")
                })

        if insurance_type in ["mycover_gadget", "sovereign_gadget"]:
            payload.update({
                "provider": "mycover",
                "type": "gadget",
                "deviceMake": kwargs.get("make"),
                "deviceModel": kwargs.get("model"),
                "deviceColor": kwargs.get("color"),
                "imeiNumber": kwargs.get("imei"),
                "deviceSerialNumber": kwargs.get("serial_no"),
                "dateOfPurchase": kwargs.get("purchase_date"),
                "deviceType": kwargs.get("device_type"),
                "deviceValue": kwargs.get("device_value"),
            })
            if insurance_type == "mycover_gadget":
                payload.update({"serviceProvider": "MyCoverGenius"})
            if insurance_type == "sovereign_gadget":
                payload.update({"serviceProvider": "Sovereign Trust"})

        header = cls.get_header()
        log_request(f"Vend Insurance Request:\nurl: {url}\nheader: {header}\npayload: {payload}")
        response = requests.request("POST", url=url, headers=header, data=payload)
        log_request(f"Vend Insurance Response:\nresponse: {response.text}")
        return response.json()
