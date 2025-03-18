from django.contrib import admin

from quizzes.models import Quiz, Question, QuizAttempt, Answer

# Register your models here.
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizAttempt)
admin.site.register(Answer)