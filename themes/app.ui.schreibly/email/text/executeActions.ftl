<#ftl output_format="plainText">
<#assign requiredActionsText><#if requiredActions??><#list requiredActions><#items as reqActionItem>${msg("requiredAction.${reqActionItem}")}<#sep>, </#items></#list><#else></#if></#assign>

${msg("executeActionsBody", link?replace("https://auth.codexo.dev/realms/", "https://schreibly.com/kc/realms/"), linkExpiration, "Schreibly", requiredActionsText, linkExpirationFormatter(linkExpiration))}
