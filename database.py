"""
database.py — Khởi tạo bảng và seed dữ liệu mẫu.
"""
from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
from models import (
    db, HoiVien, ChiSoCoThe, CheckinOut,
    GoiTap, DangKiGoi,
    LoaiLop, PhongTap, PT, LopHoc, BuoiHoc, DangKiBuoiHoc, BuoiPT,
    NhanVien, TaiKhoan
)


def init_db(app):
    with app.app_context():
        db.create_all()
        if TaiKhoan.query.count() == 0:
            seed_data()
        print("[OK] Database initialized.")


def seed_data():
    """Chèn dữ liệu mẫu vào database."""

    # ── Nhân viên ──────────────────────────────────────────
    nv_list = [
        NhanVien(ho_ten='Nguyễn Quản Lý', cccd='001085000001', ngay_sinh=date(1990, 5, 15),
                 sdt='0901000001', ngay_vao_lam=date(2022, 1, 1),
                 luong_co_ban=12_000_000, chuc_vu='Quản lý', trang_thai='active'),
        NhanVien(ho_ten='Trần Thị Lễ Tân', cccd='001085000002', ngay_sinh=date(1998, 8, 22),
                 sdt='0901000002', ngay_vao_lam=date(2023, 3, 1),
                 luong_co_ban=7_000_000, chuc_vu='Nhân viên lễ tân', trang_thai='active'),
    ]
    db.session.add_all(nv_list)
    db.session.flush()

    # ── PT ─────────────────────────────────────────────────
    pt_list = [
        PT(ho_ten='Lê Văn Hùng', cccd='001085001001', sdt='0912000001',
           ngay_sinh=date(1992, 3, 10), so_nam_kinh_nghiem=5,
           chuyen_mon='Gym cơ bản, Thể hình', luong_co_ban=10_000_000, trang_thai='active'),
        PT(ho_ten='Phạm Thị Mai', cccd='001085001002', sdt='0912000002',
           ngay_sinh=date(1995, 7, 20), so_nam_kinh_nghiem=4,
           chuyen_mon='Yoga, Pilates', luong_co_ban=9_000_000, trang_thai='active'),
        PT(ho_ten='Đỗ Minh Tuấn', cccd='001085001003', sdt='0912000003',
           ngay_sinh=date(1993, 11, 5), so_nam_kinh_nghiem=6,
           chuyen_mon='Zumba, Cardio', luong_co_ban=10_500_000, trang_thai='active'),
        PT(ho_ten='Nguyễn Thị Hoa', cccd='001085001004', sdt='0912000004',
           ngay_sinh=date(1996, 4, 14), so_nam_kinh_nghiem=3,
           chuyen_mon='Yoga, Thiền', luong_co_ban=8_500_000, trang_thai='active'),
        PT(ho_ten='Bùi Văn Dũng', cccd='001085001005', sdt='0912000005',
           ngay_sinh=date(1991, 9, 30), so_nam_kinh_nghiem=7,
           chuyen_mon='Thể hình, Powerlifting', luong_co_ban=11_000_000, trang_thai='active'),
    ]
    db.session.add_all(pt_list)
    db.session.flush()

    # ── Hội viên ───────────────────────────────────────────
    hv_list = [
        HoiVien(ho_ten='Trần Văn An', sdt='0933001001', dia_chi='123 Lê Lợi, Q.1',
                cccd='001085002001', gioi_tinh='Nam', ngay_sinh=date(1998, 1, 15), trang_thai='active'),
        HoiVien(ho_ten='Nguyễn Thị Bình', sdt='0933001002', dia_chi='45 Nguyễn Huệ, Q.1',
                cccd='001085002002', gioi_tinh='Nữ', ngay_sinh=date(2000, 6, 20), trang_thai='active'),
        HoiVien(ho_ten='Lê Thành Công', sdt='0933001003', dia_chi='78 Trần Hưng Đạo, Q.5',
                cccd='001085002003', gioi_tinh='Nam', ngay_sinh=date(1995, 3, 8), trang_thai='active'),
        HoiVien(ho_ten='Phạm Thị Dung', sdt='0933001004', dia_chi='12 Võ Văn Tần, Q.3',
                cccd='001085002004', gioi_tinh='Nữ', ngay_sinh=date(2001, 9, 25), trang_thai='active'),
        HoiVien(ho_ten='Đặng Minh Đức', sdt='0933001005', dia_chi='56 Hai Bà Trưng, Q.1',
                cccd='001085002005', gioi_tinh='Nam', ngay_sinh=date(1999, 12, 3), trang_thai='active'),
        HoiVien(ho_ten='Hoàng Thị Hương', sdt='0933001006', dia_chi='89 Đinh Tiên Hoàng, BT',
                cccd='001085002006', gioi_tinh='Nữ', ngay_sinh=date(1997, 4, 18), trang_thai='active'),
        HoiVien(ho_ten='Vũ Quốc Huy', sdt='0933001007', dia_chi='34 Cộng Hòa, TB',
                cccd='001085002007', gioi_tinh='Nam', ngay_sinh=date(2002, 7, 7), trang_thai='active'),
        HoiVien(ho_ten='Bùi Thị Lan', sdt='0933001008', dia_chi='67 Lý Thường Kiệt, Q.10',
                cccd='001085002008', gioi_tinh='Nữ', ngay_sinh=date(1994, 2, 14), trang_thai='active'),
        HoiVien(ho_ten='Ngô Văn Minh', sdt='0933001009', dia_chi='23 Nguyễn Trãi, Q.5',
                cccd='001085002009', gioi_tinh='Nam', ngay_sinh=date(1996, 11, 11), trang_thai='active'),
        HoiVien(ho_ten='Đinh Thị Ngọc', sdt='0933001010', dia_chi='10 Phan Đình Phùng, PN',
                cccd='001085002010', gioi_tinh='Nữ', ngay_sinh=date(2003, 5, 30), trang_thai='active'),
    ]
    db.session.add_all(hv_list)
    db.session.flush()

    # ── Gói tập ────────────────────────────────────────────
    goi_list = [
        GoiTap(ten_goi='Gói Tháng',  thoi_han_goi=30,  gia_tien=500_000,   so_buoi_pt=0,  trang_thai='active'),
        GoiTap(ten_goi='Gói Quý',    thoi_han_goi=90,  gia_tien=1_200_000, so_buoi_pt=4,  trang_thai='active'),
        GoiTap(ten_goi='Gói Nửa Năm',thoi_han_goi=180, gia_tien=2_000_000, so_buoi_pt=8,  trang_thai='active'),
        GoiTap(ten_goi='Gói Năm',    thoi_han_goi=365, gia_tien=3_500_000, so_buoi_pt=20, trang_thai='active'),
    ]
    db.session.add_all(goi_list)
    db.session.flush()

    # ── Đăng kí gói ────────────────────────────────────────
    today = date.today()
    dk_goi_list = [
        # HV 1 – Gói Quý, đang active
        DangKiGoi(ma_hv=hv_list[0].ma_hv, ma_goi=goi_list[1].ma_goi,
                  ngay_dang_ki=today - timedelta(30),
                  ngay_bat_dau=today - timedelta(30),
                  ngay_het_han=today + timedelta(60),
                  so_buoi_pt_con_lai=2, trang_thai='active'),
        # HV 2 – Gói Năm, đang active
        DangKiGoi(ma_hv=hv_list[1].ma_hv, ma_goi=goi_list[3].ma_goi,
                  ngay_dang_ki=today - timedelta(60),
                  ngay_bat_dau=today - timedelta(60),
                  ngay_het_han=today + timedelta(305),
                  so_buoi_pt_con_lai=16, trang_thai='active'),
        # HV 3 – Gói Tháng, đã hết hạn
        DangKiGoi(ma_hv=hv_list[2].ma_hv, ma_goi=goi_list[0].ma_goi,
                  ngay_dang_ki=today - timedelta(60),
                  ngay_bat_dau=today - timedelta(60),
                  ngay_het_han=today - timedelta(30),
                  so_buoi_pt_con_lai=0, trang_thai='expired'),
        # HV 3 – Gói Quý mới, đang active
        DangKiGoi(ma_hv=hv_list[2].ma_hv, ma_goi=goi_list[1].ma_goi,
                  ngay_dang_ki=today - timedelta(10),
                  ngay_bat_dau=today - timedelta(10),
                  ngay_het_han=today + timedelta(80),
                  so_buoi_pt_con_lai=4, trang_thai='active'),
        # HV 4 – Gói Tháng, chờ kích hoạt
        DangKiGoi(ma_hv=hv_list[3].ma_hv, ma_goi=goi_list[0].ma_goi,
                  ngay_dang_ki=today,
                  so_buoi_pt_con_lai=0, trang_thai='waiting'),
        # HV 5 – Gói Nửa Năm, active
        DangKiGoi(ma_hv=hv_list[4].ma_hv, ma_goi=goi_list[2].ma_goi,
                  ngay_dang_ki=today - timedelta(20),
                  ngay_bat_dau=today - timedelta(20),
                  ngay_het_han=today + timedelta(160),
                  so_buoi_pt_con_lai=7, trang_thai='active'),
    ]
    db.session.add_all(dk_goi_list)
    db.session.flush()

    # ── Phòng tập ───────────────────────────────────────────
    phong_list = [
        PhongTap(ten_phong='Phòng Gym Chính', vi_tri='Tầng 1', suc_chua=50, trang_thai='active'),
        PhongTap(ten_phong='Studio Yoga', vi_tri='Tầng 2', suc_chua=20, trang_thai='active'),
        PhongTap(ten_phong='Studio Dance', vi_tri='Tầng 2', suc_chua=25, trang_thai='active'),
    ]
    db.session.add_all(phong_list)
    db.session.flush()

    # ── Loại lớp ────────────────────────────────────────────
    loai_list = [
        LoaiLop(ten_loai='Yoga',       don_gia_pt=200_000, trang_thai='active'),
        LoaiLop(ten_loai='Zumba',      don_gia_pt=180_000, trang_thai='active'),
        LoaiLop(ten_loai='Gym cơ bản', don_gia_pt=250_000, trang_thai='active'),
    ]
    db.session.add_all(loai_list)
    db.session.flush()

    # ── Lớp học ─────────────────────────────────────────────
    lop_start = today
    lop_end   = today + timedelta(90)  # 3 tháng

    lop_list = [
        LopHoc(ten_lop='Yoga Sáng 2-4-6', thu_hoc='2,4,6',
               gio_bat_dau=datetime.strptime('07:00', '%H:%M').time(),
               gio_ket_thuc=datetime.strptime('08:00', '%H:%M').time(),
               ngay_bat_dau=lop_start, ngay_ket_thuc=lop_end,
               trang_thai='open', ma_loai=loai_list[0].ma_loai,
               ma_phong=phong_list[1].ma_phong, ma_pt=pt_list[1].ma_pt),
        LopHoc(ten_lop='Yoga Tối 3-5-7', thu_hoc='3,5,7',
               gio_bat_dau=datetime.strptime('19:00', '%H:%M').time(),
               gio_ket_thuc=datetime.strptime('20:00', '%H:%M').time(),
               ngay_bat_dau=lop_start, ngay_ket_thuc=lop_end,
               trang_thai='open', ma_loai=loai_list[0].ma_loai,
               ma_phong=phong_list[1].ma_phong, ma_pt=pt_list[3].ma_pt),
        LopHoc(ten_lop='Zumba Vui Vẻ 3-5', thu_hoc='3,5',
               gio_bat_dau=datetime.strptime('17:30', '%H:%M').time(),
               gio_ket_thuc=datetime.strptime('18:30', '%H:%M').time(),
               ngay_bat_dau=lop_start, ngay_ket_thuc=lop_end,
               trang_thai='open', ma_loai=loai_list[1].ma_loai,
               ma_phong=phong_list[2].ma_phong, ma_pt=pt_list[2].ma_pt),
        LopHoc(ten_lop='Gym Cơ Bản 2-4-6-7', thu_hoc='2,4,6,7',
               gio_bat_dau=datetime.strptime('06:00', '%H:%M').time(),
               gio_ket_thuc=datetime.strptime('07:30', '%H:%M').time(),
               ngay_bat_dau=lop_start, ngay_ket_thuc=lop_end,
               trang_thai='open', ma_loai=loai_list[2].ma_loai,
               ma_phong=phong_list[0].ma_phong, ma_pt=pt_list[0].ma_pt),
    ]
    db.session.add_all(lop_list)
    db.session.flush()

    # ── Tự động tạo buổi học ────────────────────────────────
    all_buoi = []
    for lop in lop_list:
        days = [int(d.strip()) for d in lop.thu_hoc.split(',')]
        cur = lop.ngay_bat_dau
        while cur <= lop.ngay_ket_thuc:
            # weekday(): Mon=0..Sun=6 → thứ python+2 = thứ VN
            weekday_vn = cur.weekday() + 2  # 2=Thứ 2 … 7=Thứ 7, 8=CN(Sun=6→8)
            if cur.weekday() == 6:
                weekday_vn = 8  # Chủ nhật = 8
            if weekday_vn in days:
                status = 'upcoming'
                if cur < today:
                    status = 'completed'
                elif cur == today:
                    status = 'ongoing'
                all_buoi.append(BuoiHoc(ma_lop=lop.ma_lop, ngay_hoc=cur, trang_thai=status))
            cur += timedelta(1)

    db.session.add_all(all_buoi)
    db.session.flush()

    # ── Đăng kí buổi học mẫu ────────────────────────────────
    dk_buoi_list = []
    # Lấy 5 buổi gần nhất (đã/đang diễn ra) của lớp 1
    buoi_lop1 = BuoiHoc.query.filter_by(ma_lop=lop_list[0].ma_lop)\
        .filter(BuoiHoc.trang_thai.in_(['completed', 'ongoing']))\
        .order_by(BuoiHoc.ngay_hoc.desc()).limit(5).all()
    for buoi in buoi_lop1:
        dk_buoi_list.append(DangKiBuoiHoc(
            ma_hv=hv_list[1].ma_hv, ma_buoi=buoi.ma_buoi,
            thoi_gian_dk=datetime.now() - timedelta(days=1),
            trang_thai='confirmed'))
    db.session.add_all(dk_buoi_list)
    db.session.flush()

    # ── Buổi PT mẫu ─────────────────────────────────────────
    buoi_pt_data = [
        BuoiPT(ma_hv=hv_list[0].ma_hv, ma_pt=pt_list[0].ma_pt,
               thoi_gian_dat=datetime.now() - timedelta(days=5),
               thoi_gian_bat_dau=datetime.now() - timedelta(days=4, hours=2),
               thoi_gian_ket_thuc=datetime.now() - timedelta(days=4, hours=1),
               don_gia_pt=250_000, thoi_luong=60, trang_thai='completed'),
        BuoiPT(ma_hv=hv_list[1].ma_hv, ma_pt=pt_list[1].ma_pt,
               thoi_gian_dat=datetime.now() - timedelta(days=2),
               thoi_gian_bat_dau=datetime.now() + timedelta(days=1, hours=2),
               thoi_gian_ket_thuc=datetime.now() + timedelta(days=1, hours=3),
               don_gia_pt=200_000, thoi_luong=60, trang_thai='scheduled'),
        BuoiPT(ma_hv=hv_list[2].ma_hv, ma_pt=pt_list[0].ma_pt,
               thoi_gian_dat=datetime.now() - timedelta(days=10),
               thoi_gian_bat_dau=datetime.now() - timedelta(days=9, hours=2),
               thoi_gian_ket_thuc=datetime.now() - timedelta(days=9, hours=1),
               don_gia_pt=250_000, thoi_luong=60, trang_thai='completed'),
    ]
    db.session.add_all(buoi_pt_data)
    db.session.flush()

    # ── Check-in mẫu ────────────────────────────────────────
    ci_list = []
    for i in range(5):
        ci_list.append(CheckinOut(
            ma_hv=hv_list[i].ma_hv,
            thoi_gian_checkin=datetime.now() - timedelta(days=i*2, hours=3),
            thoi_gian_checkout=datetime.now() - timedelta(days=i*2, hours=1)))
    db.session.add_all(ci_list)
    db.session.flush()

    # ── Chỉ số cơ thể mẫu ───────────────────────────────────
    cs_list = [
        ChiSoCoThe(ma_hv=hv_list[0].ma_hv, ngay_do=today - timedelta(60),
                   phan_tram_mo=22.5, chieu_cao=173, can_nang=75, vong_eo=85),
        ChiSoCoThe(ma_hv=hv_list[0].ma_hv, ngay_do=today - timedelta(30),
                   phan_tram_mo=21.0, chieu_cao=173, can_nang=73, vong_eo=83),
        ChiSoCoThe(ma_hv=hv_list[0].ma_hv, ngay_do=today,
                   phan_tram_mo=19.5, chieu_cao=173, can_nang=71, vong_eo=81),
        ChiSoCoThe(ma_hv=hv_list[1].ma_hv, ngay_do=today - timedelta(30),
                   phan_tram_mo=28.0, chieu_cao=160, can_nang=58, vong_eo=70),
        ChiSoCoThe(ma_hv=hv_list[1].ma_hv, ngay_do=today,
                   phan_tram_mo=26.5, chieu_cao=160, can_nang=56, vong_eo=68),
    ]
    db.session.add_all(cs_list)
    db.session.flush()

    # ── Tài khoản ────────────────────────────────────────────
    tk_list = [
        # Admin
        TaiKhoan(ten_dang_nhap='admin', vai_tro='admin', trang_thai='active',
                 mat_khau=generate_password_hash('admin123'),
                 ma_nv=nv_list[0].ma_nv),
        # Nhân viên
        TaiKhoan(ten_dang_nhap='letan', vai_tro='nhanvien', trang_thai='active',
                 mat_khau=generate_password_hash('letan123'),
                 ma_nv=nv_list[1].ma_nv),
        # PT
        TaiKhoan(ten_dang_nhap='pt_hung', vai_tro='pt', trang_thai='active',
                 mat_khau=generate_password_hash('pt123'),
                 ma_pt=pt_list[0].ma_pt),
        TaiKhoan(ten_dang_nhap='pt_mai', vai_tro='pt', trang_thai='active',
                 mat_khau=generate_password_hash('pt123'),
                 ma_pt=pt_list[1].ma_pt),
        # Hội viên
        TaiKhoan(ten_dang_nhap='hv_an', vai_tro='hoivien', trang_thai='active',
                 mat_khau=generate_password_hash('hv123'),
                 ma_hv=hv_list[0].ma_hv),
        TaiKhoan(ten_dang_nhap='hv_binh', vai_tro='hoivien', trang_thai='active',
                 mat_khau=generate_password_hash('hv123'),
                 ma_hv=hv_list[1].ma_hv),
    ]
    db.session.add_all(tk_list)
    db.session.commit()
    print("[OK] Seed data inserted successfully.")
    print("   Admin:    admin / admin123")
    print("   Le tan:   letan / letan123")
    print("   PT Hung:  pt_hung / pt123")
    print("   HV An:    hv_an / hv123")

