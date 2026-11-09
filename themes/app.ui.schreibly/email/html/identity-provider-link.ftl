<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("identityProviderLinkBodyHtml", identityProviderAlias, "Schreibly", identityProviderContext.username, link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
