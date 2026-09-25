import os
import threading

from chatbot_pluviometrico.main import rodarzap
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

TARGET_GROUP_ID = os.getenv('TARGET_GROUP_ID')
TARGET_MENTIONED_JID = os.getenv('TARGET_MENTIONED_JID')


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)

        if not data:
            return jsonify({"status": "ok"}), 200

        if data.get('event') != 'messages.upsert':
            return jsonify({"status": "ok"}), 200

        msg_data = data.get('data', {})
        key = msg_data.get('key', {})
        remote_jid = key.get('remoteJid')

        if remote_jid != TARGET_GROUP_ID:
            return jsonify({"status": "ok"}), 200

        context_info = msg_data.get('contextInfo', {})
        mentioned_jids = context_info.get('mentionedJid', [])

        if TARGET_MENTIONED_JID not in mentioned_jids:
            return jsonify({"status": "ok"}), 200

        message_content = msg_data.get('message') or {}
        text_msg = (
            message_content.get('conversation') or
            message_content.get('extendedTextMessage', {}).get('text', '')
        )

        if not text_msg:
            return jsonify({"status": "ok"}), 200

        print(f"✅ Trigger detectado — grupo: {remote_jid}")
        print(f"📩 Mensagem: {text_msg}")

        thread = threading.Thread(target=rodarzap, args=(text_msg, remote_jid), daemon=True)
        thread.start()

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
