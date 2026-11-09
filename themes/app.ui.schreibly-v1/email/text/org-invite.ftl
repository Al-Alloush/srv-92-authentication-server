<#ftl output_format="plainText">

<#if firstName?? && lastName??>
    ${kcSanitize(msg("orgInviteBodyPersonalized", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", organization.name, linkExpirationFormatter(linkExpiration), firstName, lastName))}
<#else>
    ${kcSanitize(msg("orgInviteBody", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", organization.name, linkExpirationFormatter(linkExpiration)))}
</#if>
