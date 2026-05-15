def format_phone(phone):

    if not phone:
        return ""

    phone=str(phone)

    if len(phone)!=11:
        return phone

    return f"{phone[:3]}****{phone[-4:]}"