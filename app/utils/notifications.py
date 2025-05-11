import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import uuid
from collections import defaultdict
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

def check_and_notify_limit(user, expenses_today, daily_limit):
    print("INSIDE1 check_and_notify_limit")
    print("expenses_today: ",expenses_today)
    total = sum(exp.amount for exp in expenses_today)
    print("TOTAL: ", total)
    print("DAILY_LIMIT: ",daily_limit)
    if total > daily_limit:
        pie_chart_path = generate_pie_chart(expenses_today)
        send_limit_exceeded_email(user.email, user.username, pie_chart_path, total, daily_limit)

def generate_pie_chart(expense_data):
    print("INSIDE generate_pie_chart")

    # Combine amounts by category
    category_totals = defaultdict(float)
    for exp in expense_data:
        category_totals[exp.category] += exp.amount

    labels = list(category_totals.keys())
    sizes = list(category_totals.values())

    # Plot
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')

    # Save to file
    output_dir = os.path.join(os.path.dirname(__file__), "..", "temp")
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"chart_{uuid.uuid4()}.png")
    plt.savefig(filename)
    plt.close()

    return filename

def send_limit_exceeded_email(to_email: str, username: str, pie_chart_path: str, total: float, daily_limit: float):
    print("INSIDE send_limit_exceeded_email")

    subject = "⚠️ Daily Expense Limit Exceeded"
    plain_text = f"""
    Hi {username},

    Your daily expenditure exceeded your limit.
    You spent ₹{total:.2f}, but your limit is ₹{daily_limit:.2f}.

    I know you only spend when necessary, but it's better to control your expenses.

    Stay mindful!
    """

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = 'yarraguntakulasekharreddy@gmail.com'
    msg['To'] = to_email
    msg.set_content(plain_text)

    # Create a CID for the inline image
    cid = make_msgid(domain='xyz.com')  # domain doesn't matter here

    # Add HTML content referencing the inline image by its CID
    html_content = f"""
    <html>
        <body>
            <p>Hi {username},</p>
            <p>Your daily expenditure exceeded your limit.</p>
            <p>You spent ₹{total:.2f}, but your limit is ₹{daily_limit:.2f}.</p>
            <p>I know you only spend when necessary, but it's better to control your expenses.</p>
            <p><b>Stay mindful!</b></p>
            <p><img src="cid:{cid[1:-1]}" alt="Pie Chart" style="width:400px;"></p>
        </body>
    </html>
    """
    msg.add_alternative(html_content, subtype='html')

    # Attach the image with the matching CID
    if os.path.exists(pie_chart_path):
        with open(pie_chart_path, 'rb') as img:
            msg.get_payload()[1].add_related(
                img.read(),
                maintype='image',
                subtype='png',
                cid=cid
            )

    # Send email using Gmail SMTP
    try:
        print("INSIDE SMTP TRY")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('yarraguntakulasekharreddy@gmail.com', 'kymm hlvn qtuc igzt')  # Use Gmail App Password
            smtp.send_message(msg)
        print("Email with inline chart sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        if os.path.exists(pie_chart_path):
            os.remove(pie_chart_path)
            print(f"Deleted pie chart: {pie_chart_path}")
