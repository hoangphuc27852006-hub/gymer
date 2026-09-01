from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date
from models import db, NhanVien

staff_bp = Blueprint('staff', __name__, template_folder='../templates')


def _admin_only():
    if current_user.vai_tro != 'admin':
        flash('Chỉ Admin mới có quyền truy cập.', 'danger')
        return False
    return True


def _parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


@staff_bp.route('/')
@login_required
def index():
    if not _admin_only():
        return redirect(url_for('dashboard.index'))

    q      = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    query  = NhanVien.query
    if q:
        query = query.filter(NhanVien.ho_ten.ilike(f'%{q}%') | NhanVien.sdt.ilike(f'%{q}%'))
    if status:
        query = query.filter_by(trang_thai=status)
    nv_list = query.order_by(NhanVien.ho_ten).all()
    return render_template('staff/index.html', nv_list=nv_list, q=q, status=status)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not _admin_only():
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        nv = NhanVien(
            ho_ten       = request.form.get('ho_ten', '').strip(),
            cccd         = request.form.get('cccd', '').strip() or None,
            ngay_sinh    = _parse_date(request.form.get('ngay_sinh')),
            sdt          = request.form.get('sdt', '').strip(),
            ngay_vao_lam = _parse_date(request.form.get('ngay_vao_lam')) or date.today(),
            luong_co_ban = float(request.form.get('luong_co_ban', 0)),
            chuc_vu      = request.form.get('chuc_vu', '').strip(),
            trang_thai   = 'active'
        )
        if not nv.ho_ten:
            flash('Vui lòng nhập họ tên.', 'danger')
            return render_template('staff/add.html')

        if nv.cccd and NhanVien.query.filter_by(cccd=nv.cccd).first():
            flash('CCCD đã tồn tại.', 'danger')
            return render_template('staff/add.html')

        db.session.add(nv)
        db.session.commit()
        flash(f'Thêm nhân viên "{nv.ho_ten}" thành công!', 'success')
        return redirect(url_for('staff.index'))

    return render_template('staff/add.html')


@staff_bp.route('/<int:ma_nv>/edit', methods=['GET', 'POST'])
@login_required
def edit(ma_nv):
    if not _admin_only():
        return redirect(url_for('dashboard.index'))

    nv = NhanVien.query.get_or_404(ma_nv)
    if request.method == 'POST':
        nv.ho_ten       = request.form.get('ho_ten', nv.ho_ten).strip()
        nv.sdt          = request.form.get('sdt', '').strip()
        nv.ngay_sinh    = _parse_date(request.form.get('ngay_sinh'))
        nv.ngay_vao_lam = _parse_date(request.form.get('ngay_vao_lam'))
        nv.luong_co_ban = float(request.form.get('luong_co_ban', nv.luong_co_ban))
        nv.chuc_vu      = request.form.get('chuc_vu', nv.chuc_vu).strip()
        nv.trang_thai   = request.form.get('trang_thai', nv.trang_thai)
        db.session.commit()
        flash('Đã cập nhật thông tin nhân viên.', 'success')
        return redirect(url_for('staff.index'))

    return render_template('staff/edit.html', nv=nv)


@staff_bp.route('/<int:ma_nv>/toggle', methods=['POST'])
@login_required
def toggle(ma_nv):
    if not _admin_only():
        return redirect(url_for('dashboard.index'))

    nv = NhanVien.query.get_or_404(ma_nv)
    nv.trang_thai = 'inactive' if nv.trang_thai == 'active' else 'active'
    db.session.commit()
    flash(f'Đã cập nhật trạng thái nhân viên "{nv.ho_ten}".', 'success')
    return redirect(url_for('staff.index'))
