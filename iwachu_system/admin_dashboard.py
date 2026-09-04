from django.utils import timezone
from datetime import timedelta

from members.models import Member
from sms.models import SMSMessage


def dashboard_callback(request, context):

    # ==============================
    # MEMBERS
    # ==============================

    total_members = Member.objects.count()

    active_members = Member.objects.filter(
        status=True
    ).count()

    inactive_members = Member.objects.filter(
        status=False
    ).count()

    # ==============================
    # SMS
    # ==============================

    total_sms = SMSMessage.objects.count()

    # Kama model yako ina status
    try:
        sent_sms = SMSMessage.objects.filter(
            status="sent"
        ).count()

        failed_sms = SMSMessage.objects.filter(
            status="failed"
        ).count()

    except Exception:
        sent_sms = 0
        failed_sms = 0

    # ==============================
    # RECENT MEMBERS
    # ==============================

    recent_members = Member.objects.order_by(
        "-tarehe_ya_usajili"
    )[:5]

    # ==============================
    # RECENT SMS
    # ==============================

    recent_sms = SMSMessage.objects.order_by(
        "-created_at"
    )[:5]

    # ==============================
    # TODAY
    # ==============================

    today = timezone.localdate()

    today_members = Member.objects.filter(
        tarehe_ya_usajili__date=today
    ).count()

    # ==============================
    # SEND DATA TO DASHBOARD
    # ==============================

    context.update({

        "total_members": total_members,

        "active_members": active_members,

        "inactive_members": inactive_members,

        "total_sms": total_sms,

        "sent_sms": sent_sms,

        "failed_sms": failed_sms,

        "today_members": today_members,

        "recent_members": recent_members,

        "recent_sms": recent_sms,

    })

    return context