from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from models import db, LopHoc, BuoiHoc, DangKiBuoiHoc, LoaiLop, PhongTap, PT, HoiVien

classes_bp = Blueprint('classes', __name__, template_folder='../templates')


def _staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


# ── Lớp học ──────────────────────────────────────────────────

@classes_bp.route('/')
@login_required
def index():
    q      = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    query  = LopHoc.query
    if q:
        query = query.filter(LopHoc.ten_lop.ilike(f'%{q}%'))
    if status:
        query = query.filter_by(trang_thai=status)
    lop_list = query.order_by(LopHoc.ma_lop.desc()).all()
    return render_template('classes/index.html', lop_list=lop_list, q=q, status=status)


@classes_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('classes.index'))

    loai_list  = LoaiLop.query.filter_by(trang_thai='active').all()
    phong_list = PhongTap.query.filter_by(trang_thai='active').all()
    pt_list    = PT.query.filter_by(trang_thai='active').all()

    if request.method == 'POST':
        ten_lop      = request.form.get('ten_lop', '').strip()
        thu_hoc      = ','.join(request.form.getlist('thu_hoc'))
        gio_bd_str   = request.form.get('gio_bat_dau', '')
        gio_kt_str   = request.form.get('gio_ket_thuc', '')
        ngay_bd_str  = request.form.get('ngay_bat_dau', '')
        ngay_kt_str  = request.form.get('ngay_ket_thuc', '')
        ma_loai      = int(request.form.get('ma_loai'))
        ma_phong     = int(request.form.get('ma_phong'))
        ma_pt        = int(request.form.get('ma_pt'))

        if not ten_lop or not thu_hoc:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
            return render_template('classes/add.html',
                                   loai_list=loai_list, phong_list=phong_list, pt_list=pt_list)

        try:
            gio_bd  = datetime.strptime(gio_bd_str, '%H:%M').time()
            gio_kt  = datetime.strptime(gio_kt_str, '%H:%M').time()
            ngay_bd = date.fromisoformat(ngay_bd_str)
            ngay_kt = date.fromisoformat(ngay_kt_str)
        except ValueError:
            flash('Ngày/giờ không hợp lệ.', 'danger')
            return render_template('classes/add.html',
                                   loai_list=loai_list, phong_list=phong_list, pt_list=pt_list)

        if ngay_kt < ngay_bd:
            flash('Ngày kết thúc phải sau ngày bắt đầu.', 'danger')
            return render_template('classes/add.html',
                                   loai_list=loai_list, phong_list=phong_list, pt_list=pt_list)

        lop = LopHoc(
            ten_lop=ten_lop, thu_hoc=thu_hoc,
            gio_bat_dau=gio_bd, gio_ket_thuc=gio_kt,
            ngay_bat_dau=ngay_bd, ngay_ket_thuc=ngay_kt,
            trang_thai='open',
            ma_loai=ma_loai, ma_phong=ma_phong, ma_pt=ma_pt
        )
        db.session.add(lop)
        db.session.flush()

        # Tự động tạo buổi học đến hết khóa
        count = _generate_sessions(lop)
        db.session.commit()
        flash(f'Tạo lớp "{ten_lop}" thành công với {count} buổi học!', 'success')
        return redirect(url_for('classes.detail', ma_lop=lop.ma_lop))

    return render_template('classes/add.html',
                           loai_list=loai_list, phong_list=phong_list, pt_list=pt_list)


@classes_bp.route('/<int:ma_lop>')
@login_required
def detail(ma_lop):
    lop  = LopHoc.query.get_or_404(ma_lop)
    page = request.args.get('page', 1, type=int)
    buoi_list = (lop.buoi_hoc_list
                 .order_by(BuoiHoc.ngay_hoc)
                 .paginate(page=page, per_page=20))
    today = date.today()
    return render_template('classes/detail.html', lop=lop, buoi_list=buoi_list, today=today)


@classes_bp.route('/<int:ma_lop>/edit', methods=['GET', 'POST'])
@login_required
def edit(ma_lop):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('classes.index'))

    lop        = LopHoc.query.get_or_404(ma_lop)
    loai_list  = LoaiLop.query.filter_by(trang_thai='active').all()
    phong_list = PhongTap.query.filter_by(trang_thai='active').all()
    pt_list    = PT.query.filter_by(trang_thai='active').all()

    if request.method == 'POST':
        lop.ten_lop    = request.form.get('ten_lop', lop.ten_lop).strip()
        lop.trang_thai = request.form.get('trang_thai', lop.trang_thai)
        lop.ma_pt      = int(request.form.get('ma_pt', lop.ma_pt))
        lop.ma_phong   = int(request.form.get('ma_phong', lop.ma_phong))
        db.session.commit()
        flash('Đã cập nhật thông tin lớp.', 'success')
        return redirect(url_for('classes.detail', ma_lop=lop.ma_lop))

    return render_template('classes/edit.html',
                           lop=lop, loai_list=loai_list, phong_list=phong_list, pt_list=pt_list)


# ── Buổi học ──────────────────────────────────────────────────

@classes_bp.route('/session/<int:ma_buoi>')
@login_required
def session_detail(ma_buoi):
    buoi     = BuoiHoc.query.get_or_404(ma_buoi)
    dk_list  = buoi.dang_ki_list.order_by(DangKiBuoiHoc.thoi_gian_dk).all()
    hv_list  = HoiVien.query.filter_by(trang_thai='active').order_by(HoiVien.ho_ten).all()
    return render_template('classes/session_detail.html',
                           buoi=buoi, dk_list=dk_list, hv_list=hv_list)


@classes_bp.route('/session/<int:ma_buoi>/register', methods=['POST'])
@login_required
def register_session(ma_buoi):
    buoi   = BuoiHoc.query.get_or_404(ma_buoi)
    ma_hv  = request.form.get('ma_hv', type=int)

    if not ma_hv:
        flash('Vui lòng chọn hội viên.', 'danger')
        return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))

    # Kiểm tra đã đăng kí chưa
    existing = DangKiBuoiHoc.query.filter_by(ma_hv=ma_hv, ma_buoi=ma_buoi).first()
    if existing:
        flash('Hội viên đã đăng kí buổi học này.', 'warning')
        return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))

    # Kiểm tra còn chỗ không
    if buoi.con_cho <= 0:
        flash('Buổi học đã đầy.', 'danger')
        return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))

    dk = DangKiBuoiHoc(
        ma_hv=ma_hv, ma_buoi=ma_buoi,
        thoi_gian_dk=datetime.now(), trang_thai='confirmed'
    )
    db.session.add(dk)

    # Cập nhật trạng thái lớp nếu đầy
    if buoi.con_cho - 1 == 0:
        buoi.lop_hoc.trang_thai = 'full'

    db.session.commit()
    flash('Đăng kí buổi học thành công!', 'success')
    return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))


@classes_bp.route('/session/registration/<int:dk_id>/cancel', methods=['POST'])
@login_required
def cancel_registration(dk_id):
    dk = DangKiBuoiHoc.query.get_or_404(dk_id)
    dk.trang_thai = 'cancelled'
    # Mở lại lớp nếu bị đầy
    lop = dk.buoi_hoc.lop_hoc
    if lop.trang_thai == 'full':
        lop.trang_thai = 'open'
    db.session.commit()
    flash('Đã hủy đăng kí buổi học.', 'info')
    return redirect(url_for('classes.session_detail', ma_buoi=dk.ma_buoi))


@classes_bp.route('/session/<int:ma_buoi>/update-status', methods=['POST'])
@login_required
def update_session_status(ma_buoi):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))

    buoi = BuoiHoc.query.get_or_404(ma_buoi)
    buoi.trang_thai = request.form.get('trang_thai', buoi.trang_thai)
    db.session.commit()
    flash('Đã cập nhật trạng thái buổi học.', 'success')
    return redirect(url_for('classes.session_detail', ma_buoi=ma_buoi))


# ── Loại lớp ──────────────────────────────────────────────────

@classes_bp.route('/types')
@login_required
def class_types():
    loai_list = LoaiLop.query.order_by(LoaiLop.ma_loai).all()
    return render_template('classes/types.html', loai_list=loai_list)


@classes_bp.route('/types/add', methods=['POST'])
@login_required
def add_class_type():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('classes.class_types'))

    loai = LoaiLop(
        ten_loai   = request.form.get('ten_loai', '').strip(),
        don_gia_pt = float(request.form.get('don_gia_pt', 0)),
        trang_thai = 'active'
    )
    if not loai.ten_loai:
        flash('Vui lòng nhập tên loại lớp.', 'danger')
    else:
        db.session.add(loai)
        db.session.commit()
        flash(f'Đã thêm loại lớp "{loai.ten_loai}".', 'success')
    return redirect(url_for('classes.class_types'))


@classes_bp.route('/types/<int:ma_loai>/toggle', methods=['POST'])
@login_required
def toggle_class_type(ma_loai):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('classes.class_types'))
    loai = LoaiLop.query.get_or_404(ma_loai)
    loai.trang_thai = 'inactive' if loai.trang_thai == 'active' else 'active'
    db.session.commit()
    flash('Đã cập nhật trạng thái loại lớp.', 'success')
    return redirect(url_for('classes.class_types'))


# ── Helper: tạo buổi học ──────────────────────────────────────

def _generate_sessions(lop: LopHoc) -> int:
    """Tự động tạo buổi học cho lớp từ ngày bắt đầu đến hết khóa."""
    days = [int(d.strip()) for d in lop.thu_hoc.split(',') if d.strip()]
    today = date.today()
    cur   = lop.ngay_bat_dau
    count = 0

    while cur <= lop.ngay_ket_thuc:
        # Chuyển weekday Python (0=Mon..6=Sun) sang thứ VN (2=T2..8=CN)
        wd = cur.weekday()
        thu_vn = wd + 2 if wd < 6 else 8  # Sunday → 8

        if thu_vn in days:
            status = 'upcoming'
            if cur < today:
                status = 'completed'
            elif cur == today:
                status = 'ongoing'
            buoi = BuoiHoc(ma_lop=lop.ma_lop, ngay_hoc=cur, trang_thai=status)
            db.session.add(buoi)
            count += 1
        cur += timedelta(1)

    return count
