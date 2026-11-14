FROM python:3.12
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --create-home app && chown app:app /app
USER app

CMD ["python", "parse_mail.py"]