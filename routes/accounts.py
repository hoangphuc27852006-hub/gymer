from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, TaiKhoan
from werkzeug.security import generate_password_hash
from functools import wraps

accounts_bp = Blueprint('accounts', __name__, template_folder='../templates')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.vai_tro != 'admin':
            flash('Chỉ Admin mới có quyền truy cập trang này.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


@accounts_bp.route('/')
@login_required
@admin_required
def index():
    tks = TaiKhoan.query.order_by(TaiKhoan.vai_tro).all()
    return render_template('accounts/index.html', tks=tks)


@accounts_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    from models import HoiVien, NhanVien, PT
    if request.method == 'POST':
        ten_dn   = request.form.get('ten_dang_nhap', '').strip()
        mat_khau = request.form.get('mat_khau', '').strip()
        vai_tro  = request.form.get('vai_tro')
        ma_hv    = request.form.get('ma_hv') or None
        ma_nv    = request.form.get('ma_nv') or None
        ma_pt    = request.form.get('ma_pt') or None

        if not ten_dn or not mat_khau:
            flash('Vui lòng nhập đầy đủ thông tin.', 'danger')
        elif TaiKhoan.query.filter_by(ten_dang_nhap=ten_dn).first():
            flash('Tên đăng nhập đã tồn tại.', 'danger')
        else:
            tk = TaiKhoan(
                ten_dang_nhap=ten_dn,
                mat_khau=generate_password_hash(mat_khau),
                vai_tro=vai_tro,
                trang_thai='active',
                ma_hv=int(ma_hv) if ma_hv else None,
                ma_nv=int(ma_nv) if ma_nv else None,
                ma_pt=int(ma_pt) if ma_pt else None,
            )
            db.session.add(tk)
            db.session.commit()
            flash(f'Tạo tài khoản "{ten_dn}" thành công!', 'success')
            return redirect(url_for('accounts.index'))

    hv_list = HoiVien.query.filter(~HoiVien.tai_khoan.has()).all()
    nv_list = NhanVien.query.filter(~NhanVien.tai_khoan.has()).all()
    pt_list = PT.query.filter(~PT.tai_khoan.has()).all()
    return render_template('accounts/add.html', hv_list=hv_list, nv_list=nv_list, pt_list=pt_list)


@accounts_bp.route('/<int:ma_tk>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle(ma_tk):
    tk = TaiKhoan.query.get_or_404(ma_tk)
    if tk.ma_tk == current_user.ma_tk:
        flash('Không thể thay đổi trạng thái tài khoản của chính mình.', 'warning')
    else:
        tk.trang_thai = 'blocked' if tk.trang_thai == 'active' else 'active'
        db.session.commit()
        flash(f'Tài khoản "{tk.ten_dang_nhap}" đã được cập nhật.', 'success')
    return redirect(url_for('accounts.index'))


@accounts_bp.route('/<int:ma_tk>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password(ma_tk):
    tk = TaiKhoan.query.get_or_404(ma_tk)
    new_pw = request.form.get('new_password', '').strip()
    if not new_pw or len(new_pw) < 6:
        flash('Mật khẩu phải có ít nhất 6 ký tự.', 'danger')
    else:
        tk.mat_khau = generate_password_hash(new_pw)
        db.session.commit()
        flash(f'Đặt lại mật khẩu cho "{tk.ten_dang_nhap}" thành công!', 'success')
    return redirect(url_for('accounts.index'))


@accounts_bp.route('/<int:ma_tk>/delete', methods=['POST'])
@login_required
@admin_required
def delete(ma_tk):
    tk = TaiKhoan.query.get_or_404(ma_tk)
    if tk.ma_tk == current_user.ma_tk:
        flash('Không thể xóa tài khoản của chính mình.', 'danger')
    else:
        db.session.delete(tk)
        db.session.commit()
        flash('Đã xóa tài khoản.', 'success')
    return redirect(url_for('accounts.index'))
