from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models, transaction

# phone number validator - implementation to create custom phone number field
# NOTE: can update to use django-phonenumber-field library, to handle better formatting
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

# might not need this, if user-inputted and just using foreign key
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


# school-related models
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

    programs = models.ManyToManyField(
        Program,
        help_text="The programs offered at this school.",
        related_name="schools",
    )

    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField()
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="faculties"
    )

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField()
    faculty = models.ForeignKey(
        Faculty, on_delete=models.PROTECT, related_name="subjects"
    )

    def __str__(self):
        return self.name


# course-related models


class CourseBadge(models.Model):
    COURSE_BADGE_TYPES = [
        ("TOP_COURSE", "top course"),
        ("LIKED_COURSE", "liked course"),
        ("L_COURSE", "L course"),
        ("TRASH_COURSE", "trash course"),
    ]

    type = models.CharField(
        help_text="A badge awarded to a course, depending on its standing among the student body.",
        choices=COURSE_BADGE_TYPES,
        blank=True,
    )


class Course(models.Model):
    # summaries
    summary = models.CharField(
        help_text="A human-generated summary of a teacher.", blank=True
    )
    generated_summary = models.CharField(
        help_text="A summary of a teacher generated using AI, based on the review text.",
        blank=True,
        default=summary,
    )

    name = models.CharField()
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name="courses"
    )
    code = models.CharField(unique=True)
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        help_text="Whether this course belongs to a specific program at the school.",
        related_name="courses",
    )

    # badge
    badge = models.ForeignKey(
        CourseBadge,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        related_name="courses",
    )

    description = models.CharField()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if self.name:
            self.name = self.name.capitalize()

        if self.code:
            self.code = self.code.upper()

        super().save(*args, **kwargs)


# helper function dictating the path the save course images
def course_directory_path(instance, filename):
    return f"course/{instance.course.code}/{filename}"


class CoursePictures(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="pictures"
    )
    picture = models.ImageField(upload_to=course_directory_path)


# teacher-related models
class TeacherBadge(models.Model):
    TEACHER_BADGE_TYPES = [
        ("TOP_TEACHER", "top teacher"),
        ("W_TEACHER", "W teacher"),
        ("L_TEACHER", "L teacher"),
        ("BOTTOM_TEACHER", "bottom teacher"),
    ]

    type = models.CharField(
        help_text="A badge awarded to a teacher, depending on their standing among the student body.",
        choices=TEACHER_BADGE_TYPES,
        blank=True,
    )


class Teacher(models.Model):
    # summaries
    summary = models.CharField(
        help_text="A human-generated summary of a teacher.", blank=True
    )
    generated_summary = models.CharField(
        help_text="A summary of a teacher generated using AI, based on the review text.",
        blank=True,
        default=summary,
    )

    # basic info
    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="teachers"
    )

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    gender = models.CharField(choices=GENDER_CHOICES, max_length=2)
    pronouns = models.CharField(choices=PRONOUN_CHOICES, blank=True)

    date_of_birth = models.DateField()

    # badge
    badge = models.ForeignKey(
        TeacherBadge,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
        related_name="teachers",
    )

    # contact info + location
    # has to start with p - regex
    pdsb_validator = RegexValidator(
        regex=r"^[pP]\d+$",
        message="PDSB number must start with 'p' followed by numbers.",
    )
    pdsb_number = models.CharField(max_length=20, unique=True)

    # automatically generated upon save if not included
    pdsb_email = models.EmailField(unique=True, blank=True)
    pdsb_direct_email = models.EmailField(
        help_text="The email that teachers check much more frequently than their regular one",
        unique=True,
        blank=True,
    )

    personal_email = models.EmailField(unique=True, blank=True)

    school_phone_extension = models.PositiveIntegerField()
    personal_number = models.CharField(
        validators=[phone_regex], max_length=17, blank=True
    )

    room_number = models.CharField(max_length=10, blank=True)
    home_address = models.TextField(blank=True)
    business_address = models.TextField(blank=True)

    # finance
    salary = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, default=None
    )

    # socials + links
    sunshine_list = models.URLField(
        help_text="The website containing teacher details for those who make over $100k. Fun Fact: Initially created to manufacture backlash against teacher to cut their funding.",
        unique=True,
        blank=True,
    )
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

    # setting profile picture - either the one explicitly set, or the first one in all the pictures
    @property
    def profile_picture(self):
        self.pictures.get(is_profile_picture=True) or self.pictures.first()

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


# helper function dictating the path the save teacher images
def teacher_directory_path(instance, filename):
    return f"teacher/{instance.teacher.pdsb_number}/{filename}"


class TeacherPictures(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="pictures"
    )
    picture = models.ImageField(upload_to=teacher_directory_path)

    is_profile_picture = models.BooleanField(
        help_text="Allows selection of profile picture from all the pictures.",
        default=False,
    )

    # save function, to ensure a teacher has one profile picture selected at a time
    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.is_profile_picture:
                self.teacher.pictures.filter(is_profile_picture=True).update(
                    is_profile_picture=False
                )

        super().save(*args, **kwargs)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    school = models.ForeignKey(
        School, on_delete=models.PROTECT, related_name="students"
    )
    student_number = models.PositiveIntegerField(unique=True)
    grade = models.PositiveIntegerField()
    program = models.ManyToManyField(Program, related_name="students")

    @property
    def student_email(self):
        return f"{self.student_number}@pdsb.net"


# review models
class BaseReview(models.Model):
    reviewer = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField()

    class Meta:
        abstract = True


class CourseReview(BaseReview):
    reviewer = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="course_reviews"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "course"], name="unique_course_student_review"
            ),
        ]


class TeacherReview(BaseReview):
    reviewer = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="teacher_reviews"
    )
    teacher = models.ForeignKey(
        Teacher, on_delete=models.CASCADE, related_name="reviews"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "teacher"], name="unique_teacher_student_review"
            ),
        ]
