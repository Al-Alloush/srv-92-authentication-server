<#import "template.ftl" as layout>
<@layout.emailLayout>
<#if firstName?? && lastName??>
    ${kcSanitize(msg("orgInviteBodyPersonalizedHtml", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", organization.name, linkExpirationFormatter(linkExpiration), firstName, lastName))?no_esc}
<#else>
    ${kcSanitize(msg("orgInviteBodyHtml", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", organization.name, linkExpirationFormatter(linkExpiration)))?no_esc}
</#if>
</@layout.emailLayout>
