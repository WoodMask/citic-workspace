import smtplib
import os
import sys
import json
import argparse
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_default_body():
    return f"""您好！

附件为工作文件，请查收。

发送时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

如有问题，请随时联系。
"""

def expand_attachments(attachment_patterns):
    files = []
    for pattern in attachment_patterns:
        if os.path.isabs(pattern):
            matched = glob.glob(pattern)
        else:
            matched = glob.glob(pattern)
        
        if matched:
            files.extend(matched)
        elif os.path.exists(pattern):
            files.append(pattern)
        else:
            print(f"警告: 文件不存在 - {pattern}")
    return list(set(files))

def send_email(attachments, content, subject):
    config = load_config()
    
    sender = config["sender"]
    receiver = config["receiver"]
    auth_code = config["auth_code"]
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    
    if not subject:
        subject = config.get("default_subject", "工作文件发送")
    
    if not content:
        content = get_default_body()
    
    print("=" * 50)
    print("发送邮件")
    print("=" * 50)
    print(f"发件人: {sender}")
    print(f"收件人: {receiver}")
    print(f"主题: {subject}")
    print(f"附件数量: {len(attachments)}")
    print("-" * 50)
    
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "plain", "utf-8"))
    
    total_size = 0
    for filepath in attachments:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            total_size += size
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as f:
                part = MIMEApplication(f.read())
            part.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(part)
            print(f"已添加附件: {filename} ({size / 1024:.1f} KB)")
        else:
            print(f"警告: 文件不存在 - {filepath}")
    
    if total_size > 50 * 1024 * 1024:
        print("警告: 附件总大小超过50MB，可能发送失败")
    
    print("-" * 50)
    print("正在发送邮件...")
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender, auth_code)
            server.sendmail(sender, receiver, msg.as_string())
        print("=" * 50)
        print("邮件发送成功!")
        print(f"收件人: {receiver}")
        print("=" * 50)
        return True
    except smtplib.SMTPAuthenticationError:
        print("错误: 授权码验证失败，请检查授权码是否正确")
        return False
    except smtplib.SMTPRecipientsRefused:
        print("错误: 收件人地址被拒绝")
        return False
    except smtplib.SMTPException as e:
        print(f"错误: 发送失败 - {e}")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="发送邮件到公司邮箱")
    parser.add_argument("--attachments", "-a", nargs="*", default=[], help="附件文件路径")
    parser.add_argument("--content", "-c", default=None, help="邮件正文内容")
    parser.add_argument("--subject", "-s", default=None, help="邮件标题")
    
    args = parser.parse_args()
    
    attachments = expand_attachments(args.attachments) if args.attachments else []
    
    success = send_email(attachments, args.content, args.subject)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()