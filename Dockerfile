FROM python:3.9-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tạo các thư mục cần thiết
RUN mkdir -p data/image-member \
    static/images/avatars \
    static/images/banners \
    static/images/events \
    static/images/members \
    static/images/projects

# Copy source code và data
COPY app app/
COPY controllers controllers/
COPY models models/
COPY migrations migrations/
COPY *.py ./

# Đảm bảo các thư mục có quyền ghi
RUN chmod -R 777 /app/data
RUN chmod -R 777 /app/static

# Expose port
EXPOSE 5000

# Chạy server
CMD ["flask", "run", "--host=0.0.0.0"] 