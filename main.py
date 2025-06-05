import requests
import io
from PIL import Image

# 飞书应用凭证
APP_ID = "cli_a8caa195e2b6500d"
APP_SECRET = "x5IdOTQR3NiaKpXUfBFTfepvIQmBuven"

# 多维表格信息
APP_TOKEN = "FvQSbItv8a8oAYs0S4Oc7gUDn2g"
TABLE_ID = "tblkZPRuBfrmugNf"


# 1. 获取飞书访问令牌
def get_feishu_access_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("tenant_access_token")
    else:
        raise Exception(f"获取access_token失败: {response.text}")


# 2. 下载图片
def download_image(image_url):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            # 将图片内容转换为bytes
            image_bytes = io.BytesIO()
            for chunk in response.iter_content(1024):
                image_bytes.write(chunk)
            image_bytes.seek(0)

            # 获取图片格式
            image = Image.open(image_bytes)
            format = image.format.lower()

            # 重置指针
            image_bytes.seek(0)
            return image_bytes, format
        else:
            raise Exception(f"下载图片失败，HTTP状态码: {response.status_code}")
    except Exception as e:
        raise Exception(f"下载图片时出错: {str(e)}")


# 3. 上传图片到飞书并获得file_token
def upload_to_feishu(image_bytes, image_format, access_token):
    url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    files = {
        "file": (f"image.{image_format}", image_bytes, f"image/{image_format}")
    }
    data = {
        "file_name": f"image.{image_format}",
        "parent_type": "bitable_file",
        "parent_node": APP_TOKEN,
        "size": str(len(image_bytes.getvalue()))
    }

    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.json().get("data", {}).get("file_token")
    else:
        raise Exception(f"上传图片到飞书失败: {response.text}")


# 4. 将file_token写入多维表格的附件字段
def update_bitable_field(access_token, file_token, record_id=None):
    # 如果有record_id则是更新现有记录，否则是创建新记录
    if record_id:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records/{record_id}"
        method = "PUT"
    else:
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
        method = "POST"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 假设附件字段的field_name是"image"，请根据实际情况修改
    data = {
        "fields": {
            "附件": [{
                "file_token": file_token
            }]
        }
    }

    response = requests.request(method, url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"更新多维表格失败: {response.text}")


# 主函数
def main(image_url, record_id=None):
    try:
        # 1. 获取访问令牌
        access_token = get_feishu_access_token()
        print("获取access_token成功")

        # 2. 下载图片
        image_bytes, image_format = download_image(image_url)
        print(f"下载图片成功，格式: {image_format}")

        # 3. 上传到飞书
        file_token = upload_to_feishu(image_bytes, image_format, access_token)
        print(f"上传图片成功，file_token: {file_token}")

        # 4. 更新到多维表格
        result = update_bitable_field(access_token, file_token, record_id)
        print("更新多维表格成功")
        print(result)

        return True
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        return False


# 使用示例
if __name__ == "__main__":
    # 指定图片URL
    image_url = "http://sns-webpic-qc.xhscdn.com/202506050327/3c9b805edaf8ae8d415b39f88b856716/notes_pre_post/1040g3k831i910r7qnehg5or9tmq7qifdlob2b7o!nd_dft_wlteh_jpg_3"  # 替换为实际的图片URL

    # 如果要更新现有记录，提供record_id
    # record_id = "rec123456"  # 替换为实际的记录ID

    # 调用主函数
    main(image_url)  # 如果要更新现有记录，传入record_id参数