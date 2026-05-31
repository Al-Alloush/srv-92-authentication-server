<#import "template.ftl" as layout>
<@layout.registrationLayout displayMessage=false; section>

<#if section = "header">
  <div class="kc-illus">
    <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
      <circle cx="36" cy="36" r="32" fill="#FFF1F1" stroke="#E5484D" stroke-width="2"/>
      <path d="M36 22v18" stroke="#E5484D" stroke-width="4" stroke-linecap="round"/>
      <circle cx="36" cy="50" r="2.5" fill="#E5484D"/>
    </svg>
  </div>
  <h1 class="kc-title">${msg("errorTitle")!"Something went wrong"}</h1>
  <p class="kc-subtitle">${kcSanitize(message.summary)?no_esc}</p>

<#elseif section = "form">
  <#if skipLink??>
  <#else>
    <#if client?? && client.baseUrl?has_content>
      <a class="kc-btn kc-btn--primary" href="${client.baseUrl}" style="text-decoration:none;">${kcSanitize(msg("backToApplication"))?no_esc}</a>
    </#if>
    <a class="kc-btn kc-btn--ghost" href="${url.loginUrl}" style="text-decoration:none;">${msg("backToLogin")}</a>
  </#if>
</#if>

</@layout.registrationLayout>
