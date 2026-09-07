IWACHU IMSAMBARA - EXCEL MEMBER IMPORT

1. Install dependencies:
   pip install -r requirements.txt

2. Run migrations:
   python manage.py migrate

3. Start server:
   python manage.py runserver

4. Open:
   http://127.0.0.1:8000/members/

5. Click "Import Excel".

The importer accepts:
- JINA / JINA LA MWANACHAMA / NAME
- SIMU / NAMBA YA SIMU / PHONE
- KITONGOJI (optional)
- JINSIA (optional)

It can also read the existing IWACHU Excel format where the header is
on a later row, and it automatically searches worksheets for the name
and phone columns.

Phone numbers are normalized to +255XXXXXXXXX.
Existing phone numbers and duplicates inside the uploaded Excel are skipped.

A template is available at:
  /members/import/template/

IMPORTANT:
The original .env file is intentionally not included in this package.
Create .env from .env.example and enter your own TextBee credentials.
