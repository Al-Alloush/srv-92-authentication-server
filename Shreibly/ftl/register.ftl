<#import "template.ftl" as layout>
<@layout.registrationLayout; section>

<#if section = "header">
  <h1 class="kc-title">${msg("registerTitle")!"Create your account"}</h1>
  <p class="kc-subtitle">${msg("registerSubtitle")!"Start writing with Schreibly — free for 14 days."}</p>

<#elseif section = "form">
  <form class="kc-form" id="kc-register-form" action="${url.registrationAction}" method="post">
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:14px;">
      <div class="kc-field">
        <label class="kc-label" for="firstName">${msg("firstName")}</label>
        <input class="kc-input <#if messagesPerField.existsError('firstName')>kc-input--invalid</#if>"
               id="firstName" name="firstName" type="text" value="${(register.formData.firstName!'')}" />
      </div>
      <div class="kc-field">
        <label class="kc-label" for="lastName">${msg("lastName")}</label>
        <input class="kc-input <#if messagesPerField.existsError('lastName')>kc-input--invalid</#if>"
               id="lastName" name="lastName" type="text" value="${(register.formData.lastName!'')}" />
      </div>
    </div>

    <div class="kc-field">
      <label class="kc-label" for="email">${msg("email")}</label>
      <input class="kc-input <#if messagesPerField.existsError('email')>kc-input--invalid</#if>"
             id="email" name="email" type="email" value="${(register.formData.email!'')}" autocomplete="email" />
    </div>

    <#if !realm.registrationEmailAsUsername>
      <div class="kc-field">
        <label class="kc-label" for="username">${msg("username")}</label>
        <input class="kc-input <#if messagesPerField.existsError('username')>kc-input--invalid</#if>"
               id="username" name="username" type="text" value="${(register.formData.username!'')}" autocomplete="username" />
      </div>
    </#if>

    <#if passwordRequired??>
      <div class="kc-field">
        <label class="kc-label" for="password">${msg("password")}</label>
        <div class="kc-pw">
          <input class="kc-input <#if messagesPerField.existsError('password','password-confirm')>kc-input--invalid</#if>"
                 id="password" name="password" type="password" autocomplete="new-password" />
          <button class="kc-pw-toggle" type="button" aria-label="${msg('showPassword')!'Show password'}"
                  onclick="(()=>{const i=document.getElementById('password');i.type=i.type==='password'?'text':'password'})()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          </button>
        </div>
      </div>

      <div class="kc-field">
        <label class="kc-label" for="password-confirm">${msg("passwordConfirm")}</label>
        <input class="kc-input <#if messagesPerField.existsError('password-confirm')>kc-input--invalid</#if>"
               id="password-confirm" name="password-confirm" type="password" autocomplete="new-password" />
      </div>
    </#if>

    <#if recaptchaRequired??>
      <div class="g-recaptcha" data-sitekey="${recaptchaSiteKey}"></div>
    </#if>

    <button class="kc-btn kc-btn--primary" type="submit">${msg("doRegister")}</button>
  </form>

<#elseif section = "info">
  <p class="kc-foot">${msg("alreadyHaveAccount")!"Already have an account?"} <a class="kc-link" href="${url.loginUrl}">${msg("doLogIn")}</a></p>
</#if>

</@layout.registrationLayout>
