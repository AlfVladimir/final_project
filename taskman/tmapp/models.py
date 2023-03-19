import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

logger = logging.getLogger(__name__)


class Task(models.Model):
    """Задачи"""

    name = models.CharField(max_length=50, help_text="Название")
    content = models.TextField(help_text="Описание")
    is_complete = models.BooleanField(default=False, help_text="Выполнена")
    timestamp_create = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, help_text="Когда создана"
    )
    timestamp_done = models.DateTimeField(
        null=True, blank=True, editable=False, help_text="Когда выполнена"
    )
    history = HistoricalRecords()

    status = models.ForeignKey(
        to="tmapp.Status",
        on_delete=models.SET_NULL,
        related_name="tasks",
        blank=True,
        null=True,
        help_text="Статус",
    )

    executor = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tasks",
        blank=True,
        null=True,
        help_text="Исполнитель",
    )

    project = models.ForeignKey(
        to="tmapp.Project",
        on_delete=models.SET_NULL,
        related_name="tasks",
        blank=True,
        null=True,
        help_text="Проект",
    )

    sprint = models.ForeignKey(
        to="tmapp.Sprint",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tasks",
        help_text="Спринт",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Ставим время окончания, если задача сделана
        """

        logger.warning(f"Сработало сохранение у модели Task {str(timezone.now())}")

        if self.is_complete and self.timestamp_done is None:
            self.timestamp_done = timezone.localtime()

        if not self.is_complete and self.timestamp_done:
            self.timestamp_done = None

        if self.pk is not None:
            orig = Task.objects.get(id=self.id)
            if orig.status != self.status:
                if self.executor.email:
                    ...
                    # send_mail("Изменился статус задачи",
                    #     f"У задачи {self.id} поменялся статус на {self.status}",
                    #     "tessio@list.ru",
                    #     [f"{self.executor.email}"],
                    #     fail_silently=True,
                    # )

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "задача"
        verbose_name_plural = "задачи"
        ordering = ["id"]


class Project(models.Model):
    """Проекты"""

    name = models.CharField(max_length=50, help_text="Название")
    content = models.TextField(help_text="Описание")
    is_complete = models.BooleanField(default=False, help_text="Выполнен")
    timestamp_create = models.DateTimeField(
        auto_now_add=True, null=True, blank=True, help_text="Когда создан"
    )
    timestamp_done = models.DateTimeField(
        null=True, blank=True, editable=False, help_text="Когда выполнен"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        """
        Ставим время окончания, если проект закрыт
        """
        if self.is_complete and self.timestamp_done is None:
            self.timestamp_done = timezone.localtime()

        if not self.is_complete and self.timestamp_done:
            self.timestamp_done = None

        return super().save(*args, **kwargs)

    class Meta:
        verbose_name = "проект"
        verbose_name_plural = "проекты"
        ordering = ["id"]


class Sprint(models.Model):
    """Спринты"""

    name = models.CharField(max_length=50, help_text="Название")
    date_start = models.DateField(blank=False, help_text="Дата начала")
    date_end = models.DateField(blank=False, help_text="Дата окончания")
    project = models.ForeignKey(
        to="tmapp.Project",
        on_delete=models.PROTECT,
        related_name="sprints",
        help_text="Проект",
    )

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        lcdt = timezone.localdate()
        return self.date_start <= lcdt and lcdt <= self.date_end


class Status(models.Model):
    """Статус задачи"""

    name = models.CharField(
        max_length=50,
        help_text="Статус задачи",
    )

    parent_status = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="substatus",
        help_text="Родительский статус",
    )

    def get_relative_name(self):
        """Вычисляемое поле для вывода древовидной структуры"""
        str = self.name
        parent_status_obj = self.parent_status
        while parent_status_obj is not None:
            str = "---" + str
            parent_status_obj = parent_status_obj.parent_status
        return str

    def get_parent_id(self):
        """id корневого элемента"""
        parent_status_obj = self
        while parent_status_obj.parent_status is not None:
            parent_status_obj = parent_status_obj.parent_status
        return parent_status_obj.id

    class Meta:
        verbose_name = "статус"
        verbose_name_plural = "статусы"
        ordering = ["id"]

    def __str__(self):
        return self.name
