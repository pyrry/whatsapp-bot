from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import re

app = Flask(__name__)

# 存储地址的文件
ADDRESS_FILE = "addresses.json"

def load_addresses():
    try:
        with open(ADDRESS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_addresses(addresses):
    with open(ADDRESS_FILE, "w") as file:
        json.dump(addresses, file, indent=4)

def is_valid_crypto_address(address):
    return bool(re.match(r"^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$", address))  # 仅示例比特币地址格式

addresses = load_addresses()

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")
    
    resp = MessagingResponse()
    reply = resp.message()
    
    if incoming_msg.lower() == "清空":
        addresses.pop(sender, None)
        save_addresses(addresses)
        reply.body("✅ 你的地址记录已清空。")
    elif sender in addresses:
        if incoming_msg in addresses[sender]:
            reply.body("✅ 地址已确认，与之前存储的地址匹配。")
        else:
            reply.body("⚠️ 警告：当前地址与之前存储的地址不匹配！")
    else:
        if is_valid_crypto_address(incoming_msg):
            if sender not in addresses:
                addresses[sender] = []
            addresses[sender].append(incoming_msg)
            save_addresses(addresses)
            reply.body("📌 地址已存储，下次发送相同地址时将自动确认。")
        else:
            reply.body("❌ 无效的加密货币地址，请检查输入。")
    
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
