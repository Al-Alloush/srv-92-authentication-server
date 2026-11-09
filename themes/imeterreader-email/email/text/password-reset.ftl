<#ftl output_format="plainText">
<#assign appBase = link?contains("/realms/imeterreader/")?then("https://imeterreader.app/kc/", "https://dev.imeterreader.app/kc/")>
<#assign appLink = link?replace("https://auth.codexo.dev/", appBase)>
${msg("passwordResetBody",appLink, linkExpiration, realmName, linkExpirationFormatter(linkExpiration))}