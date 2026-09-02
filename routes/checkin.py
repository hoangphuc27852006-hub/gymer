from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from models import db, CheckinOut, HoiVien

checkin_bp = Blueprint('checkin', __name__, template_folder='../templates')


def _staff():
    return current_user.vai_tro in ('admin', 'nhanvien')


def _digits(s):
    return ''.join(ch for ch in (s or '') if ch.isdigit())


def _find_member(keyword):
    """Tìm hội viên theo SĐT (bỏ khoảng trắng) hoặc họ tên."""
    keyword = (keyword or '').strip()
    if not keyword:
        return None

    digits = _digits(keyword)
    if digits:
        hv = HoiVien.query.filter(HoiVien.sdt == digits).first()
        if hv:
            return hv
        hv = (HoiVien.query
              .filter(func.replace(func.coalesce(HoiVien.sdt, ''), ' ', '') == digits)
              .first())
        if hv:
            return hv

    matches = (HoiVien.query
               .filter(HoiVien.ho_ten.ilike(f'%{keyword}%'))
               .order_by(HoiVien.ho_ten)
               .limit(6).all())
    if len(matches) == 1:
        return matches[0]
    return matches


@checkin_bp.route('/')
@login_required
def index():
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('dashboard.index'))

    dang_trong = (CheckinOut.query
                  .options(joinedload(CheckinOut.hoi_vien))
                  .filter(CheckinOut.thoi_gian_checkout.is_(None))
                  .order_by(CheckinOut.thoi_gian_checkin.desc()).all())
    dang_trong = [luot for luot in dang_trong if luot.hoi_vien]

    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    lich_su = (CheckinOut.query
               .options(joinedload(CheckinOut.hoi_vien))
               .filter(CheckinOut.thoi_gian_checkin >= today_start)
               .order_by(CheckinOut.thoi_gian_checkin.desc())
               .limit(50).all())
    lich_su = [luot for luot in lich_su if luot.hoi_vien]

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
    if hv.trang_thai != 'active':
        flash(f'{hv.ho_ten} đang ngừng hoạt động, không thể check-in.', 'warning')
        return redirect(url_for('checkin.index'))

    existing = CheckinOut.query.filter(
        CheckinOut.ma_hv == ma_hv,
        CheckinOut.thoi_gian_checkout.is_(None)
    ).first()
    if existing:
        flash(f'{hv.ho_ten} đang trong phòng tập. Vui lòng check-out trước.', 'warning')
        return redirect(url_for('checkin.index'))

    ci = CheckinOut(ma_hv=ma_hv, thoi_gian_checkin=datetime.now())
    db.session.add(ci)
    db.session.commit()
    if not hv.goi_hien_tai:
        flash(f'Check-in thành công: {hv.ho_ten}. Lưu ý: hội viên chưa có gói tập đang hoạt động.', 'warning')
    else:
        flash(f'Check-in thành công: {hv.ho_ten}', 'success')
    return redirect(url_for('checkin.index'))


@checkin_bp.route('/<int:luot_id>/checkout', methods=['POST'])
@login_required
def do_checkout(luot_id):
    if not _staff():
        flash('Không có quyền.', 'danger')
        return redirect(url_for('checkin.index'))

    ci = db.session.get(CheckinOut, luot_id)
    if not ci:
        flash('Không tìm thấy lượt check-in.', 'danger')
        return redirect(url_for('checkin.index'))
    if ci.thoi_gian_checkout:
        flash('Hội viên đã check-out trước đó.', 'warning')
    else:
        ci.thoi_gian_checkout = datetime.now()
        db.session.commit()
        ten = ci.hoi_vien.ho_ten if ci.hoi_vien else 'hội viên'
        flash(f'Check-out thành công: {ten}', 'success')
    return redirect(url_for('checkin.index'))


@checkin_bp.route('/quick', methods=['POST'])
@login_required
def quick_checkin():
    """Check-in/out nhanh bằng SDT."""
    if not _staff():
        return redirect(url_for('checkin.index'))

    keyword = request.form.get('sdt', '').strip()
    found = _find_member(keyword)
    if isinstance(found, list):
        if not found:
            flash(f'Không tìm thấy hội viên với: {keyword}', 'danger')
        else:
            names = ', '.join(hv.ho_ten for hv in found)
            flash(f'Có nhiều hội viên khớp ({names}). Vui lòng chọn chính xác ở form thủ công.', 'warning')
        return redirect(url_for('checkin.index'))
    hv = found
    if not hv:
        flash(f'Không tìm thấy hội viên với: {keyword}', 'danger')
        return redirect(url_for('checkin.index'))
    if hv.trang_thai != 'active':
        flash(f'{hv.ho_ten} đang ngừng hoạt động, không thể check-in/out.', 'warning')
        return redirect(url_for('checkin.index'))

    existing = CheckinOut.query.filter(
        CheckinOut.ma_hv == hv.ma_hv,
        CheckinOut.thoi_gian_checkout.is_(None)
    ).first()
    if existing:
        existing.thoi_gian_checkout = datetime.now()
        db.session.commit()
        flash(f'Check-out thành công: {hv.ho_ten}', 'success')
    else:
        ci = CheckinOut(ma_hv=hv.ma_hv, thoi_gian_checkin=datetime.now())
        db.session.add(ci)
        db.session.commit()
        if not hv.goi_hien_tai:
            flash(f'Check-in thành công: {hv.ho_ten}. Lưu ý: hội viên chưa có gói tập đang hoạt động.', 'warning')
        else:
            flash(f'Check-in thành công: {hv.ho_ten}', 'success')

    return redirect(url_for('checkin.index'))
