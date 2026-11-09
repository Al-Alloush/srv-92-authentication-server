<#import "template.ftl" as layout>
<#assign appBase = link?contains("/realms/imeterreader/")?then("https://imeterreader.app/kc/", "https://dev.imeterreader.app/kc/")>
<#assign appLink = link?replace("https://auth.codexo.dev/", appBase)>
<@layout.emailLayout>
${msg("passwordResetBodyHtml", appLink, linkExpiration, realmName, linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
