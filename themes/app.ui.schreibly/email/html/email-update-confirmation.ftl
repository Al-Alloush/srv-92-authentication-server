<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("emailUpdateConfirmationBodyHtml", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), newEmail, "Schreibly", linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
