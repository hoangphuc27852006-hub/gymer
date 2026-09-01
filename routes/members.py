from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from models import db, HoiVien, ChiSoCoThe, CheckinOut, DangKiGoi, DangKiBuoiHoc, BuoiPT

members_bp = Blueprint('members', __name__, template_folder='../templates')


def _require_staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


@members_bp.route('/')
@login_required
def index():
    q      = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    page   = request.args.get('page', 1, type=int)

    query = HoiVien.query
    if q:
        query = query.filter(
            HoiVien.ho_ten.ilike(f'%{q}%') |
            HoiVien.sdt.ilike(f'%{q}%') |
            HoiVien.cccd.ilike(f'%{q}%')
        )
    if status:
        query = query.filter_by(trang_thai=status)

    members = query.order_by(HoiVien.ma_hv.desc()).paginate(page=page, per_page=15)
    return render_template('members/index.html', members=members, q=q, status=status)


@members_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not _require_staff():
        flash('Không có quyền thực hiện thao tác này.', 'danger')
        return redirect(url_for('members.index'))

    if request.method == 'POST':
        hv = HoiVien(
            ho_ten    = request.form.get('ho_ten', '').strip(),
            sdt       = request.form.get('sdt', '').strip(),
            dia_chi   = request.form.get('dia_chi', '').strip(),
            cccd      = request.form.get('cccd', '').strip() or None,
            gioi_tinh = request.form.get('gioi_tinh'),
            ngay_sinh = _parse_date(request.form.get('ngay_sinh')),
            trang_thai='active'
        )
        if not hv.ho_ten:
            flash('Vui lòng nhập họ tên.', 'danger')
            return render_template('members/add.html')

        if hv.cccd and HoiVien.query.filter_by(cccd=hv.cccd).first():
            flash('CCCD đã tồn tại trong hệ thống.', 'danger')
            return render_template('members/add.html')

        db.session.add(hv)
        db.session.commit()
        flash(f'Thêm hội viên "{hv.ho_ten}" thành công!', 'success')
        return redirect(url_for('members.detail', ma_hv=hv.ma_hv))

    return render_template('members/add.html')


@members_bp.route('/<int:ma_hv>')
@login_required
def detail(ma_hv):
    hv = HoiVien.query.get_or_404(ma_hv)

    # Kiểm tra quyền: hội viên chỉ xem được trang của mình
    if current_user.vai_tro == 'hoivien' and (
        not current_user.hoi_vien or current_user.hoi_vien.ma_hv != ma_hv
    ):
        flash('Không có quyền xem thông tin này.', 'danger')
        return redirect(url_for('dashboard.index'))

    chi_so_list   = hv.chi_so_list.order_by(ChiSoCoThe.ngay_do.desc()).all()
    checkin_list  = hv.checkins.order_by(CheckinOut.thoi_gian_checkin.desc()).limit(20).all()
    goi_list      = hv.dang_ki_gois.order_by(DangKiGoi.ngay_dang_ki.desc()).all()
    buoi_pt_list  = hv.buoi_pt_list.order_by(BuoiPT.thoi_gian_dat.desc()).limit(10).all()
    dk_buoi_list  = hv.dang_ki_buois.order_by(DangKiBuoiHoc.thoi_gian_dk.desc()).limit(10).all()
    dang_checkin  = hv.dang_checkin

    return render_template('members/detail.html',
        hv=hv, chi_so_list=chi_so_list, checkin_list=checkin_list,
        goi_list=goi_list, buoi_pt_list=buoi_pt_list,
        dk_buoi_list=dk_buoi_list, dang_checkin=dang_checkin)


@members_bp.route('/<int:ma_hv>/edit', methods=['GET', 'POST'])
@login_required
def edit(ma_hv):
    if not _require_staff():
        flash('Không có quyền thực hiện thao tác này.', 'danger')
        return redirect(url_for('members.detail', ma_hv=ma_hv))

    hv = HoiVien.query.get_or_404(ma_hv)
    if request.method == 'POST':
        hv.ho_ten    = request.form.get('ho_ten', hv.ho_ten).strip()
        hv.sdt       = request.form.get('sdt', '').strip()
        hv.dia_chi   = request.form.get('dia_chi', '').strip()
        hv.gioi_tinh = request.form.get('gioi_tinh', hv.gioi_tinh)
        hv.ngay_sinh = _parse_date(request.form.get('ngay_sinh'))
        hv.trang_thai= request.form.get('trang_thai', hv.trang_thai)

        new_cccd = request.form.get('cccd', '').strip() or None
        if new_cccd and new_cccd != hv.cccd:
            existing = HoiVien.query.filter_by(cccd=new_cccd).first()
            if existing and existing.ma_hv != hv.ma_hv:
                flash('CCCD đã tồn tại.', 'danger')
                return render_template('members/edit.html', hv=hv)
        hv.cccd = new_cccd

        db.session.commit()
        flash('Cập nhật thông tin thành công!', 'success')
        return redirect(url_for('members.detail', ma_hv=hv.ma_hv))

    return render_template('members/edit.html', hv=hv)


@members_bp.route('/<int:ma_hv>/body-stats', methods=['POST'])
@login_required
def add_body_stat(ma_hv):
    if not _require_staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('members.detail', ma_hv=ma_hv))

    hv = HoiVien.query.get_or_404(ma_hv)
    cs = ChiSoCoThe(
        ma_hv        = ma_hv,
        ngay_do      = _parse_date(request.form.get('ngay_do')) or date.today(),
        chieu_cao    = _parse_float(request.form.get('chieu_cao')),
        can_nang     = _parse_float(request.form.get('can_nang')),
        vong_eo      = _parse_float(request.form.get('vong_eo')),
        phan_tram_mo = _parse_float(request.form.get('phan_tram_mo')),
        ghi_chu      = request.form.get('ghi_chu', '').strip()
    )
    db.session.add(cs)
    db.session.commit()
    flash('Đã thêm chỉ số cơ thể.', 'success')
    return redirect(url_for('members.detail', ma_hv=ma_hv))


# ── Helpers ──────────────────────────────────────────────
def _parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def _parse_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None
