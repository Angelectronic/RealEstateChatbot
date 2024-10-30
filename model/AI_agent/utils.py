def convert_price_to_text(price):
    try:
        if price < 1000000000:
            return f"{int(price / 1000000)} triệu"
        else:
            return f"{price / 1000000000} tỷ"
    except:
        return price