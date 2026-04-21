<#import "template.ftl" as layout>
<@layout.emailLayout>
${msg("emailTestBodyHtml")?no_esc}
</@layout.emailLayout>
