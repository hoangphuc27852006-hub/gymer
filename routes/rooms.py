from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, PhongTap

rooms_bp = Blueprint('rooms', __name__, template_folder='../templates')


def _staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


@rooms_bp.route('/')
@login_required
def index():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('dashboard.index'))
    phong_list = PhongTap.query.order_by(PhongTap.ma_phong).all()
    return render_template('rooms/index.html', phong_list=phong_list)


@rooms_bp.route('/add', methods=['POST'])
@login_required
def add():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('rooms.index'))

    phong = PhongTap(
        ten_phong  = request.form.get('ten_phong', '').strip(),
        vi_tri     = request.form.get('vi_tri', '').strip(),
        suc_chua   = int(request.form.get('suc_chua', 20)),
        trang_thai = 'active'
    )
    if not phong.ten_phong:
        flash('Vui lòng nhập tên phòng.', 'danger')
    else:
        db.session.add(phong)
        db.session.commit()
        flash(f'Đã thêm phòng "{phong.ten_phong}".', 'success')
    return redirect(url_for('rooms.index'))


@rooms_bp.route('/<int:ma_phong>/edit', methods=['POST'])
@login_required
def edit(ma_phong):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('rooms.index'))

    phong = PhongTap.query.get_or_404(ma_phong)
    phong.ten_phong  = request.form.get('ten_phong', phong.ten_phong).strip()
    phong.vi_tri     = request.form.get('vi_tri', '').strip()
    phong.suc_chua   = int(request.form.get('suc_chua', phong.suc_chua))
    phong.trang_thai = request.form.get('trang_thai', phong.trang_thai)
    db.session.commit()
    flash('Đã cập nhật thông tin phòng.', 'success')
    return redirect(url_for('rooms.index'))


@rooms_bp.route('/<int:ma_phong>/toggle', methods=['POST'])
@login_required
def toggle(ma_phong):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('rooms.index'))

    phong = PhongTap.query.get_or_404(ma_phong)
    phong.trang_thai = 'maintenance' if phong.trang_thai == 'active' else 'active'
    db.session.commit()
    flash(f'Đã cập nhật trạng thái phòng "{phong.ten_phong}".', 'success')
    return redirect(url_for('rooms.index'))
