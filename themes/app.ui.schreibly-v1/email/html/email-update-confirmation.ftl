<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("emailUpdateConfirmationBodyHtml", link, linkExpiration, realmName, linkExpirationFormatter(linkExpiration))?no_esc}
</@layout.emailLayout>
