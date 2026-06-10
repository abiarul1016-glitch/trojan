from django.core.validators import RegexValidator
from django.db import models

# phone number validator - implementation to create custom phone number field
# can update to use django-phonenumber-field library, to handle better formatting
phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

# CHOICES
GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("NB", "Non-Binary"),
    ("O", "Other"),
    ("P", "Prefer not to say"),
]

PRONOUN_CHOICES = [
    ("he_him", "He/Him"),
    ("she_her", "She/Her"),
    ("they_them", "They/Them"),
    ("other", "Other/Ask"),
]

PROGRAM_CHOICES = [
    ("IB", "International Baccalaureate"),
    ("AP", "Advanced Placement"),
    ("S", "Sports"),
    ("SHSM", "Specialist High Skills Major"),
    ("FI", "French Immersion"),
    ("EF", "Extended French"),
    ("CM", "Core/Mainstream"),
]


# Create your models here.
class Program(models.Model):
    name = models.CharField(choices=PROGRAM_CHOICES, max_length=4)

    def __str__(self):
        return self.name


class School(models.Model):
    name = models.CharField(max_length=64)

    district = models.CharField()
    city = models.CharField(max_length=64)
    province = models.CharField(max_length=64)
    province_code = models.CharField(max_length=2)
    country = models.CharField(max_length=64)

    programs = models.ManyToManyField(Program, related_name="schools")

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField()
    school = models.ForeignKey(School, related_name="faculties")

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField()
    faculty = models.ForeignKey(Faculty, related_name="subjects")


class Course(models.Model):
    name = models.CharField()
    subject = models.ForeignKey(Subject, related_name="courses")
    code = models.CharField(unique=True)
    description = models.CharField()


class Teacher(models.Model):
    # basic info
    school = models.ForeignKey(on_delete=models.CASCADE, related_name="teachers")

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    pronouns = models.CharField(choices=PRONOUN_CHOICES, blank=True)

    date_of_birth = models.DateField()

    # contact info + location
    # has to start with p - regex
    pdsb_validator = RegexValidator(
        regex=r"^[pP]\d+$",
        message="PDSB number must start with 'p' followed by numbers.",
    )
    pdsb_number = models.CharField(max_length=20, unique=True)

    # automatically generated upon save if not included
    pdsb_email = models.EmailField(unique=True, blank=True)
    pdsb_direct_email = models.EmailField(unique=True, blank=True)

    personal_email = models.EmailField(unique=True, blank=True)

    school_phone_extension = models.PositiveIntegerField()
    personal_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )

    room_number = models.CharField(max_length=10, blank=True)
    home_address = models.TextField(blank=True)
    business_address = models.TextField(blank=True)

    # finance
    salary = models.DecimalField(decimal_places=2, blank=True, null=True)

    # socials + links
    sunshine_list = models.URLField(unique=True, blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    reddit = models.URLField(blank=True)
    snapchat = models.CharField(blank=True)
    discord = models.CharField(blank=True)

    # courses
    courses = models.ManyToManyField(Course, related_name="teachers")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} ({self.school})"

    def save(self, *args, **kwargs):

        # generate pdsb email using number and vice versa
        if self.pdsb_number and not self.pdsb_email:
            self.pdsb_email = f"p{self.pdsb_number}@pdsb.net"
        elif self.pdsb_email and not self.pdsb_number:
            self.pdsb_number = self.pdsb_email.split("@")[0]

        if not self.pdsb_direct_email:
            clean_first_name = self.first_name.lower().replace(" ", "")
            clean_last_name = self.first_name.lower().replace(" ", "")
            self.pdsb_direct_email = f"{clean_first_name}.{clean_last_name}@pdsb.net"

        super().save(*args, **kwargs)


class User(models.Model):
    pass


class Student(models.Model):
    school = models.ForeignKey(School, related_name="students")
    student_number = models.PositiveIntegerField(unique=True)
    grade = models.PositiveIntegerField()
    program = models.ManyToManyField(Program, related_name="students")
    
    @property
    def student_email(self):
        return f'{self.student_number}@pdsb.net'
