import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# --- CONFIGURATION ---
sender_email = "odionkassim1001@gmail.com"
sender_password = "vwkq eihe pdxl ftqq"  # Not your login password! (See Step 3)
receiver_email = "alukomorolayo2016@gmail.com"

# --- EMAIL CONTENT ---
msg = MIMEMultipart('related')
msg['Subject'] = "ATM Analytics"
msg['From'] = f"Odion Kassim <{sender_email}>"
msg['To'] = receiver_email

# --- HTML BODY (The "Flyer" Layout) ---
html = f"""
<html>
  <body style="font-family: Calibri, Arial, sans-serif; color: #000; line-height: 1.5;">
    <div style="max-width: 700px;">
      
      <p> XYZ ATM Analytics Dashboard.</p>

      <div style="margin: 20px 0;">
        <img src="cid:flyer_img" style="width: 100%; border: 1px solid #eee;">
      </div>

      <p><b>Project Summary: ATM Analytics</b></p>
      <p>This task analyzes ATM withdrawal patterns between January and June from 2015 to 2017</p>
    </div>
  </body>
</html>
"""

msg.attach(MIMEText(html, 'html'))

# --- EMBED IMAGE ---
with open("flyer.png", 'rb') as f:
    img = MIMEImage(f.read())
    img.add_header('Content-ID', '<flyer_img>')
    msg.attach(img)

# --- SEND EMAIL ---
try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Flyer sent successfully!")
except Exception as e:
    print(f"Error: {e}")