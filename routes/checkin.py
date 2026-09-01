from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models import db, CheckinOut, HoiVien

checkin_bp = Blueprint('checkin', __name__, template_folder='../templates')


def _staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


@checkin_bp.route('/')
@login_required
def index():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('dashboard.index'))

    # Danh sách đang trong phòng
    dang_trong = (CheckinOut.query
                  .filter(CheckinOut.thoi_gian_checkout == None)
                  .order_by(CheckinOut.thoi_gian_checkin.desc()).all())

    # Lịch sử hôm nay
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    lich_su = (CheckinOut.query
               .filter(CheckinOut.thoi_gian_checkin >= today_start)
               .order_by(CheckinOut.thoi_gian_checkin.desc())
               .limit(50).all())

    hv_list = HoiVien.query.filter_by(trang_thai='active').order_by(HoiVien.ho_ten).all()
    return render_template('checkin/index.html',
                           dang_trong=dang_trong, lich_su=lich_su, hv_list=hv_list)


@checkin_bp.route('/do', methods=['POST'])
@login_required
def do_checkin():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('checkin.index'))

    ma_hv = request.form.get('ma_hv', type=int)
    hv = HoiVien.query.get(ma_hv)
    if not hv:
        flash('Không tìm thấy hội viên.', 'danger')
        return redirect(url_for('checkin.index'))

    # Kiểm tra đang checkin chưa
    existing = CheckinOut.query.filter_by(
        ma_hv=ma_hv, thoi_gian_checkout=None
    ).first()
    if existing:
        flash(f'{hv.ho_ten} đang trong phòng tập. Vui lòng check-out trước.', 'warning')
        return redirect(url_for('checkin.index'))

    ci = CheckinOut(ma_hv=ma_hv, thoi_gian_checkin=datetime.now())
    db.session.add(ci)
    db.session.commit()
    flash(f'✅ Check-in thành công: {hv.ho_ten}', 'success')
    return redirect(url_for('checkin.index'))


@checkin_bp.route('/<int:luot_id>/checkout', methods=['POST'])
@login_required
def do_checkout(luot_id):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('checkin.index'))

    ci = CheckinOut.query.get_or_404(luot_id)
    if ci.thoi_gian_checkout:
        flash('Hội viên đã check-out trước đó.', 'warning')
    else:
        ci.thoi_gian_checkout = datetime.now()
        db.session.commit()
        flash(f'✅ Check-out: {ci.hoi_vien.ho_ten}', 'success')
    return redirect(url_for('checkin.index'))


@checkin_bp.route('/quick', methods=['POST'])
@login_required
def quick_checkin():
    """Check-in/out nhanh bằng SDT."""
    if not _staff():
        return redirect(url_for('checkin.index'))

    sdt = request.form.get('sdt', '').strip()
    hv = HoiVien.query.filter_by(sdt=sdt).first()
    if not hv:
        flash(f'Không tìm thấy hội viên với SDT: {sdt}', 'danger')
        return redirect(url_for('checkin.index'))

    existing = CheckinOut.query.filter_by(ma_hv=hv.ma_hv, thoi_gian_checkout=None).first()
    if existing:
        # Đang trong phòng → tự động checkout
        existing.thoi_gian_checkout = datetime.now()
        db.session.commit()
        flash(f'✅ Check-out: {hv.ho_ten}', 'success')
    else:
        ci = CheckinOut(ma_hv=hv.ma_hv, thoi_gian_checkin=datetime.now())
        db.session.add(ci)
        db.session.commit()
        flash(f'✅ Check-in: {hv.ho_ten}', 'success')

    return redirect(url_for('checkin.index'))
