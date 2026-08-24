from django.shortcuts import render, redirect, get_object_or_404

from .models import Member, SMSMessage


# ==========================================
# HOME
# ==========================================

def home(request):

    total_members = Member.objects.count()

    total_sms = SMSMessage.objects.count()

    context = {
        "total_members": total_members,
        "total_sms": total_sms,
    }

    return render(
        request,
        "members/home.html",
        context
    )


# ==========================================
# REGISTER MEMBER
# ==========================================

def register_member(request):

    if request.method == "POST":

        jina = request.POST.get("jina", "").strip()
        simu = request.POST.get("simu", "").strip()
        kitongoji = request.POST.get("kitongoji", "").strip()
        jinsia = request.POST.get("jinsia", "").strip()

        Member.objects.create(
            jina=jina,
            simu=simu,
            kitongoji=kitongoji,
            jinsia=jinsia
        )

        return redirect("members_list")

    return render(
        request,
        "members/register.html"
    )


# ==========================================
# MEMBERS LIST
# ==========================================

def members_list(request):

    members = Member.objects.all().order_by("jina")

    return render(
        request,
        "members/members_list.html",
        {
            "members": members
        }
    )


# ==========================================
# MEMBER DETAIL
# ==========================================

def member_detail(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id
    )

    return render(
        request,
        "members/member_detail.html",
        {
            "member": member
        }
    )


# ==========================================
# EDIT MEMBER
# ==========================================

def edit_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id
    )

    if request.method == "POST":

        member.jina = request.POST.get(
            "jina",
            ""
        ).strip()

        member.simu = request.POST.get(
            "simu",
            ""
        ).strip()

        member.kitongoji = request.POST.get(
            "kitongoji",
            ""
        ).strip()

        member.jinsia = request.POST.get(
            "jinsia",
            ""
        ).strip()

        member.save()

        return redirect(
            "member_detail",
            member_id=member.id
        )

    return render(
        request,
        "members/edit_member.html",
        {
            "member": member
        }
    )


# ==========================================
# DELETE MEMBER
# ==========================================

def delete_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id
    )

    if request.method == "POST":

        member.delete()

        return redirect(
            "members_list"
        )

    return render(
        request,
        "members/delete_member.html",
        {
            "member": member
        }
    )