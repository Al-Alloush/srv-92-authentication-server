<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("identityProviderLinkBodyHtml", identityProviderAlias, realmName, identityProviderContext.username, link, linkExpiration, linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
