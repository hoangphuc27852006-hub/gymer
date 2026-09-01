from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import TaiKhoan

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        ten_dn   = request.form.get('ten_dang_nhap') or request.form.get('username', '')
        ten_dn   = ten_dn.strip()
        mat_khau = request.form.get('mat_khau') or request.form.get('password', '')
        mat_khau = mat_khau.strip()
        remember = request.form.get('remember') == 'on'

        tk = TaiKhoan.query.filter_by(ten_dang_nhap=ten_dn).first()

        if not tk or not check_password_hash(tk.mat_khau, mat_khau):
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')
        elif tk.trang_thai == 'blocked':
            flash('Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin.', 'danger')
        else:
            login_user(tk, remember=remember)
            next_page = request.args.get('next')
            flash(f'Chào mừng, {tk.display_name}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))
