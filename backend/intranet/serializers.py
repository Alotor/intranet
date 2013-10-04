# -*- coding: utf-8 -*-

from django.conf import settings
from rest_framework import serializers

from . import models
from utils import get_consumed_days_for_user, get_requested_days_for_user
from django.core.exceptions import ValidationError

import datetime, calendar


class PickleField(serializers.WritableField):
    """
    Pickle objects.
    """
    def to_native(self, obj):
        return obj

    def from_native(self, data):
        if not isinstance(data, dict):
            raise ValidationError("Part data must be a json object")
        return data


class UserLogged(object):
    """
    An object represent a logged user.
    """
    def __init__(self, token, id, username, email, first_name, last_name, is_staff, is_superuser, date_joined, last_login):
        self.token = token
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.date_joined = date_joined
        self.last_login = last_login


class LoginSerializer(serializers.Serializer):
    """
    A login serializer class.
    """
    token = serializers.CharField(max_length=40)
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=256)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=256)
    last_name = serializers.CharField(max_length=256)
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    date_joined = serializers.DateTimeField()
    last_login = serializers.DateTimeField()

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update an UserLogged instance or
        create a new one.

        :param dict attrs: The attributes of an user.
        :param UserLogged instance: an existing UserLogged object.
        :return: a logged user instance.
        :rtype: UserLogged.
        """
        if instance is not None:
            instance.token = attrs.get("token", None)
            instance.id = attrs.get("id", instance.id)
            instance.username = attrs.get("username", instance.username)
            instance.email = attrs.get("email", instance.email)
            instance.first_name = attrs.get("first_name", instance.first_name)
            instance.last_name = attrs.get("last_name", instance.last_name)
            instance.is_staff = attrs.get("is_staff", instance.is_staff)
            instance.is_superuser = attrs.get("is_superuser", instance.is_superuser)
            instance.date_joined = attrs.get("date_joined", instance.date_joined)
            instance.last_login = attrs.get("last_login", instance.last_login)
            return instance
        return UserLogged(**attrs)


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project


class PartSerializer(serializers.ModelSerializer):
    data = PickleField()
    state_name = serializers.SerializerMethodField('get_state_name')
    special_days = serializers.SerializerMethodField('get_special_days')

    class Meta:
        model = models.Part
        read_only_fields = ('employee',)

    def get_state_name(self, obj):
        return obj.get_state_display()

    def get_special_days(self, obj):
        special_days = []
        initial_date = datetime.datetime(year=obj.year, month=obj.month, day=1)
        for day_counter in range(calendar.monthrange(obj.year,obj.month)[1]):
            requested_day = initial_date + datetime.timedelta(day_counter)
            special_day = models.SpecialDay.objects.filter(date=requested_day)
            special_day = special_day and special_day[0] or None
            is_weekend = datetime.date.weekday(requested_day) in [5, 6]

            if special_day:
                special_days.append(special_day)
            elif is_weekend:
                special_days.append(models.SpecialDay(
                    date = requested_day,
                    description = 'weekend',
                ))

        return [SpecialDaySerializer(d).data for d in special_days]


class HolidaysYearSerializer(serializers.ModelSerializer):
    consumed_days = serializers.SerializerMethodField('get_consumed_days')
    requested_days = serializers.SerializerMethodField('get_requested_days')
    total_days = serializers.SerializerMethodField('get_total_days')
    special_days = serializers.SerializerMethodField('get_special_days')

    class Meta:
        model = models.HolidaysYear

    def get_consumed_days(self, obj):
        return get_consumed_days_for_user(self.context['request'].user, obj)

    def get_requested_days(self, obj):
        return get_requested_days_for_user(self.context['request'].user, obj)

    def get_total_days(self, obj):
        return settings.HOLIDAYS_PER_YEAR

    def get_special_days(self, obj):
        return models.SpecialDay.objects.filter(date__year=obj.year).order_by('date').values()


class HolidaysRequestSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField('get_status_name')
    count_working_days = serializers.SerializerMethodField('get_count_working_days')

    class Meta:
        model = models.HolidaysRequest
        read_only_fields = ('employee',)

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_count_working_days(self, obj):
        return obj.count_working_days()


class DaySerializer(serializers.Serializer):
    day = serializers.IntegerField()
    month = serializers.IntegerField()
    year = serializers.IntegerField()

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """

        if instance is not None:
            instance.day = attrs.get('day', instance.day)
            instance.month = attrs.get('month', instance.month)
            instance.year = attrs.get('year', instance.year)
            return instance

        return datetime.datetime(**attrs)


class SpecialDaySerializer(serializers.ModelSerializer):
    date = DaySerializer(source='date')
    class Meta:
        model = models.SpecialDay
        fields = ('date', 'description')
