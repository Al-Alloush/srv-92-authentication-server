<#outputformat "plainText">
<#assign requiredActionsText><#if requiredActions??><#list requiredActions><#items as reqActionItem>${msg("requiredAction.${reqActionItem}")}<#sep>, </#sep></#items></#list></#if></#assign>
</#outputformat>

<#import "template.ftl" as layout>

<@layout.emailLayout>
  <div style="text-align:center; padding-bottom: 20px;">
    <img src="https://codexo.dev/wp-content/uploads/2025/06/cropped-codexo-logo-100x100.png" alt="iMeter Recorder" width="150" />
  </div>

  <p>${msg("executeActionsBodyHtml", link, linkExpiration, realmName, requiredActionsText, linkExpirationFormatter(linkExpiration))?no_esc}</p>
</@layout.emailLayout>