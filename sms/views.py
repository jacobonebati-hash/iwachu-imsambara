from django.shortcuts import render, redirect
from django.contrib import messages

from members.models import Member

from .models import SMSMessage, SMSRecipient

from .sms_service import send_sms_api


# =========================================================
# SMS HISTORY
# =========================================================

def sms_history(request):

    sms_messages = SMSMessage.objects.all().order_by(
        "-created_at"
    )

    return render(
        request,
        "sms/sms_history.html",
        {
            "sms_messages": sms_messages
        }
    )


# =========================================================
# SEND SMS
# =========================================================

def send_sms(request):

    print("\n")
    print("########################################")
    print("🔥🔥 SEND_SMS VIEW IMEITWA 🔥🔥")
    print("REQUEST METHOD:", request.method)
    print("########################################")
    print("\n")


    # -----------------------------------------------------
    # ACTIVE MEMBERS
    # -----------------------------------------------------

    members = Member.objects.filter(
        status=True
    ).order_by("jina")


    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        print("🔥 POST REQUEST IMEFIKA KWENYE SEND_SMS")


        # -------------------------------------------------
        # GET SELECTED MEMBERS
        # -------------------------------------------------

        member_ids = request.POST.getlist(
            "member_ids"
        )

        message_text = request.POST.get(
            "message",
            ""
        ).strip()


        print("MEMBER IDS:", member_ids)

        print("MESSAGE:", message_text)


        # =================================================
        # VALIDATE MESSAGE
        # =================================================

        if not message_text:

            messages.error(
                request,
                "Tafadhali andika ujumbe."
            )

            return redirect("send_sms")


        # =================================================
        # VALIDATE MEMBERS
        # =================================================

        if not member_ids:

            messages.error(
                request,
                "Tafadhali chagua angalau mwanachama mmoja."
            )

            return redirect("send_sms")


        # =================================================
        # GET MEMBERS
        # =================================================

        selected_members = Member.objects.filter(
            id__in=member_ids,
            status=True
        )


        if not selected_members.exists():

            messages.error(
                request,
                "Hakuna mwanachama halali aliyechaguliwa."
            )

            return redirect("send_sms")


        # =================================================
        # CREATE SMS HISTORY
        # =================================================

        sms_message = SMSMessage.objects.create(

            message=message_text,

            total_recipients=selected_members.count(),

            status="pending"

        )


        # =================================================
        # CREATE RECIPIENT RECORDS
        # =================================================

        recipients = []


        for member in selected_members:

            print("================================")
            print("MEMBER:", member.jina)
            print("PHONE:", member.simu)
            print("MESSAGE:", message_text)
            print("================================")


            recipient = SMSRecipient.objects.create(

                sms=sms_message,

                member=member,

                phone=member.simu,

                status="pending"

            )


            recipients.append(member.simu)


        # =================================================
        # SEND SMS THROUGH TEXTBEE
        # =================================================

        print("🔥 SASA NINAPIGA send_sms_api()")

        result = send_sms_api(
            recipients,
            message_text
        )


        print("🔥 RESULT KUTOKA API:")

        print(result)

        print("================================")


        # =================================================
        # SUCCESS
        # =================================================

        if result.get("success"):

            sms_message.status = "sent"

            sms_message.save(
                update_fields=["status"]
            )


            # -------------------------------------------------
            # Mark all recipients as sent
            # -------------------------------------------------

            SMSRecipient.objects.filter(
                sms=sms_message
            ).update(
                status="sent"
            )


            count = selected_members.count()


            messages.success(
                request,
                f"SMS imetumwa kwa wanachama {count}."
            )


        # =================================================
        # FAILED
        # =================================================

        else:

            error = result.get(
                "error",
                "Unknown error"
            )


            sms_message.status = "failed"

            sms_message.save(
                update_fields=["status"]
            )


            # -------------------------------------------------
            # Mark recipients failed
            # -------------------------------------------------

            SMSRecipient.objects.filter(
                sms=sms_message
            ).update(

                status="failed",

                error_message=str(error)

            )


            messages.error(
                request,
                f"SMS haikutumwa: {error}"
            )


        return redirect("send_sms")


    # =====================================================
    # GET
    # =====================================================

    return render(
        request,
        "sms/send_sms.html",
        {
            "members": members
        }
    )