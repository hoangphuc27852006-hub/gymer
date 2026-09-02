from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, TaiKhoan, HoiVien

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


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        ho_ten        = (request.form.get('ho_ten') or '').strip()
        ten_dang_nhap = (request.form.get('ten_dang_nhap') or '').strip()
        mat_khau      = (request.form.get('mat_khau') or '').strip()
        xac_nhan_mk   = (request.form.get('xac_nhan_mat_khau') or '').strip()
        sdt           = (request.form.get('sdt') or '').strip()

        # ── Validate ─────────────────────────────────────
        loi = None
        if not ho_ten or not ten_dang_nhap or not mat_khau:
            loi = 'Vui lòng điền đầy đủ các trường bắt buộc.'
        elif len(mat_khau) < 6:
            loi = 'Mật khẩu phải có ít nhất 6 ký tự.'
        elif mat_khau != xac_nhan_mk:
            loi = 'Mật khẩu xác nhận không khớp.'
        elif TaiKhoan.query.filter_by(ten_dang_nhap=ten_dang_nhap).first():
            loi = 'Tên đăng nhập đã tồn tại, vui lòng chọn tên khác.'

        if loi:
            flash(loi, 'danger')
            return render_template('auth/register.html', form=request.form)

        # ── Tạo hội viên + tài khoản mới ──────────────────
        hoi_vien_moi = HoiVien(ho_ten=ho_ten, sdt=sdt, trang_thai='active')
        db.session.add(hoi_vien_moi)
        db.session.flush()  # để lấy ma_hv

        tk_moi = TaiKhoan(
            ten_dang_nhap=ten_dang_nhap,
            mat_khau=generate_password_hash(mat_khau),
            vai_tro='hoivien',
            trang_thai='active',
            ma_hv=hoi_vien_moi.ma_hv
        )
        db.session.add(tk_moi)
        db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form={})


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất thành công.', 'info')
    return redirect(url_for('auth.login'))
