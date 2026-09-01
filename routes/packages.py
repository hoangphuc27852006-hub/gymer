from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, timedelta
from models import db, GoiTap, DangKiGoi, HoiVien

packages_bp = Blueprint('packages', __name__, template_folder='../templates')


def _staff_only():
    if current_user.vai_tro not in ('admin', 'nhanvien'):
        flash('Không có quyền thực hiện thao tác này.', 'danger')
        return False
    return True


@packages_bp.route('/')
@login_required
def index():
    goi_list = GoiTap.query.order_by(GoiTap.gia_tien).all()
    return render_template('packages/index.html', goi_list=goi_list)


@packages_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if not _staff_only():
        return redirect(url_for('packages.index'))

    if request.method == 'POST':
        goi = GoiTap(
            ten_goi      = request.form.get('ten_goi', '').strip(),
            thoi_han_goi = int(request.form.get('thoi_han_goi', 30)),
            gia_tien     = float(request.form.get('gia_tien', 0)),
            so_buoi_pt   = int(request.form.get('so_buoi_pt', 0)),
            trang_thai   = 'active'
        )
        if not goi.ten_goi:
            flash('Vui lòng nhập tên gói.', 'danger')
        else:
            db.session.add(goi)
            db.session.commit()
            flash(f'Đã thêm gói "{goi.ten_goi}".', 'success')
            return redirect(url_for('packages.index'))

    return render_template('packages/add.html')


@packages_bp.route('/<int:ma_goi>/edit', methods=['GET', 'POST'])
@login_required
def edit(ma_goi):
    if not _staff_only():
        return redirect(url_for('packages.index'))

    goi = GoiTap.query.get_or_404(ma_goi)
    if request.method == 'POST':
        goi.ten_goi      = request.form.get('ten_goi', goi.ten_goi).strip()
        goi.thoi_han_goi = int(request.form.get('thoi_han_goi', goi.thoi_han_goi))
        goi.gia_tien     = float(request.form.get('gia_tien', goi.gia_tien))
        goi.so_buoi_pt   = int(request.form.get('so_buoi_pt', goi.so_buoi_pt))
        goi.trang_thai   = request.form.get('trang_thai', goi.trang_thai)
        db.session.commit()
        flash('Đã cập nhật gói tập.', 'success')
        return redirect(url_for('packages.index'))

    return render_template('packages/edit.html', goi=goi)


@packages_bp.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    """Đăng kí gói cho hội viên."""
    if not _staff_only():
        return redirect(url_for('packages.index'))

    hv_list  = HoiVien.query.filter_by(trang_thai='active').order_by(HoiVien.ho_ten).all()
    goi_list = GoiTap.query.filter_by(trang_thai='active').all()

    if request.method == 'POST':
        ma_hv    = int(request.form.get('ma_hv'))
        ma_goi   = int(request.form.get('ma_goi'))
        kich_hoat = request.form.get('kich_hoat') == 'on'

        goi = GoiTap.query.get_or_404(ma_goi)
        hom_nay = date.today()

        dk = DangKiGoi(
            ma_hv              = ma_hv,
            ma_goi             = ma_goi,
            ngay_dang_ki       = hom_nay,
            so_buoi_pt_con_lai = goi.so_buoi_pt,
            trang_thai         = 'waiting'
        )

        if kich_hoat:
            dk.ngay_bat_dau  = hom_nay
            dk.ngay_het_han  = hom_nay + timedelta(days=goi.thoi_han_goi)
            dk.trang_thai    = 'active'

        db.session.add(dk)
        db.session.commit()
        flash('Đăng kí gói thành công!', 'success')
        return redirect(url_for('members.detail', ma_hv=ma_hv))

    # Cho phép pre-select HV từ query string
    selected_hv = request.args.get('ma_hv', type=int)
    return render_template('packages/buy.html',
                           hv_list=hv_list, goi_list=goi_list, selected_hv=selected_hv)


@packages_bp.route('/registration/<int:dk_id>/activate', methods=['POST'])
@login_required
def activate(dk_id):
    if not _staff_only():
        return redirect(url_for('packages.index'))

    dk = DangKiGoi.query.get_or_404(dk_id)
    if dk.trang_thai != 'waiting':
        flash('Gói không ở trạng thái chờ kích hoạt.', 'warning')
    else:
        from datetime import date, timedelta
        dk.ngay_bat_dau = date.today()
        dk.ngay_het_han = date.today() + timedelta(days=dk.goi_tap.thoi_han_goi)
        dk.trang_thai   = 'active'
        db.session.commit()
        flash('Kích hoạt gói thành công!', 'success')
    return redirect(url_for('members.detail', ma_hv=dk.ma_hv))


@packages_bp.route('/registration/<int:dk_id>/expire', methods=['POST'])
@login_required
def expire(dk_id):
    if not _staff_only():
        return redirect(url_for('packages.index'))

    dk = DangKiGoi.query.get_or_404(dk_id)
    dk.trang_thai = 'expired'
    db.session.commit()
    flash('Đã đánh dấu gói hết hạn.', 'success')
    return redirect(url_for('members.detail', ma_hv=dk.ma_hv))
