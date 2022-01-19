from datetime import datetime
from core.celeryapp import app


@app.task()
def otp_query(query):
    """
    task example
    :param query:
    :return:
    """
    with open('/tmp/a.txt', 'a') as f:
        f.write(str(datetime.now().strftime('%H:%M')))
        f.write(query)
        f.write('\n')
