FROM python:3.11-slim
WORKDIR /app
RUN apt-get update
RUN apt-get install -y gcc default-libmysqlclient-dev pkg-config xvfb
RUN apt-get install -y wget libxkbcommon0 libxrandr2 xdg-utils libu2f-udev libvulkan1 libxdamage1 libgtk-4-1 libnspr4 libnss3 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 fonts-liberation libasound2 libcurl4
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn","OzonParseApp.wsgi:application","--bind","0:8000"]