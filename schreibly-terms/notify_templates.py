#!/usr/bin/env python3
"""The policy-change notice, in the three languages the gate exists in.

The legal framing is the same as the gate's and must stay that way:
the Terms of Service are ACCEPTED (a contract, and the reader must be told they
can leave instead), the Privacy Policy is ACKNOWLEDGED (a notice about processing
under Art. 6(1)(b) GDPR). Nothing here may be reworded as consent.

The "what changed" paragraph cannot be generated -- only the person making the
change knows it. Put it in notify-changes/<lang>.txt. Without it the notice still
renders, marked, but `notify --send` refuses to go out.
"""
import pathlib
from email.message import EmailMessage

CHANGES_DIR = pathlib.Path(__file__).resolve().parent / "notify-changes"

PLACEHOLDER = {
    "en": "[WHAT CHANGED — write this into notify-changes/en.txt before sending]",
    "de": "[WAS SICH GEÄNDERT HAT — vor dem Versand in notify-changes/de.txt eintragen]",
    "ar": "[ما الذي تغيّر — اكتبه في notify-changes/ar.txt قبل الإرسال]",
}

SUBJECT = {
    "en": "Schreibly — updated Terms of Service and Privacy Policy, effective {effective}",
    "de": "Schreibly — aktualisierte Nutzungsbedingungen und Datenschutzerklärung, gültig ab {effective}",
    "ar": "Schreibly — تحديث شروط الخدمة وسياسة الخصوصية، اعتباراً من {effective}",
}

BODY = {
    "en": """Hello,

We are updating the documents that govern your Schreibly account.

  Terms of Service  (version {terms_version})
  {terms_url}

  Privacy Policy    (version {privacy_version})
  {privacy_url}

They apply from {effective}. Until that date the versions you have already
accepted remain in force.

What changed
{changes}

What this means for you

  - The next time you sign in on or after {effective}, you will be asked to
    accept the new Terms of Service and to confirm that you have read the new
    Privacy Policy. Schreibly cannot be used without that.

  - You do not have to accept. If you do not want the new Terms, you can stop
    using Schreibly and delete your account before {effective}.

The Privacy Policy is information about how we process your data, not something
you consent to: we process the text you send in order to provide the service you
asked for. That part has not changed — the text you write is sent to Schreibly to
be checked, is processed only in memory, and is never used to train our models.

Please read both documents before {effective}.

Schreibly
""",
    "de": """Guten Tag,

wir aktualisieren die Dokumente, die für Ihr Schreibly-Konto gelten.

  Nutzungsbedingungen  (Version {terms_version})
  {terms_url}

  Datenschutzerklärung (Version {privacy_version})
  {privacy_url}

Sie gelten ab dem {effective}. Bis dahin bleiben die von Ihnen bereits
akzeptierten Fassungen in Kraft.

Was sich geändert hat
{changes}

Was das für Sie bedeutet

  - Wenn Sie sich ab dem {effective} das nächste Mal anmelden, werden Sie
    gebeten, die neuen Nutzungsbedingungen zu akzeptieren und zu bestätigen,
    dass Sie die neue Datenschutzerklärung gelesen haben. Ohne dies kann
    Schreibly nicht genutzt werden.

  - Sie müssen nicht zustimmen. Wenn Sie die neuen Nutzungsbedingungen nicht
    akzeptieren möchten, können Sie die Nutzung von Schreibly beenden und Ihr
    Konto vor dem {effective} löschen.

Die Datenschutzerklärung ist eine Information darüber, wie wir Ihre Daten
verarbeiten, und keine Einwilligung: Wir verarbeiten den von Ihnen gesendeten
Text, um die von Ihnen gewünschte Leistung zu erbringen. Daran hat sich nichts
geändert — der von Ihnen geschriebene Text wird zur Prüfung an Schreibly
übermittelt, nur im Arbeitsspeicher verarbeitet und niemals zum Training unserer
Modelle verwendet.

Bitte lesen Sie beide Dokumente vor dem {effective}.

Schreibly
""",
    "ar": """مرحباً،

نقوم بتحديث المستندات التي تحكم حسابك في Schreibly.

  شروط الخدمة  (الإصدار {terms_version})
  {terms_url}

  سياسة الخصوصية  (الإصدار {privacy_version})
  {privacy_url}

تسري اعتباراً من {effective}. وحتى ذلك التاريخ تبقى النسخ التي وافقت عليها سارية.

ما الذي تغيّر
{changes}

ماذا يعني هذا لك

  - عند تسجيل الدخول في {effective} أو بعده، سيُطلب منك قبول شروط الخدمة الجديدة
    وتأكيد أنك قرأت سياسة الخصوصية الجديدة. لا يمكن استخدام Schreibly من دون ذلك.

  - لست مضطراً إلى القبول. إذا لم ترغب في الشروط الجديدة، يمكنك التوقف عن استخدام
    Schreibly وحذف حسابك قبل {effective}.

سياسة الخصوصية هي إعلام بكيفية معالجتنا لبياناتك، وليست موافقة تُمنح: نحن نعالج
النص الذي ترسله لتقديم الخدمة التي طلبتها. وهذا لم يتغيّر — النص الذي تكتبه
يُرسَل إلى Schreibly للتدقيق، ويُعالَج في الذاكرة فقط، ولا يُستخدم إطلاقاً لتدريب
نماذجنا.

يرجى قراءة المستندين قبل {effective}.

Schreibly
""",
}


def changes_text(locale):
    path = CHANGES_DIR / f"{locale}.txt"
    if path.is_file() and path.read_text(encoding="utf-8").strip():
        return path.read_text(encoding="utf-8").strip(), True
    return PLACEHOLDER[locale], False


def all_changes_present(locales):
    return all(changes_text(locale)[1] for locale in locales)


def render(locale, cfg, effective, user, sender, sender_name):
    locale = locale if locale in BODY else "en"
    changes, _ = changes_text(locale)
    fields = {
        "effective": effective,
        "terms_version": cfg["TERMS_VERSION"],
        "privacy_version": cfg["PRIVACY_VERSION"],
        "terms_url": cfg["TERMS_URL"],
        "privacy_url": cfg["PRIVACY_URL"],
        "changes": changes,
    }
    message = EmailMessage()
    message["Subject"] = SUBJECT[locale].format(**fields)
    message["From"] = f"{sender_name} <{sender}>"
    message["To"] = user["email"]
    message["Content-Language"] = locale
    message.set_content(BODY[locale].format(**fields))
    return message
