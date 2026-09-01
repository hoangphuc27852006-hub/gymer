from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date

db = SQLAlchemy()

# ─────────────────────────────────────────────
# Nhóm 1: Quản lý khách hàng
# ─────────────────────────────────────────────

class HoiVien(db.Model):
    __tablename__ = 'hoi_vien'
    ma_hv        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ho_ten       = db.Column(db.String(100), nullable=False)
    sdt          = db.Column(db.String(15))
    dia_chi      = db.Column(db.String(200))
    cccd         = db.Column(db.String(20), unique=True)
    gioi_tinh    = db.Column(db.String(5))   # Nam / Nữ
    ngay_sinh    = db.Column(db.Date)
    trang_thai   = db.Column(db.String(20), default='active')  # active / inactive

    # Relationships
    checkins       = db.relationship('CheckinOut',      backref='hoi_vien', lazy='dynamic', cascade='all, delete-orphan')
    chi_so_list    = db.relationship('ChiSoCoThe',      backref='hoi_vien', lazy='dynamic', cascade='all, delete-orphan')
    dang_ki_gois   = db.relationship('DangKiGoi',       backref='hoi_vien', lazy='dynamic', cascade='all, delete-orphan')
    dang_ki_buois  = db.relationship('DangKiBuoiHoc',   backref='hoi_vien', lazy='dynamic', cascade='all, delete-orphan')
    buoi_pt_list   = db.relationship('BuoiPT',          backref='hoi_vien', lazy='dynamic', cascade='all, delete-orphan')
    tai_khoan      = db.relationship('TaiKhoan',         backref='hoi_vien', uselist=False,  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<HoiVien {self.ma_hv}: {self.ho_ten}>'

    @property
    def goi_hien_tai(self):
        """Trả về gói đang active hiện tại (nếu có)."""
        from datetime import date
        return self.dang_ki_gois.filter_by(trang_thai='active').first()

    @property
    def dang_checkin(self):
        """Kiểm tra hội viên có đang trong phòng tập không."""
        return self.checkins.filter(CheckinOut.thoi_gian_checkout == None).first()


class ChiSoCoThe(db.Model):
    __tablename__ = 'chi_so_co_the'
    ma_lan_do      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_hv          = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=False)
    ngay_do        = db.Column(db.Date, nullable=False, default=date.today)
    phan_tram_mo   = db.Column(db.Float)
    chieu_cao      = db.Column(db.Float)   # cm
    can_nang       = db.Column(db.Float)   # kg
    vong_eo        = db.Column(db.Float)   # cm
    ghi_chu        = db.Column(db.Text)

    def __repr__(self):
        return f'<ChiSo HV={self.ma_hv} ngay={self.ngay_do}>'


class CheckinOut(db.Model):
    __tablename__ = 'checkin_out'
    ma_luot            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_hv              = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=False)
    thoi_gian_checkin  = db.Column(db.DateTime, nullable=False, default=datetime.now)
    thoi_gian_checkout = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<CheckIn HV={self.ma_hv} in={self.thoi_gian_checkin}>'


# ─────────────────────────────────────────────
# Nhóm 2: Quản lý kinh doanh
# ─────────────────────────────────────────────

class GoiTap(db.Model):
    __tablename__ = 'goi_tap'
    ma_goi       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_goi      = db.Column(db.String(100), nullable=False)
    thoi_han_goi = db.Column(db.Integer, nullable=False)  # số ngày
    gia_tien     = db.Column(db.Float, nullable=False)
    so_buoi_pt   = db.Column(db.Integer, default=0)
    trang_thai   = db.Column(db.String(20), default='active')  # active / inactive

    dang_ki_gois = db.relationship('DangKiGoi', backref='goi_tap', lazy='dynamic')

    def __repr__(self):
        return f'<GoiTap {self.ma_goi}: {self.ten_goi}>'


class DangKiGoi(db.Model):
    __tablename__ = 'dang_ki_goi'
    ma_dk_goi          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_hv              = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=False)
    ma_goi             = db.Column(db.Integer, db.ForeignKey('goi_tap.ma_goi'), nullable=False)
    ngay_dang_ki       = db.Column(db.Date, nullable=False, default=date.today)
    ngay_bat_dau       = db.Column(db.Date)
    ngay_het_han       = db.Column(db.Date)
    so_buoi_pt_con_lai = db.Column(db.Integer, default=0)
    trang_thai         = db.Column(db.String(20), default='waiting')
    # waiting / active / expired

    def __repr__(self):
        return f'<DangKiGoi HV={self.ma_hv} Goi={self.ma_goi}>'


# ─────────────────────────────────────────────
# Nhóm 3: Quản lý lớp học và dịch vụ PT
# ─────────────────────────────────────────────

class LoaiLop(db.Model):
    __tablename__ = 'loai_lop'
    ma_loai    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_loai   = db.Column(db.String(100), nullable=False)
    don_gia_pt = db.Column(db.Float, default=0)
    trang_thai = db.Column(db.String(20), default='active')  # active / inactive

    lop_hoc_list = db.relationship('LopHoc', backref='loai_lop', lazy='dynamic')

    def __repr__(self):
        return f'<LoaiLop {self.ma_loai}: {self.ten_loai}>'


class PhongTap(db.Model):
    __tablename__ = 'phong_tap'
    ma_phong   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_phong  = db.Column(db.String(100), nullable=False)
    vi_tri     = db.Column(db.String(200))
    suc_chua   = db.Column(db.Integer, default=20)
    trang_thai = db.Column(db.String(20), default='active')  # active / maintenance

    lop_hoc_list = db.relationship('LopHoc', backref='phong_tap', lazy='dynamic')

    def __repr__(self):
        return f'<PhongTap {self.ma_phong}: {self.ten_phong}>'


class PT(db.Model):
    __tablename__ = 'pt'
    ma_pt              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ho_ten             = db.Column(db.String(100), nullable=False)
    cccd               = db.Column(db.String(20), unique=True)
    sdt                = db.Column(db.String(15))
    ngay_sinh          = db.Column(db.Date)
    so_nam_kinh_nghiem = db.Column(db.Integer, default=0)
    chuyen_mon         = db.Column(db.String(200))
    luong_co_ban       = db.Column(db.Float, default=0)
    trang_thai         = db.Column(db.String(20), default='active')
    # active / nghi_phep / da_nghi

    lop_hoc_list = db.relationship('LopHoc',  backref='pt', lazy='dynamic')
    buoi_pt_list = db.relationship('BuoiPT',  backref='pt', lazy='dynamic')
    tai_khoan    = db.relationship('TaiKhoan', backref='pt', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PT {self.ma_pt}: {self.ho_ten}>'


class LopHoc(db.Model):
    __tablename__ = 'lop_hoc'
    ma_lop        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_lop       = db.Column(db.String(150), nullable=False)
    thu_hoc       = db.Column(db.String(20))   # VD: "2,4,6" (thứ 2,4,6)
    gio_bat_dau   = db.Column(db.Time)
    gio_ket_thuc  = db.Column(db.Time)
    ngay_bat_dau  = db.Column(db.Date)
    ngay_ket_thuc = db.Column(db.Date)
    trang_thai    = db.Column(db.String(20), default='open')
    # open / full / closed

    ma_loai  = db.Column(db.Integer, db.ForeignKey('loai_lop.ma_loai'), nullable=False)
    ma_phong = db.Column(db.Integer, db.ForeignKey('phong_tap.ma_phong'), nullable=False)
    ma_pt    = db.Column(db.Integer, db.ForeignKey('pt.ma_pt'), nullable=False)

    buoi_hoc_list = db.relationship('BuoiHoc', backref='lop_hoc', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LopHoc {self.ma_lop}: {self.ten_lop}>'

    @property
    def thu_hoc_display(self):
        """Chuyển "2,4,6" thành "Thứ 2, Thứ 4, Thứ 6"."""
        if not self.thu_hoc:
            return ''
        days = {'2': 'Thứ 2', '3': 'Thứ 3', '4': 'Thứ 4',
                '5': 'Thứ 5', '6': 'Thứ 6', '7': 'Thứ 7', '8': 'CN'}
        return ', '.join(days.get(d.strip(), d.strip()) for d in self.thu_hoc.split(','))


class BuoiHoc(db.Model):
    __tablename__ = 'buoi_hoc'
    ma_buoi    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_lop     = db.Column(db.Integer, db.ForeignKey('lop_hoc.ma_lop'), nullable=False)
    ngay_hoc   = db.Column(db.Date, nullable=False)
    trang_thai = db.Column(db.String(20), default='upcoming')
    # upcoming / ongoing / completed / cancelled

    dang_ki_list = db.relationship('DangKiBuoiHoc', backref='buoi_hoc', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<BuoiHoc Lop={self.ma_lop} ngay={self.ngay_hoc}>'

    @property
    def so_dang_ky(self):
        return self.dang_ki_list.filter_by(trang_thai='confirmed').count()

    @property
    def con_cho(self):
        suc_chua = self.lop_hoc.phong_tap.suc_chua if self.lop_hoc and self.lop_hoc.phong_tap else 999
        return suc_chua - self.so_dang_ky


class DangKiBuoiHoc(db.Model):
    __tablename__ = 'dang_ki_buoi_hoc'
    ma_dk_buoi      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_hv           = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=False)
    ma_buoi         = db.Column(db.Integer, db.ForeignKey('buoi_hoc.ma_buoi'), nullable=False)
    thoi_gian_dk    = db.Column(db.DateTime, nullable=False, default=datetime.now)
    trang_thai      = db.Column(db.String(20), default='confirmed')
    # confirmed / pending / cancelled

    __table_args__ = (
        db.UniqueConstraint('ma_hv', 'ma_buoi', name='uq_hv_buoi'),
    )

    def __repr__(self):
        return f'<DangKiBuoiHoc HV={self.ma_hv} Buoi={self.ma_buoi}>'


class BuoiPT(db.Model):
    __tablename__ = 'buoi_pt'
    ma_buoi_pt         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_hv              = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=False)
    ma_pt              = db.Column(db.Integer, db.ForeignKey('pt.ma_pt'), nullable=False)
    thoi_gian_dat      = db.Column(db.DateTime, nullable=False, default=datetime.now)
    thoi_gian_bat_dau  = db.Column(db.DateTime)
    thoi_gian_ket_thuc = db.Column(db.DateTime)
    thoi_gian_huy      = db.Column(db.DateTime)
    don_gia_pt         = db.Column(db.Float)
    thoi_luong         = db.Column(db.Integer)  # phút
    trang_thai         = db.Column(db.String(20), default='scheduled')
    # scheduled / completed / absent / cancelled

    def __repr__(self):
        return f'<BuoiPT HV={self.ma_hv} PT={self.ma_pt}>'


# ─────────────────────────────────────────────
# Nhóm 4: Quản lý nhân sự và hệ thống
# ─────────────────────────────────────────────

class NhanVien(db.Model):
    __tablename__ = 'nhan_vien'
    ma_nv        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ho_ten       = db.Column(db.String(100), nullable=False)
    cccd         = db.Column(db.String(20), unique=True)
    ngay_sinh    = db.Column(db.Date)
    sdt          = db.Column(db.String(15))
    ngay_vao_lam = db.Column(db.Date)
    luong_co_ban = db.Column(db.Float, default=0)
    chuc_vu      = db.Column(db.String(50))
    trang_thai   = db.Column(db.String(20), default='active')  # active / inactive

    tai_khoan = db.relationship('TaiKhoan', backref='nhan_vien', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<NhanVien {self.ma_nv}: {self.ho_ten}>'


class TaiKhoan(db.Model, UserMixin):
    __tablename__ = 'tai_khoan'
    ma_tk         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ten_dang_nhap = db.Column(db.String(50), unique=True, nullable=False)
    mat_khau      = db.Column(db.String(200), nullable=False)
    vai_tro       = db.Column(db.String(20), nullable=False)
    # admin / nhanvien / pt / hoivien
    trang_thai    = db.Column(db.String(20), default='active')  # active / blocked

    ma_hv = db.Column(db.Integer, db.ForeignKey('hoi_vien.ma_hv'), nullable=True, unique=True)
    ma_nv = db.Column(db.Integer, db.ForeignKey('nhan_vien.ma_nv'), nullable=True, unique=True)
    ma_pt = db.Column(db.Integer, db.ForeignKey('pt.ma_pt'), nullable=True, unique=True)

    def get_id(self):
        return str(self.ma_tk)

    def __repr__(self):
        return f'<TaiKhoan {self.ten_dang_nhap} ({self.vai_tro})>'

    @property
    def display_name(self):
        if self.vai_tro == 'hoivien' and self.hoi_vien:
            return self.hoi_vien.ho_ten
        elif self.vai_tro == 'pt' and self.pt:
            return self.pt.ho_ten
        elif self.vai_tro in ('admin', 'nhanvien') and self.nhan_vien:
            return self.nhan_vien.ho_ten
        return self.ten_dang_nhap

    def can_access(self, module):
        """Kiểm tra quyền truy cập module."""
        permissions = {
            'admin':     ['dashboard', 'members', 'packages', 'classes', 'trainers',
                          'staff', 'accounts', 'rooms', 'class_types', 'pt_sessions', 'checkin'],
            'nhanvien':  ['dashboard', 'members', 'packages', 'classes', 'rooms',
                          'class_types', 'pt_sessions', 'checkin'],
            'pt':        ['dashboard', 'pt_sessions', 'classes'],
            'hoivien':   ['dashboard', 'classes', 'pt_sessions'],
        }
        return module in permissions.get(self.vai_tro, [])
