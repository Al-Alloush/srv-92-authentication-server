<#import "template.ftl" as layout>
<@layout.registrationLayout; section>

<#if section = "header">
  <h1 class="kc-title">${msg("loginOtpTitle")!"Two-step verification"}</h1>
  <p class="kc-subtitle">${msg("loginOtpSubtitle")!"Enter the 6-digit code from your authenticator app."}</p>

<#elseif section = "form">
  <form class="kc-form" id="kc-otp-login-form" action="${url.loginAction}" method="post">
    <#if otpLogin.userOtpCredentials?size gt 1>
      <div class="kc-field">
        <label class="kc-label">${msg("loginOtpDevice")!"Choose device"}</label>
        <#list otpLogin.userOtpCredentials as otpCredential>
          <label class="kc-check" style="margin:6px 0;">
            <input type="radio" name="selectedCredentialId" value="${otpCredential.id}"
                   <#if otpCredential.id == otpLogin.selectedCredentialId>checked</#if> />
            <span>${otpCredential.userLabel}</span>
          </label>
        </#list>
      </div>
    </#if>

    <div class="kc-field">
      <label class="kc-label" for="otp">${msg("loginOtpOneTime")!"One-time code"}</label>
      <input class="kc-input <#if messagesPerField.existsError('totp')>kc-input--invalid</#if>"
             id="otp" name="otp" type="text" inputmode="numeric" pattern="[0-9]*"
             autocomplete="one-time-code" autofocus
             style="text-align:center; letter-spacing:0.4em; font-size:22px; font-weight:700;" />
    </div>

    <button class="kc-btn kc-btn--primary" type="submit">${msg("doLogIn")}</button>
  </form>

<#elseif section = "info">
  <p class="kc-foot"><a class="kc-link" href="${url.loginUrl}">${msg("backToLogin")}</a></p>
</#if>

</@layout.registrationLayout>
