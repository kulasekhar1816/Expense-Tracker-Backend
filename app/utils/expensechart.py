import matplotlib.pyplot as plt
from io import BytesIO
import base64

def create_pie_chart(expense_data):
    labels = [item['category'] for item in expense_data]
    sizes = [item['amount'] for item in expense_data]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf
