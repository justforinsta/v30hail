import streamlit as st
import requests
import asyncio
import json
import time 

---------------------

CONSTANTS & STATE

---------------------

reason_labels = { "Spam": "1", "Self Injury": "2", "Drugs": "3", "Nudity": "4", "Violence": "5", "Hate Speech": "6", "Harassment": "7", "Impersonation (Insta)": "8", "Impersonation (Business)": "9", "Impersonation (Other)": "10", "Underage (<13)": "11", "Gun Sales": "12", "Violence (Type 1)": "13", "Violence (Type 4)": "14" }

---------------------

HELPER FUNCTIONS

---------------------

def get_user_id(username): try: r = requests.post( 'https://i.instagram.com/api/v1/users/lookup/', headers={ "Connection": "close", "X-IG-Connection-Type": "WIFI", "mid": "XOSINgABAAG1IDmaral3noOozrK0rrNSbPuSbzHq", "X-IG-Capabilities": "3R4=", "Accept-Language": "en-US", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": "Instagram 99.4.0 TweakPY_vv1ck", "Accept-Encoding": "gzip, deflate" }, data={"signed_body": f"rand_sig.{{"q":"{username}"}}"} ) return r.json().get("user_id") except: return None

def send_report(user_id, sessionid, csrftoken, reason): res = requests.post( f"https://i.instagram.com/users/{user_id}/flag/", headers={ "User-Agent": "Mozilla/5.0", "Host": "i.instagram.com", 'cookie': f"sessionid={sessionid}", "X-CSRFToken": csrftoken, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" }, data=f'source_name=&reason_id={reason}&frx_context=', allow_redirects=False ) return res.status_code

---------------------

STREAMLIT UI

---------------------

st.set_page_config(page_title="Instagram Reporter", layout="centered") st.title("📢 Instagram Multi-Report Tool")

with st.form("report_form"): session_id = st.text_input("🔐 Instagram Session ID", type="password") csrf_token = st.text_input("🔑 CSRF Token", type="password") targets = st.text_area("🎯 Target Usernames (comma-separated)") report_reason = st.selectbox("🚨 Report Reason", list(reason_labels.keys())) report_count = st.number_input("🔁 Reports per target", min_value=1, max_value=100, value=5) delay = st.slider("⏱️ Delay between reports (seconds)", min_value=1, max_value=30, value=5) submit = st.form_submit_button("🚀 Start Reporting")

if submit: if not session_id or not csrf_token or not targets: st.error("⚠️ Please fill in all required fields.") else: usernames = [u.strip() for u in targets.split(",") if u.strip()] reason_code = reason_labels[report_reason]

st.info(f"Starting reports for {len(usernames)} user(s)...")
    report_log = st.empty()
    log_lines = []

    for username in usernames:
        user_id = get_user_id(username)
        if not user_id:
            log_lines.append(f"❌ @{username} not found.")
            report_log.text("\n".join(log_lines))
            continue

        for i in range(1, report_count + 1):
            code = send_report(user_id, session_id, csrf_token, reason_code)
            if code in [200, 302]:
                log_lines.append(f"✅ @{username} report {i}/{report_count}")
            elif code == 429:
                log_lines.append(f"🚫 @{username} rate limited.")
                break
            else:
                log_lines.append(f"⚠️ @{username} unknown response: {code}")
            report_log.text("\n".join(log_lines))
            time.sleep(delay)

    st.success("🎉 Reporting complete!")

