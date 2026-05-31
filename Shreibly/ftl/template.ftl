<#-- Schreibly · base login template (template.ftl)
     Wraps every login/* page with the brand chrome. Imported via the
     `parent=base` chain in theme.properties so subpages keep Keycloak's
     standard <@layout.registrationLayout> macro shape. -->
<#macro registrationLayout displayMessage=true displayRequiredFields=false displayWide=false>
<!DOCTYPE html>
<html lang="${locale.currentLanguageTag!'en'}" dir="${locale.rtl?then('rtl','ltr')!'ltr'}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${msg("loginTitle",(realm.displayName!''))} · Schreibly</title>
  <link rel="icon" href="${url.resourcesPath}/img/icon.png">
  <#if properties.styles?has_content>
    <#list properties.styles?split(' ') as style>
      <link rel="stylesheet" href="${url.resourcesPath}/${style}">
    </#list>
  </#if>
  <#if scripts??>
    <#list scripts as script>
      <script src="${script}" type="text/javascript"></script>
    </#list>
  </#if>
</head>
<body>
  <#if realm.internationalizationEnabled && locale.supported?size gt 1>
    <div class="kc-lang">
      <select onchange="location.href=this.value" aria-label="${msg('languages')}">
        <#list locale.supported as l>
          <option value="${l.url}" <#if l.languageTag == locale.currentLanguageTag>selected</#if>>${l.label}</option>
        </#list>
      </select>
    </div>
  </#if>

  <main class="kc-page">
    <div>
      <section class="kc-card">
        <div class="kc-logo">
          <img src="${url.resourcesPath}/img/icon.png" alt="">
          <span class="kc-wordmark">Schreibly</span>
        </div>

        <#if displayMessage && message?has_content && (message.type != 'warning' || !isAppInitiatedAction??)>
          <div class="kc-alert kc-alert--${(message.type == 'error')?then('error', (message.type == 'success')?then('ok','info'))}">
            <#if message.summary?has_content>${kcSanitize(message.summary)?no_esc}</#if>
          </div>
        </#if>

        <#nested "header">
        <#nested "form">

        <#nested "info">
      </section>

      <div class="kc-brand-strip">
        AI Writing Assistant · <strong>English · German</strong>
      </div>
    </div>
  </main>
</body>
</html>
</#macro>
