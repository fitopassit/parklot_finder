FROM python:3.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
ENV PYTHONPATH "${PYTHONPATH}:/app/"
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements_bot.txt