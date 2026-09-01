from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, date
from models import db, PT, BuoiPT, LopHoc, HoiVien, DangKiGoi

trainers_bp = Blueprint('trainers', __name__, template_folder='../templates')


def _staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


def _parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def _parse_dt(s):
    if not s:
        return None
    for fmt in ('%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    return None


# ── Danh sách PT ─────────────────────────────────────────────

@trainers_bp.route('/')
@login_required
def index():
    q      = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    query  = PT.query
    if q:
        query = query.filter(PT.ho_ten.ilike(f'%{q}%') | PT.sdt.ilike(f'%{q}%'))
    if status:
        query = query.filter_by(trang_thai=status)
    pt_list = query.order_by(PT.ho_ten).all()
    return render_template('trainers/index.html', pt_list=pt_list, q=q, status=status)


@trainers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('trainers.index'))

    if request.method == 'POST':
        pt = PT(
            ho_ten             = request.form.get('ho_ten', '').strip(),
            cccd               = request.form.get('cccd', '').strip() or None,
            sdt                = request.form.get('sdt', '').strip(),
            ngay_sinh          = _parse_date(request.form.get('ngay_sinh')),
            so_nam_kinh_nghiem = int(request.form.get('so_nam_kinh_nghiem', 0)),
            chuyen_mon         = request.form.get('chuyen_mon', '').strip(),
            luong_co_ban       = float(request.form.get('luong_co_ban', 0)),
            trang_thai         = 'active'
        )
        if not pt.ho_ten:
            flash('Vui lòng nhập họ tên.', 'danger')
            return render_template('trainers/add.html')

        if pt.cccd and PT.query.filter_by(cccd=pt.cccd).first():
            flash('CCCD đã tồn tại.', 'danger')
            return render_template('trainers/add.html')

        db.session.add(pt)
        db.session.commit()
        flash(f'Thêm PT "{pt.ho_ten}" thành công!', 'success')
        return redirect(url_for('trainers.detail', ma_pt=pt.ma_pt))

    return render_template('trainers/add.html')


@trainers_bp.route('/<int:ma_pt>')
@login_required
def detail(ma_pt):
    pt = PT.query.get_or_404(ma_pt)

    # PT chỉ xem được trang của mình
    if current_user.vai_tro == 'pt' and (
        not current_user.pt or current_user.pt.ma_pt != ma_pt
    ):
        flash('Không có quyền xem thông tin này.', 'danger')
        return redirect(url_for('dashboard.index'))

    today = date.today()
    lop_list = pt.lop_hoc_list.all()
    buoi_pt_list = pt.buoi_pt_list.order_by(BuoiPT.thoi_gian_bat_dau.desc()).limit(20).all()
    buoi_pt_upcoming = (pt.buoi_pt_list
                        .filter(BuoiPT.trang_thai == 'scheduled')
                        .order_by(BuoiPT.thoi_gian_bat_dau).all())
    hv_list = HoiVien.query.filter_by(trang_thai='active').order_by(HoiVien.ho_ten).all()

    return render_template('trainers/detail.html',
        pt=pt, lop_list=lop_list, buoi_pt_list=buoi_pt_list,
        buoi_pt_upcoming=buoi_pt_upcoming, hv_list=hv_list, today=today)


@trainers_bp.route('/<int:ma_pt>/edit', methods=['GET', 'POST'])
@login_required
def edit(ma_pt):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('trainers.detail', ma_pt=ma_pt))

    pt = PT.query.get_or_404(ma_pt)
    if request.method == 'POST':
        pt.ho_ten             = request.form.get('ho_ten', pt.ho_ten).strip()
        pt.sdt                = request.form.get('sdt', '').strip()
        pt.ngay_sinh          = _parse_date(request.form.get('ngay_sinh'))
        pt.so_nam_kinh_nghiem = int(request.form.get('so_nam_kinh_nghiem', pt.so_nam_kinh_nghiem))
        pt.chuyen_mon         = request.form.get('chuyen_mon', '').strip()
        pt.luong_co_ban       = float(request.form.get('luong_co_ban', pt.luong_co_ban))
        pt.trang_thai         = request.form.get('trang_thai', pt.trang_thai)
        db.session.commit()
        flash('Đã cập nhật thông tin PT.', 'success')
        return redirect(url_for('trainers.detail', ma_pt=pt.ma_pt))

    return render_template('trainers/edit.html', pt=pt)


# ── Buổi PT ───────────────────────────────────────────────────

@trainers_bp.route('/pt-sessions')
@login_required
def pt_sessions():
    if current_user.vai_tro == 'pt':
        pt_obj = current_user.pt
        sessions = (BuoiPT.query.filter_by(ma_pt=pt_obj.ma_pt)
                    .order_by(BuoiPT.thoi_gian_bat_dau.desc()).all())
    else:
        sessions = BuoiPT.query.order_by(BuoiPT.thoi_gian_bat_dau.desc()).all()

    pt_list = PT.query.filter_by(trang_thai='active').all()
    hv_list = HoiVien.query.filter_by(trang_thai='active').order_by(HoiVien.ho_ten).all()
    return render_template('trainers/pt_sessions.html',
                           sessions=sessions, pt_list=pt_list, hv_list=hv_list)


@trainers_bp.route('/pt-sessions/book', methods=['POST'])
@login_required
def book_pt_session():
    ma_hv     = int(request.form.get('ma_hv'))
    ma_pt     = int(request.form.get('ma_pt'))
    tg_bd_str = request.form.get('thoi_gian_bat_dau', '')
    thoi_luong = int(request.form.get('thoi_luong', 60))

    tg_bd = _parse_dt(tg_bd_str)
    if not tg_bd:
        flash('Thời gian không hợp lệ.', 'danger')
        return redirect(url_for('trainers.pt_sessions'))

    tg_kt = datetime(tg_bd.year, tg_bd.month, tg_bd.day,
                     tg_bd.hour, tg_bd.minute)
    from datetime import timedelta
    tg_kt = tg_bd + timedelta(minutes=thoi_luong)

    # Lấy giá từ loại lớp của PT hoặc mặc định
    hv = HoiVien.query.get(ma_hv)
    dk_goi = None
    if hv:
        dk_goi = hv.dang_ki_gois.filter_by(trang_thai='active').first()

    buoi = BuoiPT(
        ma_hv              = ma_hv,
        ma_pt              = ma_pt,
        thoi_gian_dat      = datetime.now(),
        thoi_gian_bat_dau  = tg_bd,
        thoi_gian_ket_thuc = tg_kt,
        don_gia_pt         = float(request.form.get('don_gia_pt', 0)),
        thoi_luong         = thoi_luong,
        trang_thai         = 'scheduled'
    )
    db.session.add(buoi)

    # Trừ buổi PT từ gói nếu có
    if dk_goi and dk_goi.so_buoi_pt_con_lai > 0:
        dk_goi.so_buoi_pt_con_lai -= 1

    db.session.commit()
    flash('Đặt lịch buổi PT thành công!', 'success')
    return redirect(url_for('trainers.pt_sessions'))


@trainers_bp.route('/pt-sessions/<int:buoi_id>/complete', methods=['POST'])
@login_required
def complete_pt_session(buoi_id):
    buoi = BuoiPT.query.get_or_404(buoi_id)
    buoi.trang_thai = 'completed'
    db.session.commit()
    flash('Đã hoàn thành buổi PT.', 'success')
    return redirect(url_for('trainers.pt_sessions'))


@trainers_bp.route('/pt-sessions/<int:buoi_id>/cancel', methods=['POST'])
@login_required
def cancel_pt_session(buoi_id):
    buoi = BuoiPT.query.get_or_404(buoi_id)
    buoi.trang_thai    = 'cancelled'
    buoi.thoi_gian_huy = datetime.now()
    db.session.commit()
    flash('Đã hủy buổi PT.', 'info')
    return redirect(url_for('trainers.pt_sessions'))


@trainers_bp.route('/pt-sessions/<int:buoi_id>/absent', methods=['POST'])
@login_required
def absent_pt_session(buoi_id):
    buoi = BuoiPT.query.get_or_404(buoi_id)
    buoi.trang_thai = 'absent'
    db.session.commit()
    flash('Đã đánh dấu hội viên vắng mặt.', 'warning')
    return redirect(url_for('trainers.pt_sessions'))
