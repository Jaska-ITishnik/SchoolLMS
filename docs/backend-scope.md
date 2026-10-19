# Maktab LMS backend scope

## Maqsad va chegaralar

- Mahsulot bir maktabning o‘quv jarayonini boshqaradigan backend bo‘ladi.
- Biznes rollari faqat `pupil` va `teacher`. `manage_accounts` va `manage_academics` tanlangan teacherlarga beriladigan capability; Django superuser texnik boshqaruv vositasi.
- `is_staff` Django admin interfeysiga kirishni, `is_superuser` esa texnik Django ruxsatlarini anglatadi; ular biznes roli emas. Superuser pupil yoki teacher rolini kengaytirmaydi.
- Ushbu bosqichlarda backend va uning API shartnomasi quriladi. React, Vite, TypeScript, mobil ilova yoki UI yo‘q.
- Ish 15 mavzuli dars bo‘yicha, bir promptdan keyingisiga qabul mezonlari bajarilgach o‘tadi. To‘liq promptlar ro‘yxati `Maktab_LMS_plan.txt`da.
- Ommaviy signup, parent roli, multi-tenant, GraphQL, mikroservislar, Kubernetes, avtomatik jadval yechimi, video transcode, RAG/pupil AI chat va rejaning “keyinga qoldirilgan” bo‘limidagi imkoniyatlar ushbu scope’ga kirmaydi.

## Arxitektura va xavfsizlik tamoyillari

- Django modulli monolit: zarur bo‘lganda accounts, academics, learning, files, assignments, assessments, scheduling, communications, core va ai kabi app’lar ochiladi.
- Session authentication va CSRF himoyasi asosiy usul. JWT, CORS wildcard va public registration talab qilinmaydi.
- DRF global autentifikatsiyasi, queryset/list scope’i, obyekt ruxsati va yoziladigan parent FK validatsiyasi birga ishlaydi.
- Oddiy CRUD uchun DRF generic view/mixin yoki ViewSet; biznes workflow uchun tor action va service; agregatsiya uchun APIView/GenericAPIView ishlatiladi.
- Tarixni saqlash: nashr qilingan kontent/rubric va topshirilgan revision izsiz o‘zgarmaydi. Muhim DB workflow’lari transaction, kerakli concurrency nazorati va idempotency bilan bajariladi.
- Fayl private storage’da saqlanadi; clean scan bo‘lmaguncha yuklab olish yoki topshirishga berilmaydi. Baholar va javoblar DBda qoladi, Redis authoritative storage bo‘lmaydi.
- Sana-vaqt UTC aware; maktabning local time zone’i Asia/Tashkent; ballar Decimal. Testlar faqat sintetik ma’lumot ishlatadi. Secret, session, login body va pupil matni loglanmaydi.
- AI keyingi bosqichda cheklangan qoralama yaratish uchun ko‘riladi; teacher review/approve shart. Real provider tayyor bo‘lmasa natija mock deb belgilanadi va production AI o‘chiq qoladi.

## Tavsiya etiladigan tayanch stack

Reja bo‘yicha maqsadli tayanch: Python 3.12, Django 5.2 LTS liniyasi, unga mos Django REST Framework, PostgreSQL/psycopg, Docker Compose, pytest-django va drf-spectacular. Aniq paket versiyalari keyin, mavjud runtime va dependency lock tekshirilgach tanlanadi.

Repository auditi paytida `requirements.txt` Django 6.1.2 ni aniq ko‘rsatdi va DRF uchun 3.x diapazonini belgiladi; `root/settings.py` ham Django 6.1 hujjatlariga tayangan. P002da loyiha rejasining Django 5.2 LTS tanlovi qo‘llandi: rasmiy jadvalda uning security support muddati 2028-yil aprelgacha, Django 6.1niki esa 2027-yil dekabrgacha. DRF 3.18.3 rasmiy ravishda Django 5.2’ni qo‘llaydi. Aniq dependency lock `requirements.lock`da. Manbalar: https://www.djangoproject.com/download/ va https://www.django-rest-framework.org/community/release-notes/

## P001 repository auditi

- Repository bo‘sh emas: Django project `root/`, `manage.py`, `apps/`, `templates/`, `requirements.txt`, mavjud migrations package’i va `db.sqlite3` bor.
- `apps/models.py` hozircha Django model skeleti; akademik yoki LMS biznes modellari aniqlanmadi.
- `requirements.txt`da Django 6.1.2, DRF 3.x, drf-spectacular, Pillow va psycopg bor. Lockfile ko‘rinmadi.
- Repository yoki uning ota kataloglaridan `AGENTS.md` topilmadi.
- Ishchi daraxtda P001dan oldingi foydalanuvchi o‘zgarishlari bor: `Maktab_LMS_plan.txt` o‘zgartirilgan, `apps/__pycache__/` va `root/__pycache__/` untracked. Ular saqlanadi va P001da o‘zgartirilmagan.
- P001 faqat hujjat bosqichi: ilova, model, migratsiya, dependency yoki runtime o‘zgarishi qilinmadi.

## P002 kirish sharti

P001 hujjatlari ko‘rib chiqilgan. P002dan oldin mavjud project tuzilishi, Python/runtime, `requirements.txt`/lockfile, Django 6.1.2 baseline’i, Django 5.2 LTS reja maqsadi va maxfiy sozlamalarni xavfsiz boshqarish talablari aniqlashtiriladi. P002 dependencylarni muhitga mos ravishda tanlaydi; bu P001da paket o‘rnatish yoki versiyani almashtirishga ruxsat bermaydi.
