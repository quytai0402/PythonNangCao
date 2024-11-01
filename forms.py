from flask_wtf import FlaskForm
import re
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import ValidationError
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

# Define categories directly in forms.py
INCOME_CATEGORIES = ['Lương', 'Thưởng', 'Đầu tư', 'Tiền Lì Xì', 'Khác']
EXPENSE_CATEGORIES = ['Ăn uống', 'Mua sắm', 'Giải trí', 'Di chuyển', 'Nhà ở', 'Tiền Điện', 'Tiền Nước', 'Khác']


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
    type = SelectField('Loại giao dịch', choices=[('Thu Nhập', 'Thu Nhập'), ('Chi Tiêu', 'Chi Tiêu')], validators=[DataRequired()])
    category = StringField('Mô Tả', validators=[DataRequired()])
    amount = IntegerField('Số Tiền', validators=[DataRequired()])
    date = DateField('Ngày', validators=[DataRequired()])
    description = StringField('Ghi chú') # Consider this addition
    submit = SubmitField('Lưu Giao Dịch')
    def validate_category(self, field):  # Line 44
        if self.type.data == 'Thu Nhập':  # Indented block starts here (4 spaces)
            if field.data not in INCOME_CATEGORIES:
                raise ValidationError('Invalid category for income.')
        elif self.type.data == 'Chi Tiêu':  # Indented block continues
            if field.data not in EXPENSE_CATEGORIES:
                raise ValidationError('Invalid category for expense.')

class EditTransactionForm(FlaskForm):
    type = SelectField('Loại giao dịch', choices=[('Thu Nhập', 'Thu Nhập'), ('Chi Tiêu', 'Chi Tiêu')], validators=[DataRequired()])
    category = StringField('Mô Tả', validators=[DataRequired()])
    amount = IntegerField('Số Tiền', validators=[DataRequired()])
    date = DateField('Ngày', validators=[DataRequired()])
    description = StringField('Ghi chú') # Added field to the edit form
    submit = SubmitField('Cập Nhật')

    def validate_category(self, field):
        if self.type.data == 'Thu Nhập':
            if field.data not in INCOME_CATEGORIES:  # Use the list defined above
                raise ValidationError('Invalid category for income.')
        elif self.type.data == 'Chi Tiêu':
            if field.data not in EXPENSE_CATEGORIES:  # Use the list defined above
                raise ValidationError('Invalid category for expense.')