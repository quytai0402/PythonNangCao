from flask_wtf import FlaskForm
import re
from wtforms import ValidationError
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

def validate_name(form, field):
    # Kiểm tra tên chỉ chứa chữ cái và khoảng trắng, không chứa số hoặc ký tự đặc biệt
    if not re.match(r"^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ\s]+$", field.data):
        raise ValidationError('Tên chỉ được chứa các chữ cái và khoảng trắng.')

class SignupForm(FlaskForm):
    username = StringField('Tên đăng nhập', validators=[DataRequired(), Length(min=6, max=80)])
    password = PasswordField('Mật khẩu', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('Họ', validators=[DataRequired(), validate_name, Length(max=50)])
    last_name = StringField('Tên', validators=[DataRequired(), validate_name, Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Đăng ký')

    
class EditProfileForm(FlaskForm):
    first_name = StringField('Họ', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Tên', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Cập nhật hồ sơ')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Mật khẩu cũ', validators=[DataRequired()])
    new_password = PasswordField('Mật khẩu mới', validators=[DataRequired()])
    confirm_new_password = PasswordField('Xác nhận mật khẩu mới', validators=[DataRequired(), EqualTo('new_password', message='Mật khẩu không khớp')])
    submit = SubmitField('Đổi mật khẩu')

class TransactionForm(FlaskForm):
    type = SelectField('Loại', choices=[('Thu Nhập', 'Thu nhập'), ('Chi Tiêu', 'Chi tiêu')], validators=[DataRequired()])
    category = SelectField('Danh mục', choices=[], validators=[DataRequired()])
    amount = IntegerField('Số tiền', validators=[DataRequired(), NumberRange(min=1, message="Số tiền phải lớn hơn 0")])
    date = DateField('Ngày', format='%Y-%m-%d', validators=[DataRequired()])
    description = StringField('Mô tả', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Thêm giao dịch')

class EditTransactionForm(FlaskForm):
    type = SelectField('Loại', choices=[('Thu Nhập', 'Thu nhập'), ('Chi Tiêu', 'Chi tiêu')], validators=[DataRequired()])
    category = SelectField('Danh mục', choices=[], validators=[DataRequired()])
    amount = IntegerField('Số tiền', validators=[DataRequired(), NumberRange(min=1, message="Số tiền phải lớn hơn 0")])
    date = DateField('Ngày', format='%Y-%m-%d', validators=[DataRequired()])
    description = StringField('Mô tả', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Sửa giao dịch')


