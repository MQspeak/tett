from flask import Flask, request, jsonify
import requests, io
from PIL import Image

app = Flask(__name__)

APP_ID = "cli_a8caa195e2b6500d"
APP_SECRET = "x5IdOTQR3NiaKpXUfBFTfepvIQmBuven"
APP_TOKEN = "FvQSbItv8a8oAYs0S4Oc7gUDn2g"
TABLE_ID = "tblkZPRuBfrmugNf"

def get_feishu_access_token():
	url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
	resp = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
	return resp.json()["tenant_access_token"]

def download_image(image_url):
	resp = requests.get(image_url, stream=True)
	img_bytes = io.BytesIO(resp.content)
	img_bytes.seek(0)
	img = Image.open(img_bytes)
	img_format = img.format.lower()
	img_bytes.seek(0)
	return img_bytes, img_format

def upload_to_feishu(img_bytes, img_format, token):
	url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
	headers = {"Authorization": f"Bearer {token}"}
	files = {"file": (f"image.{img_format}", img_bytes, f"image/{img_format}")}
	data = {
		"file_name": f"image.{img_format}",
		"parent_type": "bitable_file",
		"parent_node": APP_TOKEN,
		"size": str(len(img_bytes.getvalue()))
	}
	resp = requests.post(url, headers=headers, files=files, data=data)
	return resp.json()["data"]["file_token"]

def update_bitable_field(token, file_token, record_id=None):
	method = "PUT" if record_id else "POST"
	url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
	if record_id:
		url += f"/{record_id}"

	headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
	data = {"fields": {"附件": [{"file_token": file_token}]}}
	resp = requests.request(method, url, headers=headers, json=data)
	return resp.json()

@app.route("/api/upload", methods=["GET"])
def upload_handler():
	image_url = request.args.get("image_url")
	record_id = request.args.get("record_id", None)

	if not image_url:
		return jsonify({"error": "Missing image_url"}), 400

	try:
		token = get_feishu_access_token()
		img_bytes, img_format = download_image(image_url)
		file_token = upload_to_feishu(img_bytes, img_format, token)
		result = update_bitable_field(token, file_token, record_id)
		return jsonify({"success": True, "result": result})
	except Exception as e:
		return jsonify({"error": str(e)}), 500
