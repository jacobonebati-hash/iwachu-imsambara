from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

import pandas as pd
import re

from .models import Member, SMSMessage


# =========================================================
# HELPERS: EXCEL IMPORT
# =========================================================

NAME_ALIASES = {
    "jina",
    "jina la mwanachama",
    "jina la member",
    "name",
    "full name",
    "member name",
}

PHONE_ALIASES = {
    "simu",
    "namba ya simu",
    "phone",
    "phone number",
    "mobile",
    "mobile number",
    "telephone",
    "telephone number",
}

KITONGOJI_ALIASES = {
    "kitongoji",
    "mtaa",
    "street",
    "village",
}

GENDER_ALIASES = {
    "jinsia",
    "gender",
    "sex",
}


def _clean_header(value):
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _find_column(columns, aliases):
    cleaned = {_clean_header(c): c for c in columns}

    for alias in aliases:
        if alias in cleaned:
            return cleaned[alias]

    # Fuzzy matching for common variations.
    for cleaned_name, original in cleaned.items():
        if any(alias in cleaned_name for alias in aliases):
            return original

    return None


def _find_member_sheet(excel_file):
    """
    Finds the first worksheet that contains both a member-name
    column and a phone-number column. This allows the importer
    to work with the user's existing MKEKA Excel where the real
    headers are on row 4.
    """
    excel = pd.ExcelFile(excel_file)

    for sheet_name in excel.sheet_names:
        raw = pd.read_excel(
            excel,
            sheet_name=sheet_name,
            header=None,
            nrows=20,
        )

        for header_row in range(min(20, len(raw))):
            row = raw.iloc[header_row].tolist()

            name_col = None
            phone_col = None

            for index, value in enumerate(row):
                header = _clean_header(value)

                if header in NAME_ALIASES or (
                    "jina" in header and "mwanachama" in header
                ):
                    name_col = index

                if header in PHONE_ALIASES or (
                    "namba" in header and "simu" in header
                ):
                    phone_col = index

            if name_col is not None and phone_col is not None:
                return sheet_name, header_row

    raise ValueError(
        "Excel haijawa na columns za jina la mwanachama "
        "na namba ya simu."
    )


def _clean_cell(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_tanzania_phone(value):
    """
    Converts common Tanzania formats into +255XXXXXXXXX.
    """
    if pd.isna(value):
        return ""

    # Excel can read large phone numbers as float.
    if isinstance(value, float) and value.is_integer():
        value = int(value)

    phone = str(value).strip()

    # Remove Excel's trailing .0
    phone = re.sub(r"\.0$", "", phone)

    # Remove spaces and common separators.
    phone = re.sub(r"[\s\-\(\)]", "", phone)

    if phone.startswith("00"):
        phone = "+" + phone[2:]

    if phone.startswith("+255"):
        normalized = phone

    elif phone.startswith("255"):
        normalized = "+" + phone

    elif phone.startswith("0"):
        normalized = "+255" + phone[1:]

    elif re.fullmatch(r"[67]\d{8}", phone):
        normalized = "+255" + phone

    else:
        return ""

    # Mobile number used by this system: +255 followed by 9 digits.
    if not re.fullmatch(r"\+255\d{9}", normalized):
        return ""

    return normalized


# =========================================================
# IMPORT MEMBERS FROM EXCEL
# =========================================================

def import_members(request):

    if request.method != "POST":
        return render(
            request,
            "members/import_members.html",
        )

    excel_file = request.FILES.get("excel_file")

    if not excel_file:
        messages.error(
            request,
            "Tafadhali chagua Excel file kwanza.",
        )
        return redirect("import_members")

    filename = excel_file.name.lower()

    if not filename.endswith((".xlsx", ".xls")):
        messages.error(
            request,
            "Tafadhali upload Excel file ya .xlsx au .xls.",
        )
        return redirect("import_members")

    try:
        sheet_name, header_row = _find_member_sheet(excel_file)

        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            header=header_row,
        )

        # Remove completely empty rows.
        df = df.dropna(how="all")

        name_col = _find_column(df.columns, NAME_ALIASES)
        phone_col = _find_column(df.columns, PHONE_ALIASES)
        kitongoji_col = _find_column(df.columns, KITONGOJI_ALIASES)
        gender_col = _find_column(df.columns, GENDER_ALIASES)

        if not name_col or not phone_col:
            raise ValueError(
                "Columns za Jina na Simu hazikupatikana."
            )

        existing_phones = set(
            Member.objects.values_list("simu", flat=True)
        )

        seen_in_file = set()

        valid_rows = []
        duplicate_count = 0
        invalid_count = 0
        empty_count = 0

        for _, row in df.iterrows():

            jina = _clean_cell(row.get(name_col))
            simu = normalize_tanzania_phone(row.get(phone_col))

            if not jina and not simu:
                empty_count += 1
                continue

            if not jina or not simu:
                invalid_count += 1
                continue

            if simu in existing_phones or simu in seen_in_file:
                duplicate_count += 1
                continue

            kitongoji = (
                _clean_cell(row.get(kitongoji_col))
                if kitongoji_col
                else ""
            )

            jinsia = (
                _clean_cell(row.get(gender_col))
                if gender_col
                else ""
            )

            valid_rows.append(
                Member(
                    jina=jina[:100],
                    simu=simu,
                    kitongoji=kitongoji[:100],
                    jinsia=jinsia[:20],
                    status=True,
                )
            )

            seen_in_file.add(simu)

        with transaction.atomic():
            Member.objects.bulk_create(
                valid_rows,
                batch_size=500,
            )

        messages.success(
            request,
            (
                f"Excel imeingizwa kikamilifu! "
                f"Wameongezwa: {len(valid_rows)} | "
                f"Duplicates: {duplicate_count} | "
                f"Zisizo sahihi: {invalid_count}"
            ),
        )

        # Extra information for the user.
        if empty_count:
            messages.info(
                request,
                f"Rows tupu zilizorukwa: {empty_count}.",
            )

        messages.info(
            request,
            f"Worksheet iliyotumika: {sheet_name}.",
        )

    except IntegrityError:
        messages.error(
            request,
            "Kuna namba zinazojirudia kwenye database. "
            "Excel haijaingizwa yote.",
        )

    except Exception as error:
        messages.error(
            request,
            f"Excel haijaingizwa: {error}",
        )

    return redirect("members_list")


# =========================================================
# DOWNLOAD EXCEL TEMPLATE
# =========================================================

def download_member_template(request):

    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Members"

    headers = [
        "JINA LA MWANACHAMA",
        "NAMBA YA SIMU",
        "KITONGOJI",
        "JINSIA",
    ]

    sheet.append(headers)

    sample_rows = [
        [
            "NEBATI NEHEMIA JACOBO",
            "0698162036",
            "MSAMBARA",
            "Mwanaume",
        ],
        [
            "KABABAYE",
            "0790846187",
            "MSAMBARA",
            "Mwanaume",
        ],
    ]

    for row in sample_rows:
        sheet.append(row)

    for column in sheet.columns:
        maximum = max(
            len(str(cell.value or ""))
            for cell in column
        )
        sheet.column_dimensions[
            column[0].column_letter
        ].width = min(maximum + 4, 35)

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="IWACHU_Members_Template.xlsx"'
    )

    workbook.save(response)

    return response


# =========================================================
# HOME
# =========================================================

def home(request):

    total_members = Member.objects.count()
    total_sms = SMSMessage.objects.count()

    active_members = Member.objects.filter(
        status=True
    ).count()

    return render(
        request,
        "members/home.html",
        {
            "total_members": total_members,
            "total_sms": total_sms,
            "active_members": active_members,
        },
    )


# =========================================================
# REGISTER MEMBER
# =========================================================

def register_member(request):

    if request.method == "POST":

        jina = request.POST.get("jina", "").strip()
        simu = request.POST.get("simu", "").strip()
        kitongoji = request.POST.get("kitongoji", "").strip()
        jinsia = request.POST.get("jinsia", "").strip()

        if not jina or not simu:
            messages.error(
                request,
                "Jina na namba ya simu vinahitajika.",
            )
            return render(
                request,
                "members/register.html",
            )

        simu = normalize_tanzania_phone(simu)

        if not simu:
            messages.error(
                request,
                "Namba ya simu si sahihi. Mfano: 0712345678.",
            )
            return render(
                request,
                "members/register.html",
            )

        if Member.objects.filter(simu=simu).exists():
            messages.error(
                request,
                "Namba hii tayari imesajiliwa.",
            )
            return render(
                request,
                "members/register.html",
            )

        Member.objects.create(
            jina=jina,
            simu=simu,
            kitongoji=kitongoji,
            jinsia=jinsia,
        )

        messages.success(
            request,
            f"{jina} amesajiliwa kikamilifu.",
        )

        return redirect("members_list")

    return render(
        request,
        "members/register.html",
    )


# =========================================================
# MEMBERS LIST
# =========================================================

def members_list(request):

    search = request.GET.get("search", "").strip()

    members = Member.objects.all().order_by("jina")

    if search:
        from django.db.models import Q

        members = members.filter(
            Q(jina__icontains=search)
            | Q(simu__icontains=search)
            | Q(kitongoji__icontains=search)
        )

    return render(
        request,
        "members/members_list.html",
        {
            "members": members,
            "search": search,
        },
    )


# =========================================================
# MEMBER DETAIL
# =========================================================

def member_detail(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id,
    )

    return render(
        request,
        "members/member_detail.html",
        {
            "member": member,
        },
    )


# =========================================================
# EDIT MEMBER
# =========================================================

def edit_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id,
    )

    if request.method == "POST":

        member.jina = request.POST.get(
            "jina",
            "",
        ).strip()

        simu = request.POST.get(
            "simu",
            "",
        ).strip()

        member.simu = normalize_tanzania_phone(simu)

        member.kitongoji = request.POST.get(
            "kitongoji",
            "",
        ).strip()

        member.jinsia = request.POST.get(
            "jinsia",
            "",
        ).strip()

        member.save()

        messages.success(
            request,
            "Taarifa za mwanachama zimebadilishwa.",
        )

        return redirect(
            "member_detail",
            member_id=member.id,
        )

    return render(
        request,
        "members/edit_member.html",
        {
            "member": member,
        },
    )


# =========================================================
# DELETE MEMBER
# =========================================================

def delete_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id,
    )

    if request.method == "POST":

        member.delete()

        messages.success(
            request,
            "Mwanachama amefutwa.",
        )

        return redirect("members_list")

    return render(
        request,
        "members/delete_member.html",
        {
            "member": member,
        },
    )
