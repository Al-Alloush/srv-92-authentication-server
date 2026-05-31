<#import "template.ftl" as layout>
<@layout.registrationLayout; section>

<#if section = "header">
  <h1 class="kc-title">${msg("doLogIn")}</h1>
  <p class="kc-subtitle">${msg("loginAccountTitle")!"Sign in to continue writing."}</p>

<#elseif section = "form">
  <#if realm.password>
    <form class="kc-form" id="kc-form-login" onsubmit="login.disabled = true; return true;" action="${url.loginAction}" method="post">
      <div class="kc-field">
        <label class="kc-label" for="username">
          <#if !realm.loginWithEmailAllowed>${msg("username")}
          <#elseif !realm.registrationEmailAsUsername>${msg("usernameOrEmail")}
          <#else>${msg("email")}</#if>
        </label>
        <input class="kc-input <#if messagesPerField.existsError('username','password')>kc-input--invalid</#if>"
               id="username" name="username" type="text"
               value="${(login.username!'')}"
               autocomplete="username" autofocus
               aria-invalid="<#if messagesPerField.existsError('username','password')>true</#if>" />
      </div>

      <div class="kc-field">
        <label class="kc-label" for="password">${msg("password")}</label>
        <div class="kc-pw">
          <input class="kc-input <#if messagesPerField.existsError('username','password')>kc-input--invalid</#if>"
                 id="password" name="password" type="password"
                 autocomplete="current-password"
                 aria-invalid="<#if messagesPerField.existsError('username','password')>true</#if>" />
          <button class="kc-pw-toggle" type="button" aria-label="${msg('showPassword')!'Show password'}"
                  onclick="(()=>{const i=document.getElementById('password');i.type=i.type==='password'?'text':'password'})()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
      </div>

      <div class="kc-row">
        <#if realm.rememberMe && !usernameHidden??>
          <label class="kc-check">
            <input type="checkbox" id="rememberMe" name="rememberMe" <#if login.rememberMe??>checked</#if> />
            <span>${msg("rememberMe")}</span>
          </label>
        </#if>
        <#if realm.resetPasswordAllowed>
          <a class="kc-link" tabindex="5" href="${url.loginResetCredentialsUrl}">${msg("doForgotPassword")}</a>
        </#if>
      </div>

      <input type="hidden" id="id-hidden-input" name="credentialId" <#if auth.selectedCredential?has_content>value="${auth.selectedCredential}"</#if>/>
      <button class="kc-btn kc-btn--primary" name="login" id="kc-login" type="submit">${msg("doLogIn")}</button>
    </form>
  </#if>

  <#if realm.password && social.providers??>
    <div class="kc-divider">${msg("identity-provider-login-label")!"or continue with"}</div>
    <div class="kc-social">
      <#list social.providers as p>
        <a class="kc-btn kc-btn--ghost" href="${p.loginUrl}" id="social-${p.alias}">
          <#if p.iconClasses?has_content><i class="${properties.kcCommonLogoIdP!} ${p.iconClasses}"></i></#if>
          <span>${msg("continue-with")!"Continue with"} ${p.displayName!}</span>
        </a>
      </#list>
    </div>
  </#if>

<#elseif section = "info">
  <#if realm.password && realm.registrationAllowed && !registrationDisabled??>
    <p class="kc-foot">${msg("noAccount")} <a class="kc-link" href="${url.registrationUrl}">${msg("doRegister")}</a></p>
  </#if>
</#if>

</@layout.registrationLayout>
