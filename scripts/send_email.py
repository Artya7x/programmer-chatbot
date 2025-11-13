import smtplib

def send_email(user_email: str, chatbot_decision: str, user_name: str):
    organization_email = "panagiotisp124@gmail.com"
    password = "xijq jywo bhrl vjgs"

    if chatbot_decision == "1":
        message = f"""Subject: Application Update – Interview Outcome

Dear {user_name},

Thank you for participating in our HR Chat-Bot interview.

We are pleased to inform you that you have successfully passed the evaluation.
Our team was impressed with your responses and believes you may be a strong fit
for the available role.

You will receive a follow-up email shortly with details about the next steps
in the recruitment process.

Best regards,
HR Department
"""
    else:
        message = f"""Subject: Application Update – Interview Outcome

Dear {user_name},

Thank you for taking the time to complete our HR Chat-Bot interview.

After reviewing your responses, we regret to inform you that you were not
selected to proceed to the next stage of the recruitment process.

We appreciate your interest in the position and encourage you to apply again
in the future.

Kind regards,
HR Department
"""

    with smtplib.SMTP('smtp.gmail.com', 587) as connection:
        connection.starttls()
        connection.login(user=organization_email, password=password)
        connection.sendmail(
            from_addr=organization_email,
            to_addrs=user_email,
            msg=message.encode("utf-8")
        )
