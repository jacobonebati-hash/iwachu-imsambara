from django.db import models


class Member(models.Model):

    jina = models.CharField(max_length=100)

    simu = models.CharField(
        max_length=20,
        unique=True
    )

    kitongoji = models.CharField(
        max_length=100,
        blank=True
    )

    jinsia = models.CharField(
        max_length=20,
        blank=True
    )

    tarehe_ya_usajili = models.DateTimeField(
        auto_now_add=True
    )

    status = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.jina


class SMSMessage(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    # Wanachama watakaopokea SMS
    recipients = models.ManyToManyField(
        Member,
        related_name='sms_messages',
        blank=True
    )

    message = models.TextField()

    total_recipients = models.IntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.message[:30]