#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LaOpen 表单类
包含用户注册、登录等表单的定义和验证
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp

class RegistrationForm(FlaskForm):
    """User Registration Form"""
    nickname = StringField('NickName', validators=[
        DataRequired(message='NickName is required'),
        Length(min=2, max=20, message='NickName must be 2-20 characters')
    ])
    phone = StringField('Phone', validators=[
        DataRequired(message='Phone number is required'),
        Regexp(r'^1[3-9]\d{9}$', message='Please enter a valid phone number')
    ])
    password = PasswordField('PassWord', validators=[
        DataRequired(message='Password is required'),
        Length(min=6, max=20, message='Password must be 6-20 characters')
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """User Login Form"""
    phone = StringField('Phone', validators=[
        DataRequired(message='Phone number is required')
    ])
    password = PasswordField('PassWord', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')
