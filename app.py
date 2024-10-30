from flask import send_from_directory
import os  # Thư viện để làm việc với hệ thống tập tin và môi trường
import pandas as pd  # Thư viện xử lý dữ liệu
IntegrityError = None
import numpy as np  # Thư viện toán học
from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, send_file  # Các chức năng của Flask
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user  # Quản lý đăng nhập
from flask_sqlalchemy import SQLAlchemy  # ORM cho cơ sở dữ liệu
from werkzeug.security import generate_password_hash, check_password_hash  # Bảo mật mật khẩu
from dotenv import load_dotenv  # Tải biến môi trường từ file .env
from forms import TransactionForm, EditTransactionForm  # Các biểu mẫu cho giao dịch
from models import db, User, Transaction  # Các mô hình cơ sở dữ liệu
from datetime import datetime, date  # Làm việc với thời gian
import csv  # Xử lý tệp CSV
import calendar  # Xử lý lịch
from forms import SignupForm  # Các biểu mẫu cho đăng ký
from forms import EditProfileForm, ChangePasswordForm  # Các biểu mẫu cho chỉnh sửa hồ sơ và đổi mật khẩu
import matplotlib.pyplot as plt  # Vẽ biểu đồ
from flask_migrate import Migrate  # Migrate cơ sở dữ liệu
from datetime import timedelta

import locale  # Xử lý ngôn ngữ
import email_validator  # Kiểm tra định dạng email

load_dotenv()  # Tải các biến môi trường từ file .env
if not os.environ.get('SECRET_KEY'):  # Kiểm tra xem khóa bí mật có tồn tại không
    os.environ['SECRET_KEY'] = os.urandom(24).hex()  # Tạo khóa bí mật ngẫu nhiên

app = Flask(__name__)  # Khởi tạo ứng dụng Flask
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Cấu hình khóa bí mật
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dangnhap.db'  # Cấu hình kết nối đến cơ sở dữ liệu
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Không theo dõi thay đổi trên cơ sở dữ liệu
migrate = Migrate(app, db)  # Khởi tạo migrate với ứng dụng và cơ sở dữ liệu
db.init_app(app)  # Khởi tạo cơ sở dữ liệu với ứng dụng Flask

login_manager = LoginManager()  # Khởi tạo quản lý đăng nhập
login_manager.init_app(app)  # Gắn kết với ứng dụng
login_manager.login_view = 'login'  # Đặt trang đăng nhập
login_manager.login_message = "Vui lòng đăng nhập để truy cập trang này."

@app.template_filter('vnd_currency')
def vnd_currency_filter(value):
    return "{:,.0f} VNĐ".format(value)

@login_manager.user_loader
def load_user(user_id):  # Hàm tải người dùng theo ID
    return User.query.get(int(user_id))  # Trả về người dùng từ cơ sở dữ liệu

@app.route('/signup', methods=['GET', 'POST'])  # Route cho đăng ký người dùng mới
def signup():
    form = SignupForm()  # Khởi tạo biểu mẫu đăng ký
    if form.validate_on_submit():  # Nếu biểu mẫu hợp lệ
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')  # Mã hóa mật khẩu
        new_user = User(username=form.username.data, password=hashed_password,  # Tạo người dùng mới
                        first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        try:
            db.session.add(new_user)  # Thêm người dùng vào phiên làm việc
            db.session.commit()  # Cam kết thay đổi
            flash('Đăng ký thành công!', 'success')  # Thông báo thành công
            login_user(new_user)  # Đăng nhập người dùng mới
            return redirect(url_for('profile'))  # Chuyển hướng đến trang hồ sơ
        except IntegrityError:  # Nếu tên đăng nhập hoặc email đã tồn tại
            db.session.rollback()  # Hoàn tác thay đổi
            flash('Tên đăng nhập hoặc email đã tồn tại. Vui lòng thử lại.', 'danger')  # Thông báo lỗi
        except Exception as e:  # Xử lý lỗi khác
            db.session.rollback()  # Hoàn tác thay đổi
            flash(f'Đã xảy ra lỗi: {str(e)}', 'danger')  # Thông báo lỗi
    return render_template('signup.html', form=form)  # Render trang đăng ký


# Định nghĩa route /profile
@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user = current_user  # Lấy thông tin người dùng hiện tại
    return render_template('profile.html', user=user)  # Render trang hồ sơ

# Định nghĩa route /edit_profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user  # Lấy thông tin người dùng hiện tại
    form = EditProfileForm(obj=user)  # Khởi tạo biểu mẫu chỉnh sửa thông tin
    if form.validate_on_submit():  # Nếu biểu mẫu hợp lệ
        if (user.first_name == form.first_name.data and  # Kiểm tra nếu không có thay đổi nào
            user.last_name == form.last_name.data and
            user.email == form.email.data):
            flash('Không có thay đổi nào được thực hiện.', 'warning')  # Thông báo không có thay đổi
        else:
            user.first_name = form.first_name.data  # Cập nhật họ tên
            user.last_name = form.last_name.data
            user.email = form.email.data  # Cập nhật email
            db.session.commit()  # Cam kết thay đổi
            flash('Hồ sơ của bạn đã được cập nhật.', 'success')  # Thông báo thành công
            return redirect(url_for('profile'))  # Chuyển hướng đến trang hồ sơ
    return render_template('edit_profile.html', form=form)  # Render trang chỉnh sửa hồ sơ


@app.route('/delete/<int:transaction_id>', methods=['GET', 'POST'])  # Route xóa giao dịch
@login_required  # Yêu cầu người dùng phải đăng nhập
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)  # Lấy giao dịch hoặc trả về lỗi 404 nếu không tìm thấy

    if transaction.user_id != current_user.id:  # Kiểm tra quyền truy cập
        flash('Bạn không có quyền xoá giao dịch này.', 'danger')  # Thông báo lỗi
        return redirect(url_for('index'))  # Quay lại trang chính

    db.session.delete(transaction)  # Xóa giao dịch khỏi cơ sở dữ liệu
    db.session.commit()  # Cam kết thay đổi
    flash('Giao dịch đã bị xóa.', 'success')  # Thông báo thành công
    return redirect(url_for('index'))  # Quay lại trang chính

@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])  # Route chỉnh sửa giao dịch
@login_required  # Yêu cầu người dùng phải đăng nhập
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)  # Lấy giao dịch hoặc trả về lỗi 404 nếu không tìm thấy
    form = EditTransactionForm(obj=transaction)  # Khởi tạo form với dữ liệu của giao dịch hiện tại
    
    # Đặt lựa chọn danh mục dựa trên loại giao dịch
    if form.type.data == 'Thu Nhập':
        form.category.choices = [('Lương', 'Lương'), ('Thưởng', 'Thưởng'), ('Đầu tư', 'Đầu tư'), ('Khác', 'Khác')]
    elif form.type.data == 'Chi Tiêu':
        form.category.choices = [('Mua sắm', 'Mua sắm'), ('Giải trí', 'Giải trí'), ('Sức khỏe', 'Sức khỏe'), ('Đi lại', 'Đi lại'), ('Khác', 'Khác')]
    
    if form.validate_on_submit():  # Nếu form hợp lệ
        transaction.type = form.type.data  # Cập nhật loại giao dịch
        transaction.category = form.category.data  # Cập nhật danh mục
        transaction.amount = int(form.amount.data)  # Cập nhật số tiền và chuyển đổi sang số nguyên
        transaction.date = form.date.data  # Cập nhật ngày
        transaction.description = form.description.data  # Cập nhật mô tả
        db.session.commit()  # Cam kết thay đổi
        flash('Giao dịch đã được cập nhật thành công!', 'success')  # Thông báo thành công
        return redirect(url_for('index'))  # Quay lại trang chính
    else:
        for field, errors in form.errors.items():  # Kiểm tra lỗi trong form
            for error in errors:
                flash(f"Lỗi trong trường {getattr(form, field).label.text}: {error}", 'danger')  # Thông báo lỗi
    
    # Định dạng số tiền không có phần thập phân
    formatted_amount = "{:,.0f}".format(transaction.amount)
    
    return render_template('edit.html', form=form, transaction=transaction, formatted_amount=formatted_amount)  # Render trang chỉnh sửa

@app.route('/login', methods=['GET', 'POST'])  # Route đăng nhập
def login():
    if request.method == 'POST':  # Nếu là yêu cầu POST
        username = request.form['username']  # Lấy tên người dùng từ form
        password = request.form['password']  # Lấy mật khẩu từ form
        user = User.query.filter_by(username=username).first()  # Tìm người dùng theo tên

        if user and check_password_hash(user.password, password):  # Kiểm tra người dùng và mật khẩu
            login_user(user)  # Đăng nhập người dùng
            # flash('Đăng nhập thành công!', 'success')  # Thông báo thành công
            return redirect(url_for('dashboard'))  # Chuyển hướng đến trang chính
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng.', 'danger')  # Thông báo lỗi

    return render_template('login.html')  # Render trang đăng nhập

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Truy vấn dữ liệu chi tiêu từ cơ sở dữ liệu
    expenses = db.session.query(Transaction.category, db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='expense').group_by(Transaction.category).all()
    expense_data = {category: amount for category, amount in expenses}
    
    # Truy vấn dữ liệu thu nhập từ cơ sở dữ liệu
    incomes = db.session.query(Transaction.category, db.func.sum(Transaction.amount)).filter_by(user_id=current_user.id, type='income').group_by(Transaction.category).all()
    income_data = {category: amount for category, amount in incomes}
    
    return render_template('dashboard.html', expense_data=expense_data, income_data=income_data)


@app.route('/logout')  # Route đăng xuất
@login_required  # Yêu cầu người dùng phải đăng nhập
def logout():
    logout_user()  # Đăng xuất người dùng
    flash('Đăng xuất thành công', 'success')  # Thông báo thành công
    return redirect(url_for('login'))  # Chuyển hướng đến trang đăng nhập

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    today = date.today()  # Lấy ngày hôm nay
    start_date = today - timedelta(days=30)  # Ngày bắt đầu là 30 ngày trước
    end_date = today  # Ngày kết thúc là hôm nay
    transactions = []
    total_income = 0
    total_expense = 0
    balance = 0
    transactions_json = '[]'
    show_export_button = False  # Khởi tạo show_export_button là False

    if request.method == 'POST':
        start_date_str = request.form.get('start_date')  # Lấy ngày bắt đầu từ form
        end_date_str = request.form.get('end_date')  # Lấy ngày kết thúc từ form

        if start_date_str:  # Nếu ngày bắt đầu có giá trị
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()  # Chuyển đổi chuỗi thành ngày
            except ValueError:
                flash('Định dạng ngày bắt đầu không hợp lệ.', 'danger')  # Thông báo lỗi định dạng ngày
                return redirect(url_for('report'))

        if end_date_str:  # Nếu ngày kết thúc có giá trị
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()  # Chuyển đổi chuỗi thành ngày
            except ValueError:
                flash('Định dạng ngày kết thúc không hợp lệ.', 'danger')  # Thông báo lỗi định dạng ngày
                return redirect(url_for('report'))

        if start_date > end_date:  # Kiểm tra nếu ngày bắt đầu lớn hơn ngày kết thúc
            flash('Ngày bắt đầu không thể lớn hơn ngày kết thúc.', 'danger')  # Thông báo lỗi
            return redirect(url_for('report'))

        transactions = Transaction.query.filter(  # Lọc giao dịch dựa trên ngày
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).all()

        total_income = sum(t.amount for t in transactions if t.type == 'Thu Nhập')  # Tính tổng thu nhập
        total_expense = sum(t.amount for t in transactions if t.type == 'Chi Tiêu')  # Tính tổng chi tiêu
        balance = total_income - total_expense  # Tính số dư
        show_export_button = True  # Hiển thị nút export sau khi lọc

    transactions_json = jsonify([{
        'type': t.type,
        'category': t.category,
        'amount': t.amount,
        'date': t.date.strftime('%Y-%m-%d'),
        'description': t.description
    } for t in transactions]).get_data(as_text=True)  # Chuyển đổi giao dịch thành JSON

    return render_template('report.html', transactions=transactions,
                           total_income=total_income, total_expense=total_expense,
                           balance=balance, start_date=start_date.strftime('%Y-%m-%d'),
                           end_date=end_date.strftime('%Y-%m-%d'), transactions_json=transactions_json,
                           show_export_button=show_export_button)  # Thêm show_export_button


@app.route('/export_report', methods=['GET'])
@login_required
def export_report():
    start_date_str = request.args.get('start_date')  # Lấy ngày bắt đầu từ query string
    end_date_str = request.args.get('end_date')  # Lấy ngày kết thúc từ query string

    if not start_date_str or not end_date_str:  # Nếu không có ngày bắt đầu hoặc kết thúc
        today = date.today()  # Lấy ngày hôm nay
        start_date = today - timedelta(days=30)  # Ngày bắt đầu là 30 ngày trước
        end_date = today  # Ngày kết thúc là hôm nay
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()  # Chuyển đổi chuỗi thành ngày
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()  # Chuyển đổi chuỗi thành ngày
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Định dạng ngày không hợp lệ.'}), 400  # Thông báo lỗi

    transactions = Transaction.query.filter(  # Lọc giao dịch dựa trên ngày
        Transaction.user_id == current_user.id,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).all()

    if not transactions:  # Nếu không có giao dịch nào
        return jsonify({'status': 'error', 'message': 'Không có giao dịch nào trong khoảng thời gian này.'}), 404  # Thông báo lỗi

    total_income = sum(t.amount for t in transactions if t.type == 'Thu Nhập')  # Tính tổng thu nhập
    total_expense = sum(t.amount for t in transactions if t.type == 'Chi Tiêu')  # Tính tổng chi tiêu
    balance = total_income - total_expense  # Tính số dư

    # Tạo tên tệp với định dạng yêu cầu
    filename = f'Báo Cáo Từ {start_date_str} Đến {end_date_str}.csv'
    csv_file_path = os.path.join(app.instance_path, filename)  # Đường dẫn tệp CSV

    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)  # Khởi tạo writer cho tệp CSV
        # Viết tiêu đề
        writer.writerow(["Loại", "Danh Mục", "Số Tiền", "Ngày", "Mô Tả"])
        for transaction in transactions:  # Ghi từng giao dịch vào tệp
            amount_vnd = "{:,.0f} VNĐ".format(transaction.amount).replace(",", ".")
            writer.writerow([transaction.type, transaction.category, amount_vnd, transaction.date.strftime('%Y-%m-%d'), transaction.description])
        
        # Thêm tổng hợp vào tệp
        writer.writerow([])
        total_income_vnd = "{:,.0f} VNĐ".format(total_income).replace(",", ".")
        total_expense_vnd = "{:,.0f} VNĐ".format(total_expense).replace(",", ".")
        balance_vnd = "{:,.0f} VNĐ".format(balance).replace(",", ".")
        writer.writerow(["Tổng Thu Nhập", total_income_vnd])  # Ghi tổng thu nhập
        writer.writerow(["Tổng Chi Tiêu", total_expense_vnd])  # Ghi tổng chi tiêu
        writer.writerow(["Số Dư", balance_vnd])  # Ghi số dư

    return jsonify({'status': 'success', 'message': 'Tải xuống thành công!', 'file_url': url_for('download_file', filename=filename)})


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.instance_path, filename, as_attachment=True)  # Tải tệp xuống


@app.route('/')  # Route trang chính
@login_required  # Yêu cầu người dùng phải đăng nhập
def index():
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()  # Lấy tất cả giao dịch của người dùng
    return render_template('index.html', transactions=transactions, today=date.today())  # Render trang chính với danh sách giao dịch

@app.route('/add', methods=['GET', 'POST'])  # Route thêm giao dịch
@login_required  # Yêu cầu người dùng phải đăng nhập
def add_transaction():
    form = TransactionForm()  # Khởi tạo form cho giao dịch mới
    
    # Đặt lựa chọn danh mục dựa trên loại giao dịch
    if form.type.data == 'Thu Nhập':
        form.category.choices = [('Lương', 'Lương'), ('Thưởng', 'Thưởng'), ('Đầu tư', 'Đầu tư'), ('Khác', 'Khác')]
    elif form.type.data == 'Chi Tiêu':
        form.category.choices = [('Mua sắm', 'Mua sắm'), ('Giải trí', 'Giải trí'), ('Sức khỏe', 'Sức khỏe'), ('Đi lại', 'Đi lại'), ('Khác', 'Khác')]
    
    if form.validate_on_submit():  # Nếu form hợp lệ
        transaction = Transaction(
            type=form.type.data,  # Loại giao dịch
            category=form.category.data,  # Danh mục giao dịch
            amount=form.amount.data,  # Số tiền giao dịch
            date=form.date.data,  # Ngày giao dịch
            description=form.description.data,  # Mô tả giao dịch
            user_id=current_user.id  # ID người dùng
        )  # Tạo giao dịch mới với dữ liệu từ form
        db.session.add(transaction)  # Thêm giao dịch vào phiên làm việc
        db.session.commit()  # Cam kết thay đổi
        flash('Giao dịch đã được thêm thành công!', 'success')  # Thông báo thành công
        return redirect(url_for('index'))  # Quay lại trang chính
    else:
        for field, errors in form.errors.items():  # Kiểm tra lỗi trong form
            for error in errors:
                flash(f"Lỗi trong trường {getattr(form, field).label.text}: {error}", 'danger')  # Thông báo lỗi
    return render_template('add.html', form=form)  # Render trang thêm giao dịch



def analyze_data(df):
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Chuyển đổi cột 'amount' thành số
    df = df.dropna(subset=['amount'])  # Xóa các hàng có giá trị 'amount' là NaN

    expense_df = df[df['type'].str.lower() == 'chi tiêu']  # Lấy dữ liệu chi tiêu
    income_df = df[df['type'].str.lower() == 'thu nhập']  # Lấy dữ liệu thu nhập

    def calculate_stats(df):
        if df.empty:
            return pd.Series({'sum': 0, 'mean': 0, 'max': 0, 'min': 0})  # Trả về các giá trị mặc định nếu DataFrame trống
        return df['amount'].agg(['sum', 'mean', 'max', 'min'])  # Tính tổng, trung bình, giá trị lớn nhất và nhỏ nhất

    monthly_expense_stats = expense_df.resample('M').apply(calculate_stats).fillna(0)  # Thống kê chi tiêu hàng tháng
    monthly_income_stats = income_df.resample('M').apply(calculate_stats).fillna(0)  # Thống kê thu nhập hàng tháng

    # Đảm bảo chỉ số được làm phẳng nếu MultiIndex
    if isinstance(monthly_expense_stats.index, pd.MultiIndex):
        monthly_expense_stats.index = monthly_expense_stats.index.to_flat_index()
    if isinstance(monthly_income_stats.index, pd.MultiIndex):
        monthly_income_stats.index = monthly_income_stats.index.to_flat_index()

    # Kiểm tra xem cột 'sum' có tồn tại trong cả hai DataFrame
    if 'sum' not in monthly_expense_stats.columns:
        monthly_expense_stats['sum'] = 0
    if 'sum' not in monthly_income_stats.columns:
        monthly_income_stats['sum'] = 0

    combined_index = monthly_expense_stats[monthly_expense_stats['sum'] != 0].index.union(
        monthly_income_stats[monthly_income_stats['sum'] != 0].index
    )

    # Xử lý trường hợp không có dữ liệu
    if combined_index.empty:
        return pd.DataFrame(columns=[
            'Tháng', 
            'Tổng Chi Tiêu', 
            'Chi Tiêu Trung Bình', 
            'Chi Tiêu Cao Nhất', 
            'Chi Tiêu Thấp Nhất', 
            'Tổng Thu Nhập', 
            'Thu Nhập Trung Bình', 
            'Thu Nhập Cao Nhất', 
            'Thu Nhập Thấp Nhất'
        ])

    monthly_expense_stats = monthly_expense_stats.reindex(combined_index, fill_value=0)  # Reindex với index kết hợp
    monthly_income_stats = monthly_income_stats.reindex(combined_index, fill_value=0)  # Reindex với index kết hợp

    analysis_df = pd.DataFrame({
        'Tháng': combined_index,
        'Tổng Chi Tiêu': monthly_expense_stats['sum'],
        'Chi Tiêu Trung Bình': monthly_expense_stats['mean'] if 'mean' in monthly_expense_stats.columns else 0,
        'Chi Tiêu Cao Nhất': monthly_expense_stats['max'] if 'max' in monthly_expense_stats.columns else 0,
        'Chi Tiêu Thấp Nhất': monthly_expense_stats['min'] if 'min' in monthly_expense_stats.columns else 0,
        'Tổng Thu Nhập': monthly_income_stats['sum'],
        'Thu Nhập Trung Bình': monthly_income_stats['mean'] if 'mean' in monthly_income_stats.columns else 0,
        'Thu Nhập Cao Nhất': monthly_income_stats['max'] if 'max' in monthly_income_stats.columns else 0,
        'Thu Nhập Thấp Nhất': monthly_income_stats['min'] if 'min' in monthly_income_stats.columns else 0,
    })

    return analysis_df  # Trả về DataFrame phân tích


@app.route('/analysis', methods=['GET'])
@login_required
def analysis():
    transactions = Transaction.query.filter_by(user_id=current_user.id).all()  # Lấy tất cả giao dịch của người dùng
    data = [{
        'id': t.id,
        'type': t.type,
        'category': t.category,
        'amount': t.amount,
        'date': t.date,
        'description': t.description
    } for t in transactions]  # Biến đổi dữ liệu giao dịch thành danh sách từ điển

    df = pd.DataFrame(data)  # Khởi tạo DataFrame từ dữ liệu

    if 'date' not in df.columns or df.empty or 'amount' not in df.columns:  # Kiểm tra điều kiện không có dữ liệu
        flash('Không có dữ liệu để phân tích.', 'danger')  # Thông báo không có dữ liệu
        return redirect(url_for('index'))  # Quay lại trang chính

    df['date'] = pd.to_datetime(df['date'])  # Chuyển đổi cột 'date' thành định dạng datetime
    df.set_index('date', inplace=True)  # Đặt cột 'date' làm chỉ số

    selected_month = request.args.get('month')  # Lấy tháng được chọn từ query string

    if selected_month:  # Nếu có tháng được chọn
        df = df[df.index.month == int(selected_month)]  # Lọc theo tháng

    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Chuyển đổi cột 'amount' thành số
    df.dropna(subset=['amount'], inplace=True)  # Xóa các hàng có giá trị 'amount' là NaN

    analysis_df = analyze_data(df)  # Phân tích dữ liệu

    expense_df = df[df['type'].str.lower() == 'chi tiêu']  # Lấy dữ liệu chi tiêu
    income_df = df[df['type'].str.lower() == 'thu nhập']  # Lấy dữ liệu thu nhập

    expense_data = {}
    if not expense_df.empty:
        expense_data = {str(date): amount for date, amount in expense_df['amount'].resample('D').sum().items()}  # Tính tổng chi tiêu hàng ngày

    income_data = {}
    if not income_df.empty:
        income_data = {str(date): amount for date, amount in income_df['amount'].resample('D').sum().items()}  # Tính tổng thu nhập hàng ngày

    analysis_dict = analysis_df.reset_index().to_dict(orient='records')  # Chuyển DataFrame phân tích thành danh sách từ điển

    for row in analysis_dict:
        if 'Tháng' in row:  # Kiểm tra xem cột 'Tháng' có tồn tại không
            try:
                row['Tháng'] = pd.to_datetime(row['Tháng'], format='%B').month  # Chuyển đổi tên tháng thành số tháng
            except (ValueError, TypeError):  # Xử lý lỗi nếu giá trị 'Tháng' không hợp lệ
                pass  # Hoặc thực hiện một hành động khác nếu cần thiết

    return render_template('analysis.html',  # Render trang phân tích
                           expense_data=expense_data,
                           income_data=income_data,
                           selected_month=selected_month,
                           analysis_dict=analysis_dict)


# Đổi mật khẩu
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()  # Khởi tạo biểu mẫu đổi mật khẩu
    if form.validate_on_submit():  # Nếu biểu mẫu hợp lệ
        user = current_user  # Lấy người dùng hiện tại
        if check_password_hash(user.password, form.old_password.data):  # Kiểm tra mật khẩu cũ
            user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256')  # Mã hóa mật khẩu mới
            db.session.commit()  # Cam kết thay đổi
            flash('Mật khẩu của bạn đã được thay đổi.', 'success')  # Thông báo thành công
        else:
            flash('Mật khẩu cũ không đúng.', 'danger')  # Thông báo mật khẩu cũ không đúng
    return render_template('change_password.html', form=form)  # Render trang đổi mật khẩu


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo bảng nếu chúng không tồn tại
    app.run(debug=True)  # Chạy ứng dụng Flask trong chế độ debug
