from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import date, datetime, timedelta
from models import (db, HoiVien, CheckinOut, DangKiGoi, GoiTap,
                    BuoiHoc, BuoiPT, PT, LopHoc, DangKiBuoiHoc)
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    now   = datetime.now()

    role = current_user.vai_tro

    if role in ('admin', 'nhanvien'):
        # ── Thống kê tổng quan ──────────────────────────────
        tong_hv       = HoiVien.query.filter_by(trang_thai='active').count()
        hv_checkin    = CheckinOut.query.filter(CheckinOut.thoi_gian_checkout == None).count()
        goi_active    = DangKiGoi.query.filter_by(trang_thai='active').count()
        goi_het_han_30 = DangKiGoi.query.filter(
            DangKiGoi.trang_thai == 'active',
            DangKiGoi.ngay_het_han <= today + timedelta(30),
            DangKiGoi.ngay_het_han >= today
        ).count()
        buoi_pt_hom_nay = BuoiPT.query.filter(
            func.date(BuoiPT.thoi_gian_bat_dau) == today,
            BuoiPT.trang_thai == 'scheduled'
        ).count()
        tong_pt = PT.query.filter_by(trang_thai='active').count()

        # ── Checkin gần nhất ────────────────────────────────
        recent_checkins = (CheckinOut.query
                           .order_by(CheckinOut.thoi_gian_checkin.desc())
                           .limit(10).all())

        # ── Buổi PT hôm nay ─────────────────────────────────
        buoi_pt_today = (BuoiPT.query
                         .filter(func.date(BuoiPT.thoi_gian_bat_dau) == today)
                         .order_by(BuoiPT.thoi_gian_bat_dau).all())

        # ── Gói sắp hết hạn ─────────────────────────────────
        goi_sap_het = (DangKiGoi.query
                       .filter(DangKiGoi.trang_thai == 'active',
                               DangKiGoi.ngay_het_han <= today + timedelta(30),
                               DangKiGoi.ngay_het_han >= today)
                       .order_by(DangKiGoi.ngay_het_han).limit(10).all())

        # ── Buổi học hôm nay ────────────────────────────────
        buoi_hoc_today = BuoiHoc.query.filter_by(ngay_hoc=today).all()

        return render_template('dashboard/index.html',
            tong_hv=tong_hv, hv_checkin=hv_checkin,
            goi_active=goi_active, goi_het_han_30=goi_het_han_30,
            buoi_pt_hom_nay=buoi_pt_hom_nay, tong_pt=tong_pt,
            recent_checkins=recent_checkins,
            buoi_pt_today=buoi_pt_today,
            goi_sap_het=goi_sap_het,
            buoi_hoc_today=buoi_hoc_today,
            today=today
        )

    elif role == 'pt':
        pt_obj = current_user.pt
        # Lịch dạy của PT hôm nay
        my_buoi_pt = (BuoiPT.query
                      .filter_by(ma_pt=pt_obj.ma_pt)
                      .filter(func.date(BuoiPT.thoi_gian_bat_dau) == today)
                      .all())
        my_lop = LopHoc.query.filter_by(ma_pt=pt_obj.ma_pt, trang_thai='open').all()
        total_sessions = BuoiPT.query.filter_by(ma_pt=pt_obj.ma_pt, trang_thai='completed').count()
        upcoming_sessions = BuoiPT.query.filter_by(ma_pt=pt_obj.ma_pt, trang_thai='scheduled').count()

        return render_template('dashboard/pt.html',
            pt_obj=pt_obj, my_buoi_pt=my_buoi_pt,
            my_lop=my_lop, total_sessions=total_sessions,
            upcoming_sessions=upcoming_sessions, today=today)

    else:  # hoivien
        hv_obj = current_user.hoi_vien
        goi_ht = (DangKiGoi.query
                  .filter_by(ma_hv=hv_obj.ma_hv, trang_thai='active')
                  .first())
        my_buoi_pt = (BuoiPT.query
                      .filter_by(ma_hv=hv_obj.ma_hv)
                      .filter(BuoiPT.trang_thai.in_(['scheduled']))
                      .order_by(BuoiPT.thoi_gian_bat_dau).limit(5).all())
        my_buoi_hoc = (DangKiBuoiHoc.query
                       .filter_by(ma_hv=hv_obj.ma_hv, trang_thai='confirmed')
                       .order_by(DangKiBuoiHoc.thoi_gian_dk.desc())
                       .limit(5).all())
        chi_so_latest = (hv_obj.chi_so_list
                         .order_by(db.desc('ngay_do'))
                         .first())

        return render_template('dashboard/member.html',
            hv_obj=hv_obj, goi_ht=goi_ht,
            my_buoi_pt=my_buoi_pt, my_buoi_hoc=my_buoi_hoc,
            chi_so_latest=chi_so_latest, today=today)
