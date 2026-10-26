# Backend progress

P000 umumiy boshqaruv qoidasi qo‘llanadi. Har bir amaliy prompt uchun holat:

- `not_started`: hali boshlanmagan.
- `implemented_unverified`: o‘zgarish bajarilgan, qabul mezoni tekshirilmagan.
- `verified`: qabul mezonlari dalil bilan tekshirilgan.
- `blocked`: aniq tashqi yoki dependency blocker bor; sabab yoziladi.

Hujjat-only promptlarda sun’iy test talab qilinmaydi. Holat faqat shu promptning qabul mezoniga ko‘ra belgilanadi. Keyingi prompt faqat oldingi prompt verified bo‘lgach tavsiya etiladi.

## Joriy holat

- Amaldagi prompt: P012
- Holati: verified
- Dalil: P011 seed tekshiruvi saqlangan. `GET /api/v1/courses/` va `GET /api/v1/courses/{id}/` explicit serializer maydonlari va `IsAuthenticated` bilan qo‘shildi; pupil faqat faol enrollment/membership kurslarini, teacher esa bugungi faol assignment kurslarini ko‘radi. Anonymous, boshqa sinf detail, sessiya bilan o‘qish va profil/password maydonlari chiqmasligi tekshirildi. OpenAPI schema validate’dan ogohlantirishsiz o‘tdi; 43 pytest testi, Django system check va migration drift tekshiruvi o‘tdi. SQLite’da tekshirildi.
- Keyingi tavsiya: P013
- Ochiq blocker: PostgreSQL’da alohida constraint/concurrency tekshiruvi bajarilmadi; foydalanuvchi ko‘rsatgan joriy muhit SQLite.

## Promptlar

| ID | Holat | Dalil / blocker |
|---|---|---|
| P001 | verified | Backend scope/progress hujjatlari yaratildi va ko‘rib chiqildi. |
| P002 | verified | `.env.example`, sozlanadigan settings, README, dependency pins/lock va `.gitignore` yangilandi; `manage.py check` o‘tdi. Migrate qilmadik: custom User P003da keladi. |
| P003 | verified | `accounts.User` `AbstractUser`dan meros oldi; initial migrationda role CHECK bor. Username inherited unique. In-memory test `create_user()` parolni hash qilishini tasdiqladi. |
| P004 | verified | `.env`dagi PostgreSQL ulanishi bilan `lms_db`ga ulandi; Django system check va barcha migrationlar o‘tdi; sintetik pupil yozuvi keyingi Django shell jarayonida saqlanib qoldi. |
| P005 | verified | `IsAuthenticated` global permission ostida GET/POST endpoint qo‘shildi; missing field va malformed JSON `400`, noto‘g‘ri method `405`. 8 test va production URL yo‘qligi `DEBUG=0`, flag yoqilgan holatda tekshirildi. |
| P006 | verified | Pytest, pytest-django fixture va 3 APIClient testi qo‘shildi. Schema/docs yo‘llari `DEBUG=1` holatida mavjud; standart development sozlamasida Swagger `/` manzilida ochiladi. `docs/openapi.yaml` schema validation’dan o‘tdi. `drf-spectacular` va pytest vositalari dev requirement’lariga ajratildi. |
| P007 | verified | Foydalanuvchi so‘ragan SQLite muhitida sana CHECK, takror chorak tartibi va yil chegarasi validatsiyasi tekshirildi; umumiy testlar 19/19 o‘tdi. PostgreSQL’da tekshirilmagan. |
| P008 | verified | SQLite’da 1–11 sinf oralig‘i, sinf unikaligi, bir sinfda takror fan rad etilishi, 7-A va 7-B uchun bitta Subject ulanishi hamda PROTECT siyosati tekshirildi; umumiy testlar 24/24 o‘tdi. PostgreSQL’da tekshirilmagan. |
| P009 | verified | SQLite’da pupil teacher sifatida rad etildi; teacher almashishi eski yozuvni o‘chir-masdan avvalgi intervalni yopib, yangi assignment yaratdi. Sana, inactive teacher va archived course qoidalari tekshirildi; umumiy testlar 29/29 o‘tdi. PostgreSQL’da tekshirilmagan. |
| P010 | verified | SQLite’da teacher pupil sifatida rad etildi; faol sinf va pupil-course enrollment takrorlanishi DB’da rad etildi; sinf almashishi eski enrollmentlarni yopib saqladi; atomic rollback va backdate cheklovi tekshirildi. Jami testlar 36/36 o‘tdi. PostgreSQL’da alohida tekshirilmagan. |
| P011 | verified | Idempotent `seed_school` command bir yil, 4 chorak, 2 sinf, 2 teacher, 4 pupil, 4 fan, 8 course, 8 teaching assignment va ularning membership/enrollmentlarini yaratadi. Ikki marta ishga tushirish, parol hash’i va `DEBUG=0`da rad etish tekshirildi; README’da sintetik ma’lumot va password env yo‘riqnomasi bor. 38 pytest testi, system check va migration drift tekshiruvi o‘tdi. SQLite’da tekshirilgan. |
| P012 | verified | GET course list/detail read-only API qo‘shildi. Pupil faqat faol enrollment/membership kurslarini, teacher faqat bugungi faol assignment kurslarini oladi; archived course va boshqa roldagi user uchun ko‘rinish yo‘q. Anonymous request, list/detail scope, session auth va serializer allowlist test qilindi. `docs/openapi.yaml` validate’dan ogohlantirishsiz o‘tdi; jami 43 pytest testi. SQLite’da tekshirildi. |
| P013 | not_started | — |
| P014 | not_started | — |
| P015 | not_started | — |
| P016 | not_started | — |
| P017 | not_started | — |
| P018 | not_started | — |
| P019 | not_started | — |
| P020 | not_started | — |
| P021 | not_started | — |
| P022 | not_started | — |
| P023 | not_started | — |
| P023-A | not_started | — |
| P023-B | not_started | — |
| P023-C | not_started | — |
| P023-D | not_started | — |
| P023-E | not_started | — |
| P023-F | not_started | — |
| P024 | not_started | — |
| P025 | not_started | — |
| P026 | not_started | — |
| P027 | not_started | — |
| P028 | not_started | — |
| P029 | not_started | — |
| P030 | not_started | — |
| P031 | not_started | — |
| P032 | not_started | — |
| P033 | not_started | — |
| P034 | not_started | — |
| P035 | not_started | — |
| P036 | not_started | — |
| P037 | not_started | — |
| P038 | not_started | — |
| P039 | not_started | — |
| P040 | not_started | — |
| P041 | not_started | — |
| P042 | not_started | — |
| P043 | not_started | — |
| P044 | not_started | — |
| P045 | not_started | — |
| P046 | not_started | — |
| P047 | not_started | — |
| P048 | not_started | — |
| P049 | not_started | — |
| P050 | not_started | — |
| P051 | not_started | — |
| P052 | not_started | — |
| P053 | not_started | — |
| P054 | not_started | — |
| P055 | not_started | — |
| P056 | not_started | — |
| P057 | not_started | — |
| P058 | not_started | — |
| P059 | not_started | — |
| P060 | not_started | — |
| P061 | not_started | — |
| P062 | not_started | — |
| P063 | not_started | — |
| P064 | not_started | — |
| P065 | not_started | — |
| P066 | not_started | — |
| P067 | not_started | — |
| P068 | not_started | — |
| P069 | not_started | — |
| P070 | not_started | — |
| P071 | not_started | — |
| P072 | not_started | — |
| P073 | not_started | — |
| P074 | not_started | — |
| P075 | not_started | — |
| P076 | not_started | — |
| P077 | not_started | — |
| P078 | not_started | — |
| P079 | not_started | — |
| P080 | not_started | — |
| P081 | not_started | — |
| P081-A | not_started | — |
| P081-B | not_started | — |
| P082 | not_started | — |
| P083 | not_started | — |
| P084 | not_started | — |
| P085 | not_started | — |
| P086 | not_started | — |
| P087 | not_started | — |
| P088 | not_started | — |
| P089 | not_started | — |
| P090 | not_started | — |
