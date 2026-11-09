<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("passwordResetBodyHtml", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
