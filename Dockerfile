FROM python:3.10

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r base.pip
RUN python manage.py collectstatic --noinput
# RUN pip install --no-cache-dir -r dev.pip

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
