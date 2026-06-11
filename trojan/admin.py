from django.contrib import admin

from .models import (
    Course,
    CourseBadge,
    CoursePicture,
    CourseReview,
    Faculty,
    Program,
    School,
    Student,
    Subject,
    Teacher,
    TeacherBadge,
    TeacherPicture,
    TeacherReview,
)

# Register your models here.
admin.site.register(Program)
admin.site.register(School)
admin.site.register(Faculty)
admin.site.register(Subject)
admin.site.register(CourseBadge)
admin.site.register(Course)
admin.site.register(CoursePicture)
admin.site.register(TeacherBadge)
admin.site.register(Teacher)
admin.site.register(TeacherPicture)
admin.site.register(Student)
admin.site.register(CourseReview)
admin.site.register(TeacherReview)
