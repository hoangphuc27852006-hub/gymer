# 🏋️ GYM FIT — Hệ Thống Quản Lý Phòng Gym

Web app quản lý phòng gym full-stack với Python Flask + SQLite.

---

## 🚀 Chạy Local (máy tính cá nhân)

### Yêu cầu
- Python 3.10+
- pip

### Các bước

```bash
# 1. Cài đặt thư viện
pip install -r requirements.txt

# 2. Chạy ứng dụng (DB sẽ tự tạo và seed data)
py -3 app.py        # Windows
# hoặc
python3 app.py      # Mac/Linux
```

Truy cập: **http://127.0.0.1:5000**

### Tài khoản mặc định

| Vai trò | Tên đăng nhập | Mật khẩu |
|---|---|---|
| Admin | `admin` | `admin123` |
| Nhân viên lễ tân | `letan` | `letan123` |
| PT | `pt_hung` | `pt123` |
| PT | `pt_mai` | `pt123` |
| Hội viên | `hv_an` | `hv123` |
| Hội viên | `hv_binh` | `hv123` |

---

## ☁️ Deploy lên Render.com (MIỄN PHÍ)

### Bước 1: Tạo repository GitHub

```bash
git init
git add .
git commit -m "Initial commit - Gym Management System"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

### Bước 2: Đăng ký Render.com

1. Truy cập [render.com](https://render.com) → Sign up (miễn phí)
2. Click **New +** → **Web Service**
3. Kết nối GitHub repository của bạn

### Bước 3: Cấu hình

| Trường | Giá trị |
|---|---|
| **Name** | gym-management (tùy chọn) |
| **Language** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && py -3 -c "from app import app; from database import init_db; init_db(app)"` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT` |

### Bước 4: Environment Variables

Thêm trong phần **Environment**:
```
SECRET_KEY = [nhập bất kỳ chuỗi ngẫu nhiên dài]
```

### Bước 5: Deploy

Click **Create Web Service** → chờ ~2-3 phút → nhận link web trực tiếp từ Render!

> ⚠️ **Lưu ý về SQLite trên Render Free Tier:**  
> Render free tier dùng ephemeral filesystem — database SQLite sẽ bị reset khi service restart.  
> Để dữ liệu bền vững, nâng cấp lên Render Paid hoặc chuyển sang PostgreSQL.

---

## 📋 Tính năng

### Quản lý Hội viên
- ✅ Thêm/sửa thông tin hội viên
- ✅ Theo dõi chỉ số cơ thể (chiều cao, cân nặng, % mỡ, vòng eo)
- ✅ Lịch sử check-in/out

### Quản lý Gói tập
- ✅ Danh mục gói tập (tháng, quý, năm...)
- ✅ Đăng kí gói, kích hoạt, theo dõi hết hạn
- ✅ Cảnh báo gói sắp hết hạn

### Check-in / Check-out
- ✅ Check-in nhanh bằng số điện thoại
- ✅ Check-in thủ công qua dropdown
- ✅ Xem danh sách đang trong phòng theo thời gian thực

### Lớp học & Buổi học
- ✅ Quản lý loại lớp (Yoga, Zumba, Gym...)
- ✅ Tạo lớp học với lịch cố định
- ✅ **Tự động tạo buổi học đến hết khóa**
- ✅ Đăng kí hội viên vào buổi học
- ✅ Giới hạn sức chứa theo phòng

### Huấn luyện viên & Buổi PT
- ✅ Quản lý thông tin PT
- ✅ Đặt lịch buổi PT 1-1
- ✅ Theo dõi trạng thái: đã lên lịch, hoàn thành, vắng mặt, hủy
- ✅ Tự động trừ buổi PT còn lại trong gói

### Nhân viên
- ✅ Quản lý thông tin nhân viên (Admin only)

### Tài khoản & Phân quyền
- ✅ 4 vai trò: Admin, Nhân viên, PT, Hội viên
- ✅ Tạo/xóa tài khoản, reset mật khẩu
- ✅ Khóa/mở khóa tài khoản

### Phòng tập
- ✅ Quản lý phòng, sức chứa, trạng thái bảo trì

---

## 🗄️ Cơ sở dữ liệu

15 bảng theo phân tích hệ thống:

```
hoi_vien → chi_so_co_the, checkin_out, dang_ki_goi, dang_ki_buoi_hoc, buoi_pt, tai_khoan
goi_tap → dang_ki_goi
loai_lop → lop_hoc
phong_tap → lop_hoc
pt → lop_hoc, buoi_pt, tai_khoan
lop_hoc → buoi_hoc
buoi_hoc → dang_ki_buoi_hoc
nhan_vien → tai_khoan
```

---

## 🔧 Tech Stack

- **Backend**: Python 3 + Flask 3.0
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Auth**: Flask-Login + Werkzeug password hashing
- **DB**: SQLite (local) 
- **Frontend**: Bootstrap 5.3 + Font Awesome 6 + Chart.js
- **Deploy**: Gunicorn + Render.com
