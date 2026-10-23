# Membership va enrollment qoidalari

- Faol `ClassMembership` pupilning asosiy sinfini bildiradi; pupil uchun bir vaqtda faqat bittasi bo‘lishi mumkin.
- `Enrollment` pupilning ayni sinfdagi, arxivlanmagan fan kurslariga kirishini bildiradi. Bitta pupil-kurs juftligida bir vaqtda faqat bitta faol enrollment bo‘ladi.
- Sanalar yopiq interval sifatida talqin qilinadi: almashish sanasidan oldingi kun eski membership va enrollmentlarning `end_date` qiymati bo‘ladi.
- Sinfga tayinlash service’i eski yozuvlarni o‘chirmaydi. Membership va shu sinfning faol kurslari enrollmentlari bitta transaction ichida yaratiladi.
- Orqaga sana bilan tuzatish qo‘llab-quvvatlanmaydi: yangi membership sanasi pupilning avvalgi membership boshlanish sanalarining eng oxirgisidan keyin bo‘lishi shart. Yopilgan davrlarni qayta yozish yoki murakkab tarixiy overlapni avtomatik tuzatish bu bosqich doirasiga kirmaydi.
