from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

# Lớp User định nghĩa mô hình người dùng trong cơ sở dữ liệu
class User(db.Model, UserMixin):
    # ID của người dùng, là khóa chính
    id = db.Column(db.Integer, primary_key=True)
    # Tên người dùng, phải duy nhất và không được để trống
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Mật khẩu của người dùng, không được để trống
    password = db.Column(db.String(120), nullable=False)
    # Họ của người dùng
    first_name = db.Column(db.String(50), nullable=False)
    # Tên của người dùng
    last_name = db.Column(db.String(50), nullable=False)
    # Email của người dùng, phải duy nhất và không được để trống
    email = db.Column(db.String(120), unique=True, nullable=False)

# Lớp Transaction định nghĩa mô hình giao dịch trong cơ sở dữ liệu
class Transaction(db.Model):
    # ID của giao dịch, là khóa chính
    id = db.Column(db.Integer, primary_key=True)
    # Loại giao dịch (ví dụ: chi tiêu, thu nhập), không được để trống
    type = db.Column(db.String(20), nullable=False)
    # Danh mục giao dịch (ví dụ: ăn uống, giải trí), không được để trống
    category = db.Column(db.String(50), nullable=False)
    # Số tiền giao dịch, không được để trống
    amount = db.Column(db.Integer, nullable=False)
    # Ngày thực hiện giao dịch, không được để trống
    date = db.Column(db.Date, nullable=False)
    # Mô tả về giao dịch (có thể để trống)
    description = db.Column(db.String(200))
    # user_id là khóa ngoại liên kết tới bảng User, không được để trống
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)